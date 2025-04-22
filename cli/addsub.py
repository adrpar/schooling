import click
from addSubWritten.addsub import OPERATORS, MIN_VALUE, MAX_VALUE, NUM_EXERCISES, NUM_ROWS_PER_EXERCISE, SEED
from addSubWritten.algorithm import AddSubAlgorithm
from addSubWritten.template import AddSubTemplate

@click.command()
@click.option('--output', default='test.svg', help='Output file name for the add/sub exercises.')
def addsub(output):
    """Generate add/sub exercises SVG."""
    template = AddSubTemplate()
    algorithm = AddSubAlgorithm(
        OPERATORS, MIN_VALUE, MAX_VALUE, NUM_EXERCISES, NUM_ROWS_PER_EXERCISE, SEED
    )
    algorithm.build_addsub()
    template.create_new(algorithm, output)
    click.echo(f"Add/Sub exercises generated: {output}")
