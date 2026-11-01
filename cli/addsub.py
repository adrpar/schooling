import os
import tempfile
from typing import Optional

import click

from core.operators import Operator
from exercises.addsub.algorithm import AddSubAlgorithm
from exercises.addsub.template import AddSubTemplate
from svg.svg_handler import render_svg_to_pdf

# Operator name → Operator enum mapping for the --operators option
_OPERATOR_MAP = {
    "+": Operator.ADDITION,
    "-": Operator.SUBTRACTION,
    "*": Operator.MULTIPLICATION,
    "/": Operator.DIVISION,
}


def _parse_operators(operators_str: str) -> list[Operator]:
    """Convert a compact operator string like '+-' or '+*' to a list of Operator enums."""
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
    "--output", default="addsub.svg", show_default=True,
    help="Output file name for the student sheet SVG.",
)
@click.option(
    "--format",
    type=click.Choice(["svg", "pdf", "both"], case_sensitive=False),
    default="both", show_default=True,
    help="Output format: SVG, PDF, or both.",
)
@click.option(
    "--num-exercises",
    type=click.IntRange(min=1), default=20, show_default=True,
    help="Number of exercises per sheet.",
)
@click.option(
    "--num-rows",
    type=click.IntRange(min=2), default=2, show_default=True,
    help="Number of operand rows per exercise (2 = one addition/subtraction).",
)
@click.option(
    "--min-value",
    type=int, default=1, show_default=True,
    help="Minimum operand value.",
)
@click.option(
    "--max-value",
    type=int, default=9999, show_default=True,
    help="Maximum operand value (and maximum result for addition).",
)
@click.option(
    "--operators",
    default="+-", show_default=True,
    help=(
        "Operators to use, as a string of symbols. "
        "Use any combination of: + - * /  (e.g. '+-', '+*', '+-*/')."
    ),
)
@click.option(
    "--seed",
    type=int, default=None,
    help="Random seed for reproducible output. Omit for a random sheet each time.",
)
def addsub(
    output: str,
    format: str,
    num_exercises: int,
    num_rows: int,
    min_value: int,
    max_value: int,
    operators: str,
    seed: Optional[int],
):
    """Generate written addition/subtraction (Schriftliche Rechnung) exercise sheets."""
    if min_value >= max_value:
        raise click.BadParameter(
            f"--min-value ({min_value}) must be less than --max-value ({max_value})."
        )

    operator_list = _parse_operators(operators)

    template = AddSubTemplate()
    algorithm = AddSubAlgorithm(
        operator_list, min_value, max_value, num_exercises, num_rows, seed
    )
    algorithm.build_addsub()

    temp_files: list[str] = []
    try:
        pdf_output = output.replace(".svg", ".pdf")

        if format in ["svg", "both"]:
            template.create_new(algorithm, output)
            click.echo(f"Add/Sub exercises generated: {output}")
        else:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".svg")
            temp_files.append(tmp.name)
            template.create_new(algorithm, tmp.name)
            output = tmp.name

        if format in ["pdf", "both"]:
            render_svg_to_pdf(output, pdf_output)
            click.echo(f"PDF generated: {pdf_output}")
    finally:
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)


if __name__ == "__main__":
    addsub()
