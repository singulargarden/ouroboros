import base64
import os

import click

from ouroboros import blockchain as impl_blockchain

CWD = os.getcwd()


@click.group()
def blockchain():
    pass


@blockchain.command()
@click.option('--root', help='root PATH to use.')
@click.option('--payload', help='payload to use for your genesis')
def init(root=None, payload=None):
    path = root or CWD
    print(impl_blockchain.init(path, payload))


@blockchain.command()
def describe():
    pass


@blockchain.command()
@click.option('--root', help='root PATH to use.')
@click.option('--show-genesis/--hide-genesis', default=False, help='show the genesis block')
def list(root=None, show_genesis=False):
    path = root or CWD

    print("HASH;PAYLOAD(base64);PREVIOUS_HASH")
    for x in impl_blockchain.list(path, show_genesis=show_genesis):
        payload = str(base64.b64encode(x.payload), encoding='ascii')
        print(f'{x.hash};{payload};{x.previous_hash}')


@blockchain.command()
@click.option('--root', help='root PATH to use.')
@click.argument('payload')
def append(root=None, payload=None):
    assert payload is not None, "payload argument required"

    path = root or CWD
    hash_ = impl_blockchain.append(path, bytes(payload, encoding="utf-8"))
    print(hash_)


@blockchain.command()
@click.argument('previous_hash')
@click.argument('payload')
def add():
    pass


CLI = blockchain()

if __name__ == '__main__':
    blockchain()
