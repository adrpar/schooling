import pytest
from addSubWritten.algorithm import AddSubAlgorithm, Operator


def test_operator_enum():
    assert Operator.ADDITION.value == 1
    assert Operator.SUBTRACTION.value == 2
    assert Operator.MULTIPLICATION.value == 3
    assert Operator.DIVISION.value == 4


def test_addsubalgorithm_initialization():
    algorithm = AddSubAlgorithm(
        operator_list=[Operator.ADDITION, Operator.SUBTRACTION],
        min_value=1,
        max_value=10,
        num_exercises=5,
        num_rows_per_exercise=3,
        rand_seed=42,
    )
    assert algorithm.operations == [Operator.ADDITION, Operator.SUBTRACTION]
    assert algorithm.min_value == 1
    assert algorithm.max_value == 10
    assert algorithm.num_exercises == 5
    assert algorithm.num_rows_per_exercise == 3
    assert algorithm.seed == 42


def test_build_addsub():
    algorithm = AddSubAlgorithm(
        operator_list=[Operator.ADDITION],
        min_value=1,
        max_value=10,
        num_exercises=2,
        num_rows_per_exercise=2,
        rand_seed=42,
    )
    algorithm.build_addsub()
    assert len(algorithm.result) == 2
    for operator, values in algorithm.result:
        assert operator == Operator.ADDITION
        assert sum(values) <= algorithm.max_value
