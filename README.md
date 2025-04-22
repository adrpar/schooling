# Math Trainer

This is a CLI tool for generating math rally and add/sub exercises in SVG format.

## Installation

If you want to install this as a CLI tool that is commonly available, run:

```sh
pip install -e .
pip install uv
```

`uv` will automatically install required packages.

## Usage

### Math Rally

```sh
uv run math-trainer.py -- mathrally --output rally.svg --solution rally_solution.svg
```

### Add/Sub Exercises

```sh
uv run math-trainer.py -- addsub --output addsub.svg
```

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
uv run addSubWritten/addsub.py
```

This will generate a svg output in `./test.svg`.

Open this file in Inkscape (works in Inkscape only) and print/convert to PDF.

# Developer Guide

## Running Tests

To run the tests with pytest, use the following command:

```sh
pytest
```

Make sure you have pytest installed. You can install it using pip:

```sh
pip install pytest
```
