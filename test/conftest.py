import os

import pytest

TEST_DIR = os.path.dirname(__file__)


@pytest.fixture()
def original_mkp_file():
    return _test_file('test_original.mkp')


@pytest.fixture()
def original_mkp_file_with_info_json():
    return _test_file('test_original_with_info_json.mkp')


def _test_file(filename):
    path = os.path.join(TEST_DIR, filename)
    with open(path, 'rb') as f:
        return f.read()
