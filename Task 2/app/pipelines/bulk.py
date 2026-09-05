"""Bulk processing pipeline with concurrency control, fault tolerance, and multi-format exports."""

import asyncio
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Protocol, Tuple

from pydantic import ValidationError
from app.config import DEFAULT_CONCURRENCY, OUTPUTS_DIR
from app.models import GenerationRequest, GenerationResponse
from app.services.generator import CopyGenerator


class BatchProvider(Protocol):
    """Protocol abstraction for bulk execution engines (local async or cloud batch API)."""

    async def process_csv(
        self,
        input_csv_path: Path,
        concurrency: int = DEFAULT_CONCURRENCY,
        output_dir: Optional[Path] = None,
    ) -> Tuple[int, int, int, str, str, float]:
        """Process a batch of products from CSV and write output files."""
        ...


class LocalAsyncBulkProcessor:
    """Processes bulk copywriting jobs locally using asynchronous worker pools with semaphore bounds."""

    def __init__(self, generator: Optional[CopyGenerator] = None):
        self.generator = generator or CopyGenerator()

    async def process_csv(
        self,
        input_csv_path: Path,
        concurrency: int = DEFAULT_CONCURRENCY,
        output_dir: Optional[Path] = None,
    ) -> Tuple[int, int, int, str, str, float]:
        """Read CSV, validate rows, execute generations asynchronously, and write output files.
        
        Args:
            input_csv_path: Path to the input CSV file.
            concurrency: Maximum number of concurrent tasks.
            output_dir: Directory where result JSON and CSV will be written.
            
        Returns:
            Tuple of (total_rows, successful_count, failed_count, csv_output_path, json_output_path, duration_seconds)
        """
        start_time = time.perf_counter()
        out_dir = output_dir or OUTPUTS_DIR
        out_dir.mkdir(parents=True, exist_ok=True)

        if not input_csv_path.exists():
            raise FileNotFoundError(f"Input file not found at: {input_csv_path}")

        # Step 1: Read and parse CSV rows
        raw_rows: List[Dict[str, Any]] = []
        with open(input_csv_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw_rows.append(row)

        total_rows = len(raw_rows)
        valid_tasks: List[Tuple[int, GenerationRequest]] = []
        failed_records: List[Dict[str, Any]] = []

        # Step 2: Validate each row using Pydantic
        for idx, row in enumerate(raw_rows, start=1):
            try:
                # Type conversions from string CSV fields
                temp_val = float(row.get("temperature", 0.7)) if row.get("temperature") else 0.7
                top_p_val = float(row.get("top_p", 0.9)) if row.get("top_p") else 0.9
                max_tokens = int(row.get("max_output_tokens", 500)) if row.get("max_output_tokens") else 500

                request = GenerationRequest(
                    product_name=row.get("product_name", ""),
                    product_description=row.get("product_description", ""),
                    platform=row.get("platform", ""),
                    tone=row.get("tone", ""),
                    temperature=temp_val,
                    top_p=top_p_val,
                    max_output_tokens=max_tokens,
                )
                valid_tasks.append((idx, request))
            except (ValidationError, ValueError, TypeError) as err:
                failed_records.append({
                    "row_index": idx,
                    "raw_data": row,
                    "error": str(err),
                })

        # Step 3: Process valid requests concurrently with Semaphore
        semaphore = asyncio.Semaphore(concurrency)
        successful_results: List[GenerationResponse] = []

        async def _worker(idx: int, req: GenerationRequest) -> None:
            async with semaphore:
                try:
                    response = await self.generator.generate_copy(req)
                    successful_results.append(response)
                except Exception as exc:
                    failed_records.append({
                        "row_index": idx,
                        "raw_data": req.model_dump(),
                        "error": str(exc),
                    })

        worker_tasks = [_worker(idx, req) for idx, req in valid_tasks]
        if worker_tasks:
            await asyncio.gather(*worker_tasks)

        # Step 4: Export artifacts (JSON & CSV)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        json_filename = f"bulk_results_{timestamp}.json"
        csv_filename = f"bulk_results_{timestamp}.csv"
        json_path = out_dir / json_filename
        csv_path = out_dir / csv_filename

        # Write JSON output
        results_data = [res.model_dump() for res in successful_results]
        with open(json_path, mode="w", encoding="utf-8") as jf:
            json.dump(results_data, jf, indent=2)

        # Write CSV output
        if successful_results:
            fieldnames = [
                "product_name",
                "platform",
                "tone",
                "temperature",
                "top_p",
                "character_count",
                "word_count",
                "model_used",
                "created_at",
                "generated_copy",
            ]
            with open(csv_path, mode="w", encoding="utf-8", newline="") as cf:
                writer = csv.DictWriter(cf, fieldnames=fieldnames)
                writer.writeheader()
                for res in successful_results:
                    data = res.model_dump()
                    data["platform"] = res.platform.value
                    data["tone"] = res.tone.value
                    writer.writerow({k: data.get(k, "") for k in fieldnames})
        else:
            csv_path.touch()

        # If any rows failed, save failed report
        if failed_records:
            failed_csv = out_dir / f"bulk_failed_{timestamp}.json"
            with open(failed_csv, mode="w", encoding="utf-8") as ff:
                json.dump(failed_records, ff, indent=2)

        duration = time.perf_counter() - start_time
        return (
            total_rows,
            len(successful_results),
            len(failed_records),
            str(csv_path),
            str(json_path),
            duration,
        )
