import pytest

from ouroboros import blockchain
from ouroboros.blockchain import InvalidBlockchainException, BlockNotFoundException, HashDoNotMatchException

BASE_PAYLOAD = b"thisisapayload"
ALT_PAYLOAD = b"thisisadifferentpayload"


@pytest.fixture()
def dir(tmpdir):
    return tmpdir.mkdir("test")


@pytest.fixture()
def dir2(tmpdir):
    return tmpdir.mkdir("test_b")


def test_i_can_init_a_blockchain_in_an_empty_folder(dir):
    blockchain.init(dir)


def test_i_can_init_a_blockchain_then_list_will_be_an_empty_generator(dir):
    blockchain.init(dir)
    ls = blockchain.list(dir)

    assert list(ls) == []


def test_init_will_give_me_a_hash_I_can_retrieve(dir):
    genesis = blockchain.init(dir, genesis_payload=BASE_PAYLOAD)
    payload = blockchain.get_payload(dir, genesis)
    assert payload == BASE_PAYLOAD


def test_append_to_a_non_blockchain_fails(dir):
    with pytest.raises(InvalidBlockchainException):
        blockchain.append(dir, BASE_PAYLOAD)


def test_add_to_a_blockchin_succeeds(dir):
    blockchain.init(dir)
    blockchain.append(dir, BASE_PAYLOAD)


def test_i_can_append_a_block_ill_see_it_in_the_list(dir):
    blockchain.init(dir)

    blockchain.append(dir, BASE_PAYLOAD)
    ls = blockchain.list(dir)

    assert BASE_PAYLOAD in {x.payload for x in ls}


def test_get_in_non_blockchain_throws_invalid_blockchain(dir):
    with pytest.raises(InvalidBlockchainException):
        blockchain.get_payload(dir, '42')


def test_get_with_unknown_hash_throws_hash_not_found_exception(dir):
    blockchain.init(dir)

    with pytest.raises(BlockNotFoundException):
        blockchain.get_payload(dir, '42')


def test_append_returns_me_a_hash_id_i_can_reuse_to_retrieve_the_payload(dir):
    blockchain.init(dir)
    hash_id = blockchain.append(dir, BASE_PAYLOAD)
    blockchain.get_payload(dir, hash_id)


def test_descr_without_init_will_throw_blockchain_not_found(dir):
    with pytest.raises(InvalidBlockchainException):
        blockchain.describe(dir)


def test_descr_gives_me_the_hash_returned_by_init(dir):
    genesis = blockchain.init(dir)
    descr = blockchain.describe(dir)

    assert descr.head_hash == genesis
    assert descr.genesis_hash == genesis


def test_descr_gives_me_the_hash_of_the_last_add(dir):
    genesis = blockchain.init(dir)
    last_add = blockchain.append(dir, BASE_PAYLOAD)
    descr = blockchain.describe(dir)

    assert descr.head_hash == last_add
    assert descr.genesis_hash == genesis


def test_add_works_as_append(dir, dir2):
    # chain 1
    blockchain.init(dir, genesis_payload=BASE_PAYLOAD)
    hash_added = blockchain.append(dir, BASE_PAYLOAD)

    # chain 2
    blockchain.init(dir2, genesis_payload=BASE_PAYLOAD)

    # Act
    blockchain.add(dir2, hash_added, BASE_PAYLOAD)

    # Assert
    ls1 = blockchain.list(dir)
    ls2 = blockchain.list(dir2)
    assert list(ls1) == list(ls2), "both list should be equal."


def test_fails_when_chains_do_not_match(dir, dir2):
    # chain 1
    blockchain.init(dir, genesis_payload=BASE_PAYLOAD)
    hash_added = blockchain.append(dir, BASE_PAYLOAD)

    # chain 2, note the alternative payload
    blockchain.init(dir2, genesis_payload=ALT_PAYLOAD)

    # Act
    with pytest.raises(HashDoNotMatchException):
        blockchain.add(dir2, hash_added, BASE_PAYLOAD)
