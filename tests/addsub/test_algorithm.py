import pytest
from exercises.addsub.algorithm import AddSubAlgorithm
from core.operators import Operator


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


def test_build_addsub_subtraction():
    algorithm = AddSubAlgorithm(
        operator_list=[Operator.SUBTRACTION],
        min_value=1,
        max_value=100,
        num_exercises=10,
        num_rows_per_exercise=3,
        rand_seed=42,
    )
    algorithm.build_addsub()
    assert len(algorithm.result) == 10
    for operator, values in algorithm.result:
        assert operator == Operator.SUBTRACTION
        # Subtraction: first value is the largest and subtraction result is >= 0
        assert values[0] >= max(values[1:])
        assert values[0] - sum(values[1:]) >= 0


def test_addsub_rng_isolation():
    import random
    random.seed(888)
    val_before = random.random()
    random.seed(888)

    algorithm = AddSubAlgorithm(
        operator_list=[Operator.ADDITION, Operator.SUBTRACTION],
        min_value=1,
        max_value=100,
        num_exercises=5,
        num_rows_per_exercise=2,
        rand_seed=42,
    )
    algorithm.build_addsub()

    val_after = random.random()
    assert val_before == val_after
