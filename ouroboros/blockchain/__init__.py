import contextlib
import hashlib
import os
import time
from collections import namedtuple

Block = namedtuple('Block', ['hash', 'previous_hash', 'payload', 'bytes'])
Descr = namedtuple('Descr', ['genesis_hash', 'head_hash', 'bytes'])

ZERO_HASH = '0' * 96


class InvalidBlockchainException(Exception):
    pass


class BlockNotFoundException(Exception):
    pass


class HashDoNotMatchException(Exception):
    pass


def sha3(*args):
    m = hashlib.sha384()
    for x in args:
        m.update(x)

    return m.hexdigest()


def encode(s):
    if type(s) != bytes:
        return bytes(s, 'utf-8')
    return s


def decode(b):
    if type(b) != str:
        return str(b, 'utf-8')
    return b


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
        raise InvalidBlockchainException from e


@contextlib.contextmanager
def block_file(root_path, hash_, mode):
    try:
        block = path_block(root_path, hash_)
        with open(block, mode) as f:
            yield f
    except FileNotFoundError as e:
        raise BlockNotFoundException() from e


def make_block(previous_hash, payload):
    """Produce a new block"""
    # Generate a fingerprint of the new state:
    # combine the fingerprint of the previous state and the content of the new state.
    hash_ = sha3(encode(previous_hash), payload)

    # Prepare the content we store on disk
    bytes_ = encode(previous_hash) + b'\n' + payload

    return Block(hash=hash_, previous_hash=previous_hash, payload=payload,
                 bytes=bytes_)


def load_block(root_path, hash):
    with block_file(root_path, hash, 'rb') as f:
        return make_block(decode(f.readline()[:-1]), f.read())


def get_payload(root_path, hash):
    with descr_file(root_path, 'rb'):
        block = load_block(root_path, hash)
        return block.payload


def make_descr(genesis_hash, head_hash):
    bytes_ = encode(f'{genesis_hash}\n{head_hash}')
    return Descr(genesis_hash=genesis_hash, head_hash=head_hash, bytes=bytes_)


def descr_with_head_hash(descr, head_hash):
    return make_descr(descr.genesis_hash, head_hash)


def load_descr(root_path):
    with descr_file(root_path, 'rb') as f:
        return make_descr(decode(f.readline()[:-1]), decode(f.readline()))


def init(path, genesis_payload=None):
    # Prepare the initial block
    if genesis_payload is None:
        genesis_payload = bytes(str(time.time()), encoding="ascii")

    genesis_block = make_block(ZERO_HASH, genesis_payload)
    descr = make_descr(genesis_block.hash, genesis_block.hash)

    # TODO: assert no descr file -> do not init twice.
    with descr_file(path, 'wb') as d, block_file(path, genesis_block.hash, 'wb') as b:
        b.write(genesis_block.bytes)
        d.write(descr.bytes)

    os.sync()

    return genesis_block.hash


def list(root_path, show_genesis=False):
    # Load the description
    descr = load_descr(root_path)
    current = descr.head_hash
    last = descr.genesis_hash

    # Start from the last block and move up
    while current != last:
        block = load_block(root_path, current)
        yield block
        current = block.previous_hash

    # Finally
    if show_genesis:
        block = load_block(root_path, current)
        yield block


def prepare_block(root_path, payload):
    # Load the current blockchain state
    current_descr = load_descr(root_path)

    # Create the new block attached to the current head of the chain
    block = make_block(current_descr.head_hash, payload)

    # Prepare the new blockchain state
    new_descr = descr_with_head_hash(current_descr, block.hash)

    return new_descr, block


def store_new_block(root_path, new_descr, block):
    """Write the new description and the new block to disk."""
    with descr_file(root_path, 'wb') as d, block_file(root_path, block.hash, 'wb') as b:
        b.write(block.bytes)
        d.write(new_descr.bytes)
    os.sync()


def append(root_path, payload):
    """
    Append a new block to our chain using the given payload.
    Returns the block to share with others participants.
    """
    new_descr, block = prepare_block(root_path, payload)
    store_new_block(root_path, new_descr, block)
    return block.hash


def add(root_path, proposed_block_hash, payload):
    """
    Make sure we agree on the proposed hash add the block to our chain.
    Use this when a block comes from an external source.
    """
    # Identical to append but we verify the hash first!
    new_descr, block = prepare_block(root_path, payload)

    if block.hash != proposed_block_hash:
        raise HashDoNotMatchException()

    store_new_block(root_path, new_descr, block)
    return block.hash


def describe(root_path):
    return load_descr(root_path)
