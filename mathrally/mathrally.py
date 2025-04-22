from copy import deepcopy
from enum import Enum
from random import seed, randrange, choice
from mathrally.algorithm import Operator
from svg.svg_handler import SVGFile  # Import the SVGFile class from the new module

import lxml.etree as ET


TEMPLATE_PATH = "./img"
TEMPLATE_NAME = "Rally1.svg"


OPERATORS = [
    Operator.ADDITION,
    Operator.SUBTRACTION,
    Operator.MULTIPLICATION,
    Operator.DIVISION,
]
MIN_VALUE = 1
MAX_VALUE = 100
SEED = 7875
