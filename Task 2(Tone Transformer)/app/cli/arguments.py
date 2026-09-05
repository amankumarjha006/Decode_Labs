"""Argparse configuration for the copywriting command-line interface."""

import argparse
from app.config import (
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DEFAULT_MAX_OUTPUT_TOKENS,
    DEFAULT_CONCURRENCY,
)
from app.models import Platform, Tone


def build_parser() -> argparse.ArgumentParser:
    """Construct and configure the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="copywriter",
        description="Automated Copywriting & Tone Transformer: Generate high-impact, platform-optimized marketing copy.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python run.py interactive\n"
            "  python run.py generate --product-name 'EcoBottle' --description 'Reusable bottle' --platform instagram --tone witty\n"
            "  python run.py bulk --input data/sample_products.csv --concurrency 5\n"
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        description="Select an execution mode:",
        required=True,
    )

    # Subcommand: generate
    gen_parser = subparsers.add_parser(
        "generate",
        help="Generate marketing copy for a single product.",
        description="Generate tailored marketing copy for a single product given platform and tone specifications.",
    )
    gen_parser.add_argument(
        "--product-name",
        type=str,
        required=True,
        help="Name of the product or service.",
    )
    gen_parser.add_argument(
        "--description",
        type=str,
        required=True,
        help="Detailed description of features, benefits, and target audience.",
    )
    gen_parser.add_argument(
        "--platform",
        type=str,
        required=True,
        choices=[p.value for p in Platform],
        help="Target distribution platform (e.g. linkedin, instagram, email, twitter).",
    )
    gen_parser.add_argument(
        "--tone",
        type=str,
        required=True,
        choices=[t.value for t in Tone],
        help="Desired tone of voice (e.g. professional, witty, friendly, luxury, exciting, persuasive, casual).",
    )
    gen_parser.add_argument(
        "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
        help=f"Sampling temperature for creativity (0.0 to 2.0, default: {DEFAULT_TEMPERATURE}).",
    )
    gen_parser.add_argument(
        "--top-p",
        type=float,
        default=DEFAULT_TOP_P,
        help=f"Nucleus sampling probability threshold (0.0 to 1.0, default: {DEFAULT_TOP_P}).",
    )
    gen_parser.add_argument(
        "--max-output-tokens",
        type=int,
        default=DEFAULT_MAX_OUTPUT_TOKENS,
        help=f"Maximum output tokens to generate (50 to 2000, default: {DEFAULT_MAX_OUTPUT_TOKENS}).",
    )

    # Subcommand: bulk
    bulk_parser = subparsers.add_parser(
        "bulk",
        help="Process a batch of products from a CSV file.",
        description="Read a CSV file containing multiple products and process them asynchronously with concurrency bounds.",
    )
    bulk_parser.add_argument(
        "--input",
        "-i",
        type=str,
        default="data/sample_products.csv",
        help="Path to the input CSV file (default: data/sample_products.csv).",
    )
    bulk_parser.add_argument(
        "--concurrency",
        "-c",
        type=int,
        default=DEFAULT_CONCURRENCY,
        help=f"Maximum concurrent API requests (default: {DEFAULT_CONCURRENCY}).",
    )
    bulk_parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="outputs",
        help="Directory to save JSON and CSV generation outputs (default: outputs).",
    )

    # Subcommand: interactive
    subparsers.add_parser(
        "interactive",
        help="Launch an interactive guided session to generate copy.",
        description="Step-by-step interactive CLI prompt to input product parameters and generate marketing copy.",
    )

    return parser
