import pytest
from src.utils import generate_short_code


def test_generate_short_code_returns_string():
    code = generate_short_code()
    assert isinstance(code, str)


def test_generate_short_code_default_length():
    code = generate_short_code()
    assert len(code) == 10


def test_generate_short_code_custom_length():
    code = generate_short_code(5)
    assert len(code) == 5


def test_generate_short_code_custom_empty_length():
    code = generate_short_code(0)
    assert len(code) == 0


def test_generate_short_code_letters_digits():
    code = generate_short_code()
    assert code.isalnum()
