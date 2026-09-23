# Gates: browser correctness and lifecycle

Scope: Fix the known initial-observation, screenshot, native-select identity, and partial-startup cleanup defects.

- [x] G1: Empty initial action snapshots retry for a bounded period instead of immediately reaching the model.
  CHECK: uv run pytest -q tests/test_browser.py -k initial
  EXPECT: passed
  EVIDENCE: `tests/test_browser.py` bounded retry regression passed in the 86-test suite (2026-09-18).

- [x] G2: Optional screenshot timeout preserves the completed structured observation.
  CHECK: uv run pytest -q tests/test_browser.py -k screenshot
  EXPECT: passed
  EVIDENCE: Screenshot timeout regression passed; structured observation was retained with `screenshot=None`.

- [x] G3: Native select executes the exact observed option identity and rejects stale/replaced options.
  CHECK: uv run pytest -q tests/test_browser.py -k select
  EXPECT: passed
  EVIDENCE: Unit regression passed and isolated Chrome selected index 2 when two options shared the same value.

- [x] G4: Partial Browser initialization closes any target it created.
  CHECK: uv run pytest -q tests/test_browser.py -k cleanup
  EXPECT: passed
  EVIDENCE: Partial-startup cleanup regression passed and asserted `Target.closeTarget`.
