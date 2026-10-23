import os
import pytest

os.environ["TEST_MODE"] = "true"

@pytest.fixture(autouse=True)
def set_test_mode():
    os.environ["TEST_MODE"] = "true"
    yield