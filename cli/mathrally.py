import os
import tempfile
from pathlib import Path
from typing import Optional

import click

from core.operators import Operator
from exercises.mathrally.algorithm import RallyAlgorithm
from exercises.mathrally.mathrally import TEMPLATE_PATH, TEMPLATE_NAME
from exercises.mathrally.template import RallyTemplate
from svg.svg_handler import render_svg_to_pdf

# Operator name → Operator enum mapping for the --operators option
_OPERATOR_MAP = {
    "+": Operator.ADDITION,
    "-": Operator.SUBTRACTION,
    "*": Operator.MULTIPLICATION,
    "/": Operator.DIVISION,
}


def _parse_operators(operators_str: str) -> list[Operator]:
    """Convert a compact operator string like '+-' or '+*/' to a list of Operator enums."""
    result = []
    for ch in operators_str:
        if ch not in _OPERATOR_MAP:
            raise click.BadParameter(
                f"Unknown operator '{ch}'. Use any combination of: + - * /"
            )
        op = _OPERATOR_MAP[ch]
        if op not in result:
            result.append(op)
    if not result:
        raise click.BadParameter("At least one operator is required.")
    return result


@click.command()
@click.option(
    "--output", default="rally.svg", show_default=True,
    help="Output file name for the student sheet SVG.",
)
@click.option(
    "--solution", default="rally_solution.svg", show_default=True,
    help="Output file name for the solution sheet SVG.",
)
@click.option(
    "--template", default=None,
    help=(
        "Template filename or path (e.g. Rally1.svg, Rally2.svg, or a full path). "
        f"Defaults to {TEMPLATE_NAME} from the img/ directory."
    ),
)
@click.option(
    "--format",
    type=click.Choice(["svg", "pdf", "both"], case_sensitive=False),
    default="both", show_default=True,
    help="Output format: SVG, PDF, or both.",
)
@click.option(
    "--min-value",
    type=int, default=1, show_default=True,
    help="Minimum intermediate value in the rally chain.",
)
@click.option(
    "--max-value",
    type=int, default=100, show_default=True,
    help="Maximum intermediate value in the rally chain.",
)
@click.option(
    "--operators",
    default="+-*/", show_default=True,
    help=(
        "Operators to use, as a string of symbols. "
        "Use any combination of: + - * /  (e.g. '+-', '+*/', '+-*/')."
    ),
)
@click.option(
    "--seed",
    type=int, default=None,
    help="Random seed for reproducible output. Omit for a random sheet each time.",
)
def mathrally(
    output: str,
    solution: str,
    template: Optional[str],
    format: str,
    min_value: int,
    max_value: int,
    operators: str,
    seed: Optional[int],
) -> None:

    """Generate a Math Rally (Rechenrally) chain-calculation exercise sheet."""
    if min_value >= max_value:
        raise click.BadParameter(
            f"--min-value ({min_value}) must be less than --max-value ({max_value})."
        )

    operator_list = _parse_operators(operators)

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
                    raise click.BadParameter(
                        f"Template file not found: '{template}'. "
                        f"Looked in current directory and {TEMPLATE_PATH}/."
                    )
    else:
        template_file = Path(TEMPLATE_PATH) / TEMPLATE_NAME

    rally_template = RallyTemplate(template_file)
    algorithm = RallyAlgorithm(
        operator_list, min_value, max_value, rally_template.num_operators, seed
    )
    algorithm.build_rally()

    temp_files: list[str] = []
    try:
        pdf_output = output.replace(".svg", ".pdf")
        pdf_solution = solution.replace(".svg", ".pdf")

        if format in ["svg", "both"]:
            rally_template.create_new_rally(algorithm, output, solution)
            click.echo(f"Rally generated: {output}, Solution generated: {solution}")
        else:
            tmp_out = tempfile.NamedTemporaryFile(delete=False, suffix=".svg")
            tmp_sol = tempfile.NamedTemporaryFile(delete=False, suffix=".svg")
            temp_files.extend([tmp_out.name, tmp_sol.name])
            rally_template.create_new_rally(algorithm, tmp_out.name, tmp_sol.name)
            output, solution = tmp_out.name, tmp_sol.name

        if format in ["pdf", "both"]:
            render_svg_to_pdf(output, pdf_output)
            render_svg_to_pdf(solution, pdf_solution)
            click.echo(f"PDFs generated: {pdf_output}, {pdf_solution}")
    finally:
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)


if __name__ == "__main__":
    mathrally()
