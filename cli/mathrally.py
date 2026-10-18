import os
import tempfile
import click
from exercises.mathrally.algorithm import RallyAlgorithm
from exercises.mathrally.mathrally import (
    OPERATORS,
    MIN_VALUE,
    MAX_VALUE,
    SEED,
    TEMPLATE_PATH,
    TEMPLATE_NAME,
)
from exercises.mathrally.template import RallyTemplate
from svg.svg_handler import render_svg_to_pdf


from pathlib import Path

@click.command()
@click.option("--output", default="test.svg", help="Output file name for the rally.")
@click.option(
    "--solution", default="test_res.svg", help="Output file name for the solution."
)
@click.option(
    "--template",
    default=None,
    help="Template filename or path (e.g. Rally1.svg, Rally2.svg, or a full path).",
)
@click.option(
    "--format",
    type=click.Choice(["svg", "pdf", "both"], case_sensitive=False),
    default="both",
    help="Output format: SVG, PDF, or both.",
)
def mathrally(output, solution, template, format):
    """Generate a math rally SVG."""
    if template is not None:
        template_file = Path(template)
        if not template_file.exists():
            candidate = Path(TEMPLATE_PATH) / template
            if candidate.exists():
                template_file = candidate
            else:
                candidate_svg = Path(TEMPLATE_PATH) / f"{template}.svg"
                if candidate_svg.exists():
                    template_file = candidate_svg
    else:
        template_file = Path(TEMPLATE_PATH) / TEMPLATE_NAME

    rally_template = RallyTemplate(template_file)
    algorithm = RallyAlgorithm(
        OPERATORS, MIN_VALUE, MAX_VALUE, rally_template.num_operators, SEED
    )
    algorithm.build_rally()

    temp_files = []

    try:
        pdf_output = output.replace(".svg", ".pdf")
        pdf_solution = solution.replace(".svg", ".pdf")

        if format in ["svg", "both"]:
            rally_template.create_new_rally(algorithm, output, solution)
            click.echo(f"Rally generated: {output}, Solution generated: {solution}")
        else:  # Temporary SVG files for PDF generation
            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".svg")
            temp_solution = tempfile.NamedTemporaryFile(delete=False, suffix=".svg")
            temp_files.extend([temp_output.name, temp_solution.name])
            rally_template.create_new_rally(algorithm, temp_output.name, temp_solution.name)
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


if __name__ == "__main__":
    mathrally()

