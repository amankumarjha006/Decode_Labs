"""Main entry point for Automated Copywriting & Tone Transformer CLI."""

import asyncio
import sys
from pathlib import Path
from pydantic import ValidationError

from app.cli.arguments import build_parser
from app.config import (
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DEFAULT_MAX_OUTPUT_TOKENS,
    DEFAULT_CONCURRENCY,
    validate_api_key,
    get_api_key_help,
)
from app.models import GenerationRequest, Platform, Tone
from app.pipelines.realtime import RealtimePipeline
from app.pipelines.bulk import LocalAsyncBulkProcessor
from app.services.llm_service import ApiKeyMissingError
from app.utils.display import (
    display_header,
    display_generation_result,
    display_error,
    display_bulk_summary,
    console,
)


async def handle_generate(args) -> int:
    """Execute single copy generation from command line arguments."""
    try:
        request = GenerationRequest(
            product_name=args.product_name,
            product_description=args.description,
            platform=args.platform,
            tone=args.tone,
            temperature=args.temperature,
            top_p=args.top_p,
            max_output_tokens=args.max_output_tokens,
        )
    except ValidationError as e:
        error_msgs = "\n".join(f"- {err['loc'][0]}: {err['msg']}" for err in e.errors())
        display_error(f"Input Validation Error:\n{error_msgs}", title="Invalid Request")
        return 1

    if not validate_api_key():
        display_error(get_api_key_help(), title="API Key Required")
        return 1

    with console.status("[bold green]Synthesizing marketing copy...[/bold green]", spinner="dots"):
        try:
            pipeline = RealtimePipeline()
            response = await pipeline.generate_single(request)
        except ApiKeyMissingError as e:
            display_error(str(e), title="API Configuration Error")
            return 1
        except Exception as e:
            display_error(f"Generation failed: {str(e)}", title="LLM Execution Error")
            return 1

    display_generation_result(response)
    return 0


async def handle_bulk(args) -> int:
    """Execute bulk batch copy generation from a CSV file."""
    input_path = Path(args.input)
    if not input_path.exists():
        display_error(f"Input file not found at: {input_path}", title="File Not Found")
        return 1

    if not validate_api_key():
        display_error(get_api_key_help(), title="API Key Required")
        return 1

    output_dir = Path(args.output_dir)
    console.print(f"[bold cyan]Starting bulk processing for:[/bold cyan] {input_path}")
    console.print(f"[dim]Concurrency Limit:[/dim] {args.concurrency}")

    try:
        processor = LocalAsyncBulkProcessor()
        with console.status("[bold green]Processing batch items asynchronously...[/bold green]", spinner="dots"):
            total, success, failed, csv_out, json_out, duration = await processor.process_csv(
                input_csv_path=input_path,
                concurrency=args.concurrency,
                output_dir=output_dir,
            )
        display_bulk_summary(total, success, failed, csv_out, json_out, duration)
        return 0 if failed == 0 else 1
    except ApiKeyMissingError as e:
        display_error(str(e), title="API Configuration Error")
        return 1
    except Exception as e:
        display_error(f"Bulk processing error: {str(e)}", title="Execution Error")
        return 1


async def handle_interactive() -> int:
    """Interactive wizard guiding user to specify parameters and generate copy."""
    display_header()
    console.print("[bold yellow]=== Guided Copywriting Studio ===[/bold yellow]\n")

    # Prompt Product Name
    product_name = console.input("[bold cyan]Enter Product Name:[/bold cyan] ").strip()
    while len(product_name) < 2:
        console.print("[red]Product name must be at least 2 characters.[/red]")
        product_name = console.input("[bold cyan]Enter Product Name:[/bold cyan] ").strip()

    # Prompt Product Description
    product_desc = console.input("\n[bold cyan]Enter Product Description:[/bold cyan] ").strip()
    while len(product_desc) < 10:
        console.print("[red]Product description must be at least 10 characters.[/red]")
        product_desc = console.input("[bold cyan]Enter Product Description:[/bold cyan] ").strip()

    # Select Platform
    platforms = [p.value for p in Platform]
    console.print(f"\n[bold cyan]Available Platforms:[/bold cyan] {', '.join(platforms)}")
    platform_input = console.input("[bold cyan]Choose Platform (default: linkedin):[/bold cyan] ").strip().lower() or "linkedin"
    while platform_input not in platforms:
        console.print(f"[red]Invalid platform. Choose from: {', '.join(platforms)}[/red]")
        platform_input = console.input("[bold cyan]Choose Platform:[/bold cyan] ").strip().lower()

    # Select Tone
    tones = [t.value for t in Tone]
    console.print(f"\n[bold cyan]Available Tones:[/bold cyan] {', '.join(tones)}")
    tone_input = console.input("[bold cyan]Choose Tone (default: professional):[/bold cyan] ").strip().lower() or "professional"
    while tone_input not in tones:
        console.print(f"[red]Invalid tone. Choose from: {', '.join(tones)}[/red]")
        tone_input = console.input("[bold cyan]Choose Tone:[/bold cyan] ").strip().lower()

    # Temperature
    temp_str = console.input(f"\n[bold cyan]Sampling Temperature (0.0 to 2.0, default: {DEFAULT_TEMPERATURE}):[/bold cyan] ").strip()
    temperature = float(temp_str) if temp_str else DEFAULT_TEMPERATURE

    # Top-P
    topp_str = console.input(f"[bold cyan]Top-P Nucleus Sampling (0.0 to 1.0, default: {DEFAULT_TOP_P}):[/bold cyan] ").strip()
    top_p = float(topp_str) if topp_str else DEFAULT_TOP_P

    # Max Tokens
    tokens_str = console.input(f"[bold cyan]Maximum Output Tokens (50 to 2000, default: {DEFAULT_MAX_OUTPUT_TOKENS}):[/bold cyan] ").strip()
    max_tokens = int(tokens_str) if tokens_str else DEFAULT_MAX_OUTPUT_TOKENS

    try:
        request = GenerationRequest(
            product_name=product_name,
            product_description=product_desc,
            platform=platform_input,
            tone=tone_input,
            temperature=temperature,
            top_p=top_p,
            max_output_tokens=max_tokens,
        )
    except ValidationError as e:
        error_msgs = "\n".join(f"- {err['loc'][0]}: {err['msg']}" for err in e.errors())
        display_error(f"Input Validation Error:\n{error_msgs}", title="Invalid Request")
        return 1

    if not validate_api_key():
        display_error(get_api_key_help(), title="API Key Required")
        return 1

    with console.status("[bold green]Crafting your marketing copy...[/bold green]", spinner="dots"):
        try:
            pipeline = RealtimePipeline()
            response = await pipeline.generate_single(request)
        except ApiKeyMissingError as e:
            display_error(str(e), title="API Configuration Error")
            return 1
        except Exception as e:
            display_error(f"Generation error: {str(e)}", title="Execution Error")
            return 1

    display_generation_result(response)
    return 0


def main() -> None:
    """Parse CLI arguments and dispatch to the corresponding pipeline handler."""
    parser = build_parser()
    
    # If run with no arguments, display help
    if len(sys.argv) == 1:
        display_header()
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    try:
        if args.command == "generate":
            exit_code = asyncio.run(handle_generate(args))
        elif args.command == "bulk":
            exit_code = asyncio.run(handle_bulk(args))
        elif args.command == "interactive":
            exit_code = asyncio.run(handle_interactive())
        else:
            parser.print_help()
            exit_code = 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        sys.exit(130)


if __name__ == "__main__":
    main()
