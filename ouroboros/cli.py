import click


@click.command()
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--name', prompt='Your name',
              help='The person to greet.')
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for x in range(count):
        click.echo('Hello %s!' % name)


@click.group()
def blockchain():
    pass


@blockchain.command()
def init():
    pass


@blockchain.command()
def list():
    pass

@blockchain.command()
def describe():
    pass

@blockchain.command()
@click.argument('payload')
def append():
    pass


@blockchain.command()
@click.argument('previous_hash')
@click.argument('payload')
def add():
    pass


if __name__ == '__main__':
    hello()
