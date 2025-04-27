import os
import tempfile
import click
from mathrally.algorithm import RallyAlgorithm
from mathrally.mathrally import (
    OPERATORS,
    MIN_VALUE,
    MAX_VALUE,
    SEED,
    TEMPLATE_PATH,
    TEMPLATE_NAME,
)
from mathrally.template import RallyTemplate
from svg.svg_handler import render_svg_to_pdf


@click.command()
@click.option("--output", default="test.svg", help="Output file name for the rally.")
@click.option(
    "--solution", default="test_res.svg", help="Output file name for the solution."
)
@click.option(
    "--format",
    type=click.Choice(["svg", "pdf", "both"], case_sensitive=False),
    default="both",
    help="Output format: SVG, PDF, or both.",
)
def mathrally(output, solution, format):
    """Generate a math rally SVG."""
    template = RallyTemplate("{}/{}".format(TEMPLATE_PATH, TEMPLATE_NAME))
    algorithm = RallyAlgorithm(
        OPERATORS, MIN_VALUE, MAX_VALUE, template.num_operators, SEED
    )
    algorithm.build_rally()

    temp_files = []

    try:
        pdf_output = output.replace(".svg", ".pdf")
        pdf_solution = solution.replace(".svg", ".pdf")

        if format in ["svg", "both"]:
            template.create_new_rally(algorithm, output, solution)
            click.echo(f"Rally generated: {output}, Solution generated: {solution}")
        else:  # Temporary SVG files for PDF generation
            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".svg")
            temp_solution = tempfile.NamedTemporaryFile(delete=False, suffix=".svg")
            temp_files.extend([temp_output.name, temp_solution.name])
            template.create_new_rally(algorithm, temp_output.name, temp_solution.name)
            output, solution = temp_output.name, temp_solution.name

        if format in ["pdf", "both"]:
            render_svg_to_pdf(output, pdf_output)
            render_svg_to_pdf(solution, pdf_solution)
            click.echo(
                f"PDFs generated: {output.replace('.svg', '.pdf')}, {solution.replace('.svg', '.pdf')}"
            )
    finally:
        # Clean up temporary files if they were created
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
