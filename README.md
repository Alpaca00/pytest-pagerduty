## pytest-pagerduty

This plugin integrates [PagerDuty](https://www.pagerduty.com/platform/incident-management/) incident management with your pytest test suite. 

It automatically triggers a PagerDuty incident when a test failure occurs, allowing for real-time monitoring and faster incident response.

### Installation

```bash
pip install pytest-pagerduty
```

### Configuration

Set the required PagerDuty credentials as environment variables or provide them via pytest options:

```commandline
# Use your PagerDuty API key or OAuth token either as environment variables or pytest options
export PAGERDUTY_API_KEY="your_api_key"
export PAGERDUTY_OAUTH_TOKEN="your_oauth_token"
export PAGERDUTY_DEFAULT_FROM="your_business_email@example.com"
```

Alternatively, use pytest command-line options:

```commandline
pytest --pagerduty_api_key=your_api_key \
       --pagerduty_oauth_token=your_oauth_token \
       --pagerduty_default_from=your_business_email@example.com
```

You can also configure options through a `pytest.ini` file or section in the project configuration file:

```ini
[pytest]
pagerduty_api_key = your_api_key
pagerduty_oauth_token = your_oauth_token
pagerduty_default_from = your_business_email@example.com
```

**Plugin registration**

Ensure the plugin is registered globally by adding the following line to `tests/conftest.py`:

```python
pytest_plugins = ["pytest_pagerduty.plugin"]
```

### Usage

**Marking tests for incident reporting**

Use the `pagerduty_fixture` fixture to enable the plugin and the
`@pytest.mark.pagerduty_trigger_incident` marker to specify tests that should trigger PagerDuty incidents on failure.

```python
import pytest

@pytest.mark.usefixtures("pagerduty_fixture")
@pytest.mark.pagerduty_trigger_incident(service_id="XIXOOXZ", urgency="high", assignee_id="SE169QA")
def test_critical_feature():
    """Verifies the critical feature behavior."""
    assert False  # This will trigger a PagerDuty incident and assign it to the specified user who will be responsible for resolving the incident

@pytest.mark.usefixtures("pagerduty_fixture")
@pytest.mark.pagerduty_trigger_incident(service_id="XIXOOXZ", urgency="low")
def test_service_failure():
    """Validates the service availability."""
    assert False  # This will trigger a PagerDuty incident with low urgency level


@pytest.mark.usefixtures("pagerduty_fixture")
@pytest.mark.pagerduty_trigger_incident(service_id="IIXOOXZ", urgency="high")
def test_critical_flow():
    """Validates the critical flow.
    
    Critical test case which verifies next behavior:
    - Authentication to the production environment
    - Data retrieval from the X service
    - Data processing via the Y service
    - Data validation via the Z service
    - Data storage to the production database
    - Sending a notification to the Billing team
    """
    ...
    expected_status_code = 201
    actual_status_code = 502
    assert expected_status_code == actual_status_code  # This will trigger a PagerDuty incident and docstring will be included in the incident details
```

**Marker Parameters**

- `service_id` (required): The PagerDuty service ID.

- `priority_id` (optional): Incident priority reference.

- `escalation_policy_id` (optional): Escalation policy ID.

- `urgency` (optional): Incident urgency (e.g., "high" or "low").

- `incident_key` (optional): Deduplication key to prevent duplicate incidents.

- `details` (optional): Custom message for the incident body.

- `assignee_id` (optional): User ID to assign the incident.


### PagerDuty incident structure

When a test fails, an incident is created with the following information:

- `Summary` - Test failure message, including the test name.

- `Details` - Test docstring and assertion error traceback.

- `Service` - Linked to the specified PagerDuty service.

- `Urgency, Escalation Policy` - Configurable via markers.


### MIT License

Distributed under the MIT License. See [LICENSE](LICENSE.md) for more information.

### Warranty

**THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.**

### Useful links

- [python-pagerduty APIs:](https://pagerduty.github.io/python-pagerduty/) Clients for PagerDuty’s APIs documentation.
- [python-pagerduty:](https://github.com/PagerDuty/python-pagerduty) GitHub repository for the python-pagerduty library.
- [API Reference:](https://developer.pagerduty.com/docs/introduction) PagerDuty REST API documentation.