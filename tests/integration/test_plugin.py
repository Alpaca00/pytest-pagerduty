import pytest


@pytest.mark.usefixtures("pagerduty_fixture")
@pytest.mark.pagerduty_trigger_incident(service_id="AAW9VZA", urgency="low")
def test_expect_triggered_no_assignee():
    # without docstring
    expected_status_code = 200
    actual_status_code = 502
    assert expected_status_code == actual_status_code


class TestPagerDutyIntegration:
    """Test class to demonstrate the usage of the PagerDuty plugin."""

    @pytest.mark.usefixtures("pagerduty_fixture")
    @pytest.mark.pagerduty_trigger_incident(service_id="AAW9VZA", urgency="low")
    def test_expect_not_triggered(self, pagerduty_fixture):
        """Test case that passes and should not trigger a PagerDuty incident."""
        expected_status_code = 200
        actual_status_code = 200
        assert expected_status_code == actual_status_code

    @pytest.mark.usefixtures("pagerduty_fixture")
    @pytest.mark.pagerduty_trigger_incident(
        service_id="AAW9VZA", urgency="high", assignee_id="AA169AC"
    )
    def test_expect_triggered(self):
        """Test case that fails and should trigger a PagerDuty incident.

        Critical test case which verifies next behavior:
        - Authentication to the production environment
        - Data retrieval from the X service
        - Data processing via the Y service
        - Data validation via the Z service
        - Data storage to the production database
        - Sending a notification to the Billing team
        """
        expected_status_code = 200
        actual_status_code = 502
        assert expected_status_code == actual_status_code

    @pytest.mark.skip
    @pytest.mark.usefixtures("pagerduty_fixture")
    @pytest.mark.pagerduty_trigger_incident(service_id="AAW9VZA", urgency="low")
    def test_expect_skipped(self):
        """Test case that is skipped and should not trigger a PagerDuty incident."""
        expected_status_code = 200
        actual_status_code = 500
        assert expected_status_code == actual_status_code

    @pytest.mark.usefixtures("pagerduty_fixture")
    @pytest.mark.pagerduty_trigger_incident(service_id="AAW9VZA", urgency="low")
    def test_raise_error(self):
        """Test case that raises an error and should not trigger a PagerDuty incident."""
        with pytest.raises(Exception):
            _ = 1 / 0

    @pytest.mark.xfail
    @pytest.mark.usefixtures("pagerduty_fixture")
    @pytest.mark.pagerduty_trigger_incident(service_id="AAW9VZA", urgency="low")
    def test_asserts_in_loop(self):
        """Test case with asserts in a loop, expecting it to fail and should not trigger a PagerDuty incident."""
        for number in range(1, 10):
            assert number % 2 == 0, f"{number} is not a multiple of 2"

    @pytest.mark.parametrize("number", list(range(0, 10, 2)))
    @pytest.mark.usefixtures("pagerduty_fixture")
    @pytest.mark.pagerduty_trigger_incident(service_id="AAW9VZA", urgency="low")
    def test_asserts_by_parametrize_expect_passing(self, number):
        """Test case using parametrization that should pass and should not trigger a PagerDuty incident."""
        assert number % 2 == 0

    @pytest.mark.parametrize("number", list(range(0, 7, 3)))
    @pytest.mark.xfail
    @pytest.mark.usefixtures("pagerduty_fixture")
    @pytest.mark.pagerduty_trigger_incident(service_id="AAW9VZA", urgency="low")
    def test_asserts_by_parametrize_expect_failed(self, number):
        """Test case using parametrization that should fail and should not trigger a PagerDuty incident."""
        assert number % 2 == 0
