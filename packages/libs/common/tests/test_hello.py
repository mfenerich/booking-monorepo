"""Hello unit test module."""

from booking_common.hello import hello


def test_hello():
    """Test the hello function."""
    assert hello() == "Hello common"
