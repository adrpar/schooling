import os
import tempfile
from typing import Optional

import click

from exercises.zahlenmauer import (
    Difficulty,
    ZahlenmauerAlgorithm,
    ZahlenmauerTemplate,
)
from svg.svg_handler import render_svg_to_pdf


@click.command()
@click.option(
    "--output",
    default="zahlenmauer.svg",
    help="Output file name for the student sheet SVG.",
)
@click.option(
    "--solution",
    default="zahlenmauer_solution.svg",
    help="Output file name for the solution sheet SVG.",
)
@click.option(
    "--format",
    type=click.Choice(["svg", "pdf", "both"], case_sensitive=False),
    default="both",
    help="Output format: SVG, PDF, or both.",
)
@click.option(
    "--base-size",
    type=click.IntRange(min=3, max=10),
    default=4,
    help="Number of bricks at the bottom row (3 to 10).",
)
@click.option(
    "--difficulty",
    type=click.Choice(["easy", "medium", "hard"], case_sensitive=False),
    default="medium",
    help="Difficulty level: easy, medium, or hard.",
)
@click.option(
    "--max-value",
    type=int,
    default=None,
    help=(
        "Maximum value on the apex brick. "
        "Defaults to max(100, 2^(base_size-1) * 10) so larger pyramids work automatically."
    ),
)
@click.option(
    "--min-value",
    type=int,
    default=1,
    help="Minimum value for base bricks.",
)
@click.option(
    "--num-pyramids",
    type=int,
    default=6,
    help="Number of pyramids per sheet.",
)
@click.option(
    "--seed",
    type=int,
    default=None,
    help="Random seed for reproducible generation.",
)
def zahlenmauer(
    output: str,
    solution: str,
    format: str,
    base_size: int,
    difficulty: str,
    max_value: Optional[int],
    min_value: int,
    num_pyramids: int,
    seed: Optional[int],
):
    """Generate Zahlenmauer (Addition Pyramid) exercise sheets."""
    if max_value is None:
        max_value = max(100, (2 ** (base_size - 1)) * 10)
    diff_enum = Difficulty.from_string(difficulty)

    algorithm = ZahlenmauerAlgorithm(
        base_size=base_size,
        difficulty=diff_enum,
        min_value=min_value,
        max_value=max_value,
        num_pyramids=num_pyramids,
        rand_seed=seed,
    )
    algorithm.build()

    template = ZahlenmauerTemplate()
    temp_files: list[str] = []

    try:
        pdf_output = output.replace(".svg", ".pdf")
        pdf_solution = solution.replace(".svg", ".pdf")

        if format in ["svg", "both"]:
            template.create_sheets(algorithm, output, solution)
            click.echo(f"Zahlenmauer generated: {output}, Solution generated: {solution}")
        else:
            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".svg")
            temp_solution = tempfile.NamedTemporaryFile(delete=False, suffix=".svg")
            temp_files.extend([temp_output.name, temp_solution.name])
            template.create_sheets(algorithm, temp_output.name, temp_solution.name)
            output, solution = temp_output.name, temp_solution.name

        if format in ["pdf", "both"]:
            render_svg_to_pdf(output, pdf_output)
            render_svg_to_pdf(solution, pdf_solution)
            click.echo(f"PDFs generated: {pdf_output}, {pdf_solution}")
    finally:
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)


if __name__ == "__main__":
    zahlenmauer()
