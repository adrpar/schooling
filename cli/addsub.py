import os
import tempfile
import click
from exercises.addsub.addsub import (
    OPERATORS,
    MIN_VALUE,
    MAX_VALUE,
    NUM_EXERCISES,
    NUM_ROWS_PER_EXERCISE,
    SEED,
)
from exercises.addsub.algorithm import AddSubAlgorithm
from exercises.addsub.template import AddSubTemplate
from svg.svg_handler import render_svg_to_pdf


@click.command()
@click.option(
    "--output", default="test.svg", help="Output file name for the add/sub exercises."
)
@click.option(
    "--format",
    type=click.Choice(["svg", "pdf", "both"], case_sensitive=False),
    default="both",
    help="Output format: SVG, PDF, or both.",
)
@click.option(
    "--num-exercises",
    type=int,
    default=20,
    help="Number of exercises per sheet (default: 20, cleanly fills A4 page).",
)
def addsub(output, format, num_exercises):
    """Generate add/sub exercises SVG."""
    template = AddSubTemplate()
    algorithm = AddSubAlgorithm(
        OPERATORS, MIN_VALUE, MAX_VALUE, num_exercises, NUM_ROWS_PER_EXERCISE, SEED
    )
    algorithm.build_addsub()

    temp_files = []

    try:
        pdf_output = output.replace(".svg", ".pdf")

        if format in ["svg", "both"]:
            template.create_new(algorithm, output)
            click.echo(f"Add/Sub exercises generated: {output}")
        else:  # Temporary SVG file for PDF generation
            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".svg")
            temp_files.append(temp_output.name)
            template.create_new(algorithm, temp_output.name)
            output = temp_output.name

        if format in ["pdf", "both"]:
            render_svg_to_pdf(output, pdf_output)
            click.echo(f"PDF generated: {pdf_output}")
    finally:
        # Clean up temporary files if they were created
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)


if __name__ == "__main__":
    addsub()

