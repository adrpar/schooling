import click
from mathrally.mathrally import RallyTemplate, RallyAlgorithm, OPERATORS, MIN_VALUE, MAX_VALUE, SEED, TEMPLATE_PATH, TEMPLATE_NAME

@click.command()
@click.option('--output', default='test.svg', help='Output file name for the rally.')
@click.option('--solution', default='test_res.svg', help='Output file name for the solution.')
def mathrally(output, solution):
    """Generate a math rally SVG."""
    template = RallyTemplate("{}/{}".format(TEMPLATE_PATH, TEMPLATE_NAME))
    algorithm = RallyAlgorithm(
        OPERATORS, MIN_VALUE, MAX_VALUE, template.num_operators, SEED
    )
    algorithm.build_rally()
    template.create_new_rally(algorithm, output, solution)
    click.echo(f"Rally generated: {output}, Solution generated: {solution}")
