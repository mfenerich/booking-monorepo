"""Hello unit test module."""

from booking_shared_models.hello import hello


def test_hello():
    """Test the hello function."""
    assert hello() == "Hello shared-models"
