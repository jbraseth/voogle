# Copyright (c) 2025-2026 Voogle Contributors
# All rights reserved.

"""CLI commands for BibleProject data import.

Provides commands to import BibleProject research data into Voogle.
"""

from __future__ import annotations

from pathlib import Path

import click

from voogle.bibleproject.importer import ImportResult, import_all_courses, import_course


@click.group()
def main() -> None:
    """BibleProject data import utilities."""
    pass


@main.command("import")
@click.option(
    "--source",
    "-s",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Source directory containing BibleProject research data",
)
@click.option(
    "--target",
    "-t",
    type=click.Path(file_okay=False, path_type=Path),
    required=True,
    help="Target directory for imported data",
)
@click.option(
    "--course",
    "-c",
    type=str,
    default=None,
    help="Import only a specific course (by slug)",
)
def import_cmd(source: Path, target: Path, course: str | None) -> None:
    """Import BibleProject research data into Voogle structure."""
    if course:
        result = import_course(course, source, target)
        _print_result(result)
    else:
        results = import_all_courses(source, target)
        if not results:
            click.echo("No courses found to import.")
            return

        success_count = sum(1 for r in results if r.success)
        click.echo(f"\nImported {success_count}/{len(results)} courses successfully.\n")

        for result in results:
            _print_result(result)


def _print_result(result: ImportResult) -> None:
    """Print import result details."""
    status = click.style("OK", fg="green") if result.success else click.style("FAILED", fg="red")
    click.echo(f"[{status}] {result.course_slug}")
    click.echo(f"  VTT files converted: {result.vtt_files_converted}")
    click.echo(f"  Slides copied: {result.slides_copied}")
    click.echo(f"  Assets copied: {result.assets_copied}")

    if result.errors:
        click.echo(click.style("  Errors:", fg="yellow"))
        for error in result.errors:
            click.echo(f"    - {error}")


@main.command("list")
@click.option(
    "--target",
    "-t",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    required=True,
    help="Target directory containing imported data",
)
def list_cmd(target: Path) -> None:
    """List imported courses."""
    if not target.exists():
        click.echo("Target directory does not exist.")
        return

    courses = []
    for item in sorted(target.iterdir()):
        if item.is_dir():
            # Check if it has adapter_config.json (our marker for imported courses)
            config_file = item / "adapter_config.json"
            if config_file.exists():
                courses.append(item.name)

    if not courses:
        click.echo("No imported courses found.")
        return

    click.echo(f"Found {len(courses)} imported course(s):\n")
    for course in courses:
        click.echo(f"  - {course}")


@main.command("import-channels")
@click.option(
    "--metadata",
    "-m",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Path to metadata directory (defaults to research repo location)",
)
def import_channels_cmd(metadata: Path | None) -> None:
    """Import BibleProject courses as Channels with Episodes in the database."""
    import asyncio

    from voogle.bibleproject.import_channels import import_bibleproject_data

    asyncio.run(import_bibleproject_data(metadata))
    click.echo("Import complete.")


@main.command("import-transcripts")
@click.option(
    "--transcripts-dir",
    "-t",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path("/home/hs-dev/projects/bibleproject-research/data/transcripts"),
    help="Directory containing VTT transcripts organized by course",
)
def import_transcripts_cmd(transcripts_dir: Path) -> None:
    """Import BibleProject VTT transcripts as CSV and link to episodes."""
    import asyncio

    from voogle.bibleproject.import_transcripts import import_all_transcripts

    result = asyncio.run(import_all_transcripts(transcripts_dir))
    click.echo(f"Imported {result.success_count} transcripts, {result.error_count} errors")


if __name__ == "__main__":
    main()
