"""Run Aveli's real-browser guard suite against an isolated Moli server."""

import os
import runpy
from pathlib import Path
from urllib.parse import quote

from aveli.moli import IsolatedMoli, MoliConfig

HTML = """<!doctype html><title>Moli outcome check</title>
<label>City<input id="city" value="Zurich"></label>
<button id="save" onclick="document.body.dataset.saved=document.querySelector('#city').value">Save</button>"""


def check_outcome():
    from aveli.browser import Browser

    browser = Browser("data:text/html," + quote(HTML))
    try:
        page = browser.observe(screenshot=False)
        field = next(action for action in page["actions"] if action["kind"] == "fill")
        browser.act(field, page, text="London")
        value = browser.evaluate("document.querySelector('#city').value")
        assert value == "London", f"fill appended instead of replacing: {value!r}"
        page = browser.observe(screenshot=False)
        save = next(action for action in page["actions"] if action["label"] == "Save")
        browser.act(save, page)
        assert browser.evaluate("document.body.dataset.saved") == "London", "click outcome was not observed"
    finally:
        browser.close()
    print("MOLI_OUTCOME_PASS")


def main():
    config = MoliConfig.from_env(os.environ)
    with IsolatedMoli("browser-checks", config):
        check_outcome()
        runpy.run_path(str(Path(__file__).with_name("check_guards.py")), run_name="__main__")
    print("MOLI_COMPATIBILITY_PASS")


if __name__ == "__main__":
    main()
