"""Rich terminal display utilities for copywriting output and progress."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from app.models import GenerationResponse, Platform

console = Console()


def display_header() -> None:
    """Print an attractive application banner."""
    title_text = Text("AUTOMATED COPYWRITING & TONE TRANSFORMER", style="bold cyan")
    subtitle_text = Text("AI-Powered Multi-Platform Marketing Copy Synthesis", style="italic white")
    combined = Text.assemble(title_text, "\n", subtitle_text)
    console.print(Panel(combined, border_style="bright_blue", expand=False))


def display_generation_result(response: GenerationResponse) -> None:
    """Display the generated copy and metadata in a structured Rich panel.
    
    Args:
        response: Completed GenerationResponse.
    """
    console.print()

    # Metadata table
    meta_table = Table(show_header=False, box=None, padding=(0, 2))
    meta_table.add_column("Field", style="bold bright_cyan")
    meta_table.add_column("Value", style="white")

    meta_table.add_row("Product:", f"[bold]{response.product_name}[/bold]")
    meta_table.add_row("Platform:", f"[magenta]{response.platform.value.upper()}[/magenta]")
    meta_table.add_row("Tone:", f"[green]{response.tone.value.capitalize()}[/green]")
    meta_table.add_row("Temperature:", f"[yellow]{response.temperature:.2f}[/yellow]")
    meta_table.add_row("Top-P:", f"[yellow]{response.top_p:.2f}[/yellow]")
    meta_table.add_row("Model Used:", f"[dim]{response.model_used}[/dim]")
    meta_table.add_row("Timestamp:", f"[dim]{response.created_at}[/dim]")

    console.print(Panel(meta_table, title="[bold]Generation Parameters[/bold]", border_style="cyan"))

    # Highlighted Copy Panel
    copy_style = "white"
    if response.platform == Platform.EMAIL:
        copy_title = "[bold green]Generated Marketing Email[/bold green]"
    elif response.platform == Platform.TWITTER:
        copy_title = "[bold deep_sky_blue1]Generated X / Twitter Post[/bold deep_sky_blue1]"
    elif response.platform == Platform.INSTAGRAM:
        copy_title = "[bold magenta]Generated Instagram Caption[/bold magenta]"
    else:
        copy_title = "[bold blue]Generated LinkedIn Post[/bold blue]"

    console.print(Panel(
        response.generated_copy,
        title=copy_title,
        border_style="bright_green",
        padding=(1, 2)
    ))

    # Stats Summary
    stats = Text()
    stats.append(f"Characters: {response.character_count}", style="bold cyan")
    stats.append("  |  ", style="dim")
    stats.append(f"Words: {response.word_count}", style="bold cyan")
    
    if response.platform == Platform.TWITTER:
        status = "[green]Within 280-char limit[/green]" if response.character_count <= 280 else "[red]Over 280-char limit[/red]"
        stats.append("  |  ", style="dim")
        stats.append(f"Twitter Constraint: {status}")

    console.print(Panel(stats, border_style="dim", expand=False))
    console.print()


def display_error(message: str, title: str = "Error") -> None:
    """Print an eye-catching error message without raw tracebacks."""
    console.print(Panel(f"[bold red]{message}[/bold red]", title=f"[bold red]{title}[/bold red]", border_style="red"))


def display_warning(message: str, title: str = "Warning") -> None:
    """Print an alert warning box."""
    console.print(Panel(f"[bold yellow]{message}[/bold yellow]", title=f"[bold yellow]{title}[/bold yellow]", border_style="yellow"))


def display_bulk_summary(
    total: int,
    successful: int,
    failed: int,
    csv_path: str,
    json_path: str,
    duration: float
) -> None:
    """Display summary metrics after executing a bulk processing batch."""
    table = Table(title="Bulk Processing Execution Summary", border_style="bright_blue")
    table.add_column("Metric", style="bold cyan")
    table.add_column("Value", style="white")

    table.add_row("Total Rows Evaluated", str(total))
    table.add_row("Successfully Generated", f"[green]{successful}[/green]")
    table.add_row("Failed / Invalid", f"[red]{failed}[/red]" if failed > 0 else "0")
    table.add_row("Execution Time", f"{duration:.2f} seconds")
    table.add_row("Output JSON", json_path)
    table.add_row("Output CSV", csv_path)

    console.print()
    console.print(table)
    console.print()
