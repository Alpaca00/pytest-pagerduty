import pytest


@pytest.fixture
def mock_pagerduty_client(mocker):
    """Mock the PagerDuty client."""
    return mocker.patch("pytest_pagerduty.plugin.pagerduty.RestApiV2Client")


# TODO: cover later
