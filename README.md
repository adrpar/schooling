# Install

Requires uv:

```
pip install uv
```

`uv` will automaticall install required packages.


# Run

## Math Rally

Edit the following config section at the start of `mathrally.py`:

```
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
```

Comment out operators you don't want to have and the value range you want to cover in the exercise.

Then run:

```
uv run mathrally/mathrally.py
```

This will generate a svg output in `./test.svg`.

Open this file in Inkscape (works in Inkscape only) and print/convert to PDF.

## Written addition / subtraction


Edit the following config section at the start of `addsub.py`:

```
TEMPLATE_PATH = "./img"
TEMPLATE_NAME = "addsub1.svg"

OPERATORS = [
    Operator.ADDITION,
    Operator.SUBTRACTION,
    # Operator.MULTIPLICATION,
    # Operator.DIVISION,
]
MIN_VALUE = 1
MAX_VALUE = 999
SEED = 7874
NUM_EXERCISES = 30
NUM_ROWS_PER_EXERCISE = 2
```

Comment out operators you don't want to have and the value range you want to cover in the exercise.

Then run:

```
uv run mathrally/mathrally.py
```

This will generate a svg output in `./test.svg`.

Open this file in Inkscape (works in Inkscape only) and print/convert to PDF.
