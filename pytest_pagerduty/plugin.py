import os
import logging
from typing import Optional

import pytest
import pagerduty


class PagerDutyApiClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        oauth_token: Optional[str] = None,
        default_from: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("PAGERDUTY_API_KEY")
        self.oauth_token = oauth_token or os.getenv("PAGERDUTY_OAUTH_TOKEN")
        self.default_from = default_from or os.getenv("PAGERDUTY_DEFAULT_FROM")
        self.client = self._initialize_client()

    def _initialize_client(self):
        """Initialize the PagerDuty client."""
        if self.api_key:
            return pagerduty.RestApiV2Client(
                api_key=self.api_key, default_from=self.default_from
            )
        elif self.oauth_token:
            return pagerduty.RestApiV2Client(
                api_key=self.oauth_token,
                default_from=self.default_from,
                auth_type="oauth2",
            )
        else:
            raise ValueError(
                "PagerDuty: no PagerDuty API key or OAuth token found."
            )

    def create_incident(
        self, summary: str, service_id: str, **kwargs
    ) -> Optional[str]:
        """Create a new PagerDuty incident."""
        data = {
            "incident": {
                "type": "incident",
                "title": summary,
                "service": {"id": service_id, "type": "service_reference"},
            }
        }
        if details := kwargs.get("details"):
            data["incident"]["body"] = {
                "type": "incident_body",
                "details": details,
            }

        if priority_id := kwargs.get("priority_id"):
            data["incident"]["priority"] = {
                "id": priority_id,
                "type": "priority_reference",
            }

        if escalation_policy_id := kwargs.get("escalation_policy_id"):
            data["incident"]["escalation_policy"] = {
                "id": escalation_policy_id,
                "type": "escalation_policy_reference",
            }

        if urgency := kwargs.get("urgency"):
            data["incident"]["urgency"] = urgency

        if incident_key := kwargs.get("incident_key"):
            data["incident"]["incident_key"] = incident_key

        if assignee_id := kwargs.get("assignee_id"):
            data["incident"]["assignments"] = [
                {"assignee": {"id": assignee_id, "type": "user_reference"}}
            ]

        response = self.client.rpost("/incidents", json=data)
        incident_id = response.get("id", None)

        if not incident_id:
            logging.warning(
                "PagerDuty: incident ID not found. Incident not created."
            )
        else:
            logging.debug(f"PagerDuty: created incident ID :: {incident_id}")

        return incident_id


class PagerDutyTestNotifier:
    def __init__(
        self, client: PagerDutyApiClient, request: pytest.FixtureRequest
    ):
        self.client = client
        self.request = request
        self.service_id = self._get_marker_kwarg("service_id")
        self.urgency = self._get_marker_kwarg("urgency")
        self.priority_id = self._get_marker_kwarg("priority_id")
        self.escalation_policy_id = self._get_marker_kwarg("escalation_policy_id")
        self.incident_key = self._get_marker_kwarg("incident_key")
        self.details = self._get_marker_kwarg("details")
        self.assignee_id = self._get_marker_kwarg("assignee_id")
        self.test_doc = self.request.node.function.__doc__

    def _get_marker_kwarg(self, name: str):
        """Get a keyword argument from the closest marker."""
        marker = self.request.node.get_closest_marker(
            "pagerduty_trigger_incident"
        )
        return marker.kwargs.get(name) if marker else None

    def on_failure(self):
        """Trigger a PagerDuty incident if the test failed."""
        if (
            hasattr(self.request.node, "rep_call")
            and self.request.node.rep_call.failed
        ):
            test_name = self.request.node.nodeid
            _, _, test_name = test_name.partition("::")

            test_name = test_name or "Unknown test"
            details_message = getattr(
                self.request.node.rep_call,
                "longreprtext",
                "No error message provided.",
            )

            logging.debug(
                f"PagerDuty: test '{test_name}' failed. Triggering PagerDuty incident."
            )

            if not self.details and self.test_doc:
                self.details = self._extract_details_from_docstring()
            elif not self.details and not self.test_doc:
                self.details = "No details provided for the test description."

            self.client.create_incident(
                summary=f"Test failure detected: '{test_name}'. Possible system issue.",
                service_id=self.service_id,
                urgency=self.urgency,
                details=f"{self.details}\n{'›'*50}\nASSERTION ERROR\n{details_message}",
                priority_id=self.priority_id,
                escalation_policy_id=self.escalation_policy_id,
                incident_key=self.incident_key,
                assignee_id=self.assignee_id,
            )

    def _extract_details_from_docstring(self):
        """Extract the first line or sentence from the docstring."""
        return self.test_doc.strip()


def _get_option_or_ini(request, name: str):
    """Get value from pytest options or ini file."""
    value = (
        request.config.getoption(f"--{name}")
        or request.config.getini(name)
        or None
    )
    if value is None:
        logging.debug(
            f"PagerDuty: no value found for '{name}'. Using default behavior."
        )
    return value


@pytest.fixture
def pagerduty_fixture(request):
    """Fixture to trigger a PagerDuty incident based on test results."""
    api_key, oauth_token, default_from = (
        _get_option_or_ini(request, name)
        for name in (
            "pagerduty_api_key",
            "pagerduty_oauth_token",
            "pagerduty_default_from",
        )
    )
    client = PagerDutyApiClient(api_key, oauth_token, default_from)
    notifier = PagerDutyTestNotifier(client, request)

    yield

    notifier.on_failure()


def pytest_addoption(parser):
    """Add custom pytest options for PagerDuty API credentials."""
    options = [
        ("pagerduty_api_key", "PagerDuty API Key (v2) to use."),
        ("pagerduty_oauth_token", "PagerDuty OAuth Token to use."),
        (
            "pagerduty_default_from",
            "Default email address to use as the 'from' field.",
        ),
    ]
    for opt_name, help_text in options:
        parser.addini(opt_name, default=None, help=help_text)
        parser.addoption(
            f"--{opt_name}", action="store", default=None, help=help_text
        )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):  # noqa
    """Hook to trigger a PagerDuty incident based on test results."""
    outcome = yield
    report = outcome.get_result()
    setattr(item, "rep_call", report)


def pytest_configure(config):
    """Configure the plugin and register the marker."""
    config.addinivalue_line(
        "markers",
        "pagerduty_trigger_incident(service_id, priority_id=None, escalation_policy_id=None, urgency=None, incident_key=None, details=None, assignee_id=None): "
        "Triggers a PagerDuty incident based on test results with optional escalation, priority, urgency, and incident key.",
    )
