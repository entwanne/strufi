import pytest

import strufi


@pytest.mark.parametrize(
    "input_data",
    [
        "0",
        '%"abc"',
        'abc;a=0;foo="bar"',
    ],
)
def test_item_idempotency(input_data):
    assert strufi.dump_item(strufi.load_item(input_data)) == input_data


@pytest.mark.parametrize(
    "input_data",
    [
        "0, 1, 2",
        '%"abc", "def"',
        '(abc "def";a=0 %"ghi"), token',
    ],
)
def test_list_idempotency(input_data):
    assert strufi.dump_list(strufi.load_list(input_data)) == input_data


@pytest.mark.parametrize(
    "input_data",
    [
        'key=token;foo="bar"',
        'key=("foo" %"test";param="value")',
    ],
)
def test_dict_idempotency(input_data):
    assert strufi.dump_dict(strufi.load_dict(input_data)) == input_data


@pytest.mark.parametrize(
    "input_data",
    [
        "0",
        '%"abc"',
        'abc',
    ],
)
def test_simple_item_idempotency(input_data):
    assert strufi.dump_simple_item(strufi.load_simple_item(input_data)) == input_data


@pytest.mark.parametrize(
    "input_data",
    [
        "0, 1, 2",
        '%"abc", "def"',
        '(abc "def" %"ghi"), token',
    ],
)
def test_simple_list_idempotency(input_data):
    assert strufi.dump_simple_list(strufi.load_simple_list(input_data)) == input_data


@pytest.mark.parametrize(
    "input_data",
    [
        'key=token',
        'key=("foo" %"test")',
    ],
)
def test_simple_dict_idempotency(input_data):
    assert strufi.dump_simple_dict(strufi.load_simple_dict(input_data)) == input_data
