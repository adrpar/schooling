from addSubWritten.algorithm import Operator
from svg.number_paper.written_calc_exercise_box import WrittenCalcExerciseBox
from svg.svg_groups import distribute_groups_in_drawing_area
from svg.svg_handler import SVGFile


class AddSubTemplate:
    VALUE_ID_PREFIX = "value"
    OPERATOR_TEXT_ID_PREFIX = "operatorText"
    TITLE_ID = "Title"

    TITLE_SPAN = "TitleSpan"
    CONFIG_SPAN = "ConfigSpan"

    def __init__(self):
        self.svg = SVGFile("addSubWritten/drawing.svg")

        text_elements = self.svg.find_all_elements_by_attributes("text", "id")

        self.title_element = text_elements[self.TITLE_ID]

        title_tspan_elements = self.svg.all_spans_in_text(self.title_element)
        self.title_tspan_elements = {
            element.attrib["id"]: element for element in title_tspan_elements
        }

        self.drawing_area_group = self.svg.find_all_elements_by_attributes(
            "g", "id"
        ).get("drawingArea")

        self.drawing_area = self.svg.find_all_elements_by_attributes_in_node(
            self.drawing_area_group, "rect", "id"
        ).get("drawingAreaRect")

    def create_new(self, algorithm, filename_addsub):
        operator_string = self._get_operator_string(algorithm.operations)
        self.title_tspan_elements[
            self.CONFIG_SPAN
        ].text = "Operators: {} - Max Num: {} - Seed: {}".format(
            operator_string, algorithm.max_value, algorithm.seed
        )

        exercises = []
        exercise_nodes = []
        for operator, values in algorithm.result:
            exercise = WrittenCalcExerciseBox(operator, values)  # Updated reference
            svg_node = exercise.generateBox()

            exercises.append(exercise)
            exercise_nodes.append(svg_node)

        distribute_groups_in_drawing_area(
            exercise_nodes,
            self.drawing_area,
            self.drawing_area_group,
        )

        self.svg.write(filename_addsub)

    def _set_text(self, element, text):
        element[0].text = text

    def _get_operator_string(self, operators):
        result = ""
        for operator in operators:
            if operator == Operator.ADDITION:
                result = result + "+"
            elif operator == Operator.SUBTRACTION:
                result = result + "-"
            elif operator == Operator.MULTIPLICATION:
                result = result + "*"
            elif operator == Operator.DIVISION:
                result = result + "/"
        return result
    