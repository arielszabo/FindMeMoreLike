import pytest
import os

@pytest.mark.skipif(os.environ.get("TRAVIS") == "true", reason="needs lot of data")
def test_all():
    assert 1 == 2





