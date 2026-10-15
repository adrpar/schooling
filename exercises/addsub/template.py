from pathlib import Path
from typing import Optional, Union

from exercises.utils import operator_to_string
from svg.canvas_template import CanvasExerciseTemplate
from svg.number_paper.written_calc_exercise_box import WrittenCalcExerciseBox

_TEMPLATE = Path(__file__).parent / "drawing.svg"


class AddSubTemplate(CanvasExerciseTemplate):
    """Template for generating AddSub written calculation exercise sheets."""

    VALUE_ID_PREFIX = "value"
    OPERATOR_TEXT_ID_PREFIX = "operatorText"

    def __init__(self, template_path: Optional[Union[str, Path]] = None):
        super().__init__(template_path or _TEMPLATE)
        # Retain backward-compatible properties
        self.svg = self.doc
        self.title_tspan_elements = self.title_tspans

    def create_new(
        self,
        algorithm,
        filename_addsub: Union[str, Path],
        show_numbering: bool = True,
    ) -> None:
        op_string = operator_to_string(algorithm.operations)
        self.set_header(
            "Schriftliche Mathe",
            f"Operators: {op_string} - Max Num: {algorithm.max_value} - Seed: {algorithm.seed}",
        )
        self.set_footer(visible=True)

        exercise_nodes = [
            WrittenCalcExerciseBox(
                operator,
                values,
                exercise_number=idx + 1 if show_numbering else None,
            ).generateBox()
            for idx, (operator, values) in enumerate(algorithm.result)
        ]

        self.distribute_exercises(exercise_nodes)
        self.write(filename_addsub)

    def _set_text(self, element, text: str) -> None:
        element[0].text = text
