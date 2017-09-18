import pytest

from ouroboros import blockchain
from ouroboros.blockchain import InvalidBlockchainException, BlockNotFoundException


def test_sha3_with_random_bytes():
    x = blockchain.sha3(b'a', b'b')
    assert x
