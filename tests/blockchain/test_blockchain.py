import pytest

from ouroboros import blockchain
from ouroboros.blockchain import InvalidBlockchainException, BlockNotFoundException

BASE_PAYLOAD = b"thisisapayload"


@pytest.fixture()
def dir(tmpdir):
    return tmpdir.mkdir("test")


def test_i_can_init_a_blockchain_in_an_empty_folder(dir):
    blockchain.init(dir)


def test_i_can_init_a_blockchain_then_list_will_be_an_empty_generator(dir):
    blockchain.init(dir)
    ls = blockchain.list(dir)

    assert list(ls) == []


def test_i_can_add_a_block_ill_see_it_in_the_list(dir):
    blockchain.init(dir)
    blockchain.add(dir, BASE_PAYLOAD)

    ls = blockchain.list(dir)

    assert BASE_PAYLOAD in {x.payload for x in ls}


def test_init_will_give_me_a_hash_I_can_retrieve(dir):
    genesis = blockchain.init(dir, genesis_payload=BASE_PAYLOAD)
    payload = blockchain.get_payload(dir, genesis)
    assert payload == BASE_PAYLOAD


def test_add_to_a_non_blockchain_will_fail(dir):
    with pytest.raises(InvalidBlockchainException):
        blockchain.add(dir, BASE_PAYLOAD)


def test_add_to_a_blockchin_succeeds(dir):
    blockchain.init(dir)
    blockchain.add(dir, BASE_PAYLOAD)


def test_get_in_non_blockchain_throws_invalid_blockchain(dir):
    with pytest.raises(InvalidBlockchainException):
        blockchain.get_payload(dir, '42')


def test_get_with_unknown_hash_throws_hash_not_found_exception(dir):
    blockchain.init(dir)

    with pytest.raises(BlockNotFoundException):
        blockchain.get_payload(dir, '42')


def test_add_returns_me_a_hash_id_i_can_reuse_to_retrieve_the_payload(dir):
    blockchain.init(dir)
    hash_id = blockchain.add(dir, BASE_PAYLOAD)
    blockchain.get_payload(dir, hash_id)


def test_descr_without_init_will_throw_blockchain_not_found(dir):
    with pytest.raises(InvalidBlockchainException):
        blockchain.descr(dir)


def test_descr_gives_me_the_hash_returned_by_init(dir):
    genesis = blockchain.init(dir)
    descr = blockchain.descr(dir)

    assert descr.head_hash == genesis
    assert descr.genesis_hash == genesis


def test_descr_gives_me_the_hash_of_the_last_add(dir):
    genesis = blockchain.init(dir)
    last_add = blockchain.add(dir, BASE_PAYLOAD)
    descr = blockchain.descr(dir)

    assert descr.head_hash == last_add
    assert descr.genesis_hash == genesis
