import os
import tempfile
import click
from addSubWritten.addsub import (
    OPERATORS,
    MIN_VALUE,
    MAX_VALUE,
    NUM_EXERCISES,
    NUM_ROWS_PER_EXERCISE,
    SEED,
)
from addSubWritten.algorithm import AddSubAlgorithm
from addSubWritten.template import AddSubTemplate
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
def addsub(output, format):
    """Generate add/sub exercises SVG."""
    template = AddSubTemplate()
    algorithm = AddSubAlgorithm(
        OPERATORS, MIN_VALUE, MAX_VALUE, NUM_EXERCISES, NUM_ROWS_PER_EXERCISE, SEED
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
