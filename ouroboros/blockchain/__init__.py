import contextlib
import hashlib
import os
import time
from collections import namedtuple

from ouroboros.schemas import blockchain_pb2 as schema

Block = namedtuple('Block', ['hash', 'previous_hash', 'payload', 'bytes'])
Descr = namedtuple('Descr', ['genesis_hash', 'head_hash', 'bytes'])

ZERO_HASH = '0' * 96


def sha3(*args):
    m = hashlib.sha384()
    for x in args:
        m.update(x)

    return m.hexdigest()


def make_block(previous_hash, payload):
    hash_ = sha3(bytes(previous_hash, encoding="ascii"), payload)

    b = schema.Block()
    b.previous_hash = previous_hash
    b.payload = payload

    return Block(hash=hash_, previous_hash=previous_hash,
                 payload=payload, bytes=b.SerializeToString())


def make_descr(genesis_hash, head_hash):
    d = schema.BlockchainDescription()
    d.genesis_hash = genesis_hash
    d.head_hash = head_hash

    return Descr(genesis_hash=genesis_hash,
                 head_hash=head_hash,
                 bytes=d.SerializeToString())


class InvalidBlockchainException(Exception):
    pass


class BlockNotFoundException(Exception):
    pass


def path_descr(root_path):
    return os.path.join(root_path, 'blockchain.desc')


def path_block(root_path, hash):
    return os.path.join(root_path, f'{hash}.blck')


@contextlib.contextmanager
def descr_file(root_path, mode):
    try:
        descr = path_descr(root_path)
        with open(descr, mode) as f:
            yield f
    except FileNotFoundError as e:
        raise InvalidBlockchainException() from e


@contextlib.contextmanager
def block_file(root_path, hash_, mode):
    try:
        block = path_block(root_path, hash_)
        with open(block, mode) as f:
            yield f
    except FileNotFoundError as e:
        raise BlockNotFoundException() from e


def load_block(root_path, hash):
    with block_file(root_path, hash, 'rb') as f:
        b = schema.Block()
        b.ParseFromString(f.read())

        B = b.SerializeToString()
        return Block(hash=hash, previous_hash=b.previous_hash, payload=b.payload, bytes=B)


def init(path, genesis_payload=None):
    if genesis_payload is None:
        genesis_payload = bytes(str(time.time()), encoding="ascii")

    genesis_block = make_block(ZERO_HASH, genesis_payload)
    descr = make_descr(genesis_block.hash, genesis_block.hash)

    # TODO: assert no descr file, don't init twice.
    with descr_file(path, 'wb') as d, block_file(path, genesis_block.hash, 'wb') as b:
        b.write(genesis_block.bytes)
        d.write(descr.bytes)

    os.sync()
    return genesis_block.hash


def list(path):
    return []


def get_payload(root_path, hash):
    with descr_file(root_path, 'rb'):
        block = load_block(root_path, hash)
        return block.payload


def load_descr(root_path):
    with descr_file(root_path, 'rb') as f:
        d = schema.BlockchainDescription()
        d.ParseFromString(f.read())

        return Descr(genesis_hash=d.genesis_hash,
                     head_hash=d.head_hash,
                     bytes=d.SerializeToString())


def descr_with_head_hash(descr, head_hash):
    d = schema.BlockchainDescription()
    d.head_hash = head_hash
    d.genesis_hash = descr.genesis_hash

    return Descr(
        head_hash=head_hash,
        genesis_hash=descr.genesis_hash,
        bytes=d.SerializeToString()
    )


def add(root_path, payload):
    descr = load_descr(root_path)
    block = make_block(descr.head_hash, payload)
    descr = descr_with_head_hash(descr, block.hash)

    with descr_file(root_path, 'wb') as d, block_file(root_path, block.hash, 'wb') as b:
        b.write(block.bytes)
        d.write(descr.bytes)
    os.sync()

    return block.hash


def descr(root_path):
    descr = load_descr(root_path)
    return descr
