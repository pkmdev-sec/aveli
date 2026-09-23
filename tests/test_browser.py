from unittest.mock import Mock

import pytest

from aveli import browser as browser_module
from aveli.browser import Browser, browser_operation


def observed(actions):
    return {
        "url": "https://example.test/",
        "title": "Page",
        "text": "Page",
        "scroll": {"y": 0},
        "actions": actions,
        "marker": [],
        "page_key": [],
        "guards": {},
    }


def test_initial_observation_retries_until_page_controls_exist(monkeypatch):
    empty = observed([{"id": "wait", "kind": "wait", "label": "Wait"}])
    ready = observed([{"id": "e1", "kind": "click", "label": "Continue", "node": 1}])
    operation = Mock(side_effect=[empty, empty, ready])
    monkeypatch.setattr(browser_module, "browser_operation", operation)
    monkeypatch.setattr(browser_module.time, "sleep", Mock())
    browser = Browser.__new__(Browser)
    browser.session = "session"
    browser.after_input = None
    page = browser.observe(screenshot=False)
    assert page is ready
    assert operation.call_count == 3


def test_initial_observation_of_control_free_page_is_bounded(monkeypatch):
    empty = observed([{"id": "wait", "kind": "wait", "label": "Wait"}])
    operation = Mock(return_value=empty)
    monkeypatch.setattr(browser_module, "browser_operation", operation)
    monkeypatch.setattr(browser_module.time, "sleep", Mock())
    browser = Browser.__new__(Browser)
    browser.session = "session"
    browser.after_input = None
    assert browser.observe(screenshot=False) is empty
    assert operation.call_count == 10


def test_screenshot_timeout_preserves_structured_observation(monkeypatch):
    info = observed([{"id": "wait", "kind": "wait", "label": "Wait"}])

    def cdp(method, session_id=None, **params):
        if method == "Runtime.evaluate":
            return {"result": {"value": dict(info)}}
        if method == "Page.captureScreenshot":
            raise TimeoutError("screenshot timed out")
        raise AssertionError(method)

    monkeypatch.setattr(browser_module, "cdp", cdp)
    page = browser_operation({"operation": "observe", "session": "s", "screenshot": True})
    assert page["url"] == info["url"]
    assert page["screenshot"] is None


def test_select_requires_an_observed_option_identity(monkeypatch):
    action = {"id": "e1", "kind": "select", "node": 1, "value": "same", "label": "Available"}
    monkeypatch.setattr(browser_module, "cdp", Mock())
    with pytest.raises(ValueError, match="option identity"):
        browser_operation({"operation": "act", "session": "s", "action": action, "text": None})


def test_select_passes_exact_option_identity_to_executor(monkeypatch):
    expressions = []
    action = {
        "id": "e1",
        "kind": "select",
        "node": 1,
        "option_node": 7,
        "value": "same",
        "label": "Available",
    }

    def cdp(method, session_id=None, **params):
        if method == "Runtime.evaluate":
            expressions.append(params["expression"])
            return {"result": {"value": {"x": 1, "y": 1}}}
        return {}

    monkeypatch.setattr(browser_module, "cdp", cdp)
    browser_operation({"operation": "act", "session": "s", "action": action, "text": None})
    assert '"option_node": 7' in expressions[0]


def test_partial_browser_startup_closes_created_target(monkeypatch):
    calls = []

    def cdp(method, **params):
        calls.append((method, params))
        if method == "Target.createTarget":
            return {"targetId": "created"}
        if method == "Target.attachToTarget":
            raise RuntimeError("attach failed")
        return {}

    monkeypatch.setattr(browser_module, "ensure_daemon", Mock())
    monkeypatch.setattr(browser_module, "cdp", cdp)
    with pytest.raises(RuntimeError, match="attach failed"):
        Browser("https://example.test/")
    assert calls[-1] == ("Target.closeTarget", {"targetId": "created"})


def test_before_mutation_runs_after_freshness_and_immediately_before_operation(monkeypatch):
    import aveli.browser as browser

    instance = browser.Browser.__new__(browser.Browser)
    instance.session = "session"
    instance.after_input = None
    events = []
    instance.fresh = Mock(side_effect=lambda *_: events.append("fresh") or True)
    monkeypatch.setattr(browser, "browser_operation", lambda *_: events.append("operation"))
    instance.act(
        {"kind": "click", "node": 1},
        {"fingerprint": "f"},
        before_mutation=lambda: events.append("intent"),
    )
    assert events == ["fresh", "intent", "operation"]


def test_stale_action_never_records_mutation_intent(monkeypatch):
    import aveli.browser as browser

    instance = browser.Browser.__new__(browser.Browser)
    instance.fresh = Mock(return_value=False)
    intent = Mock()
    with pytest.raises(browser.StalePage):
        instance.act({"kind": "click", "node": 1}, {"fingerprint": "f"}, before_mutation=intent)
    intent.assert_not_called()
