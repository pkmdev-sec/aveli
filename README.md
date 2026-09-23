<img src="docs/banner.svg" alt="Aveli indexed browser agent" width="100%" />

# Aveli
[![CI](https://github.com/pkmdev-sec/aveli/actions/workflows/ci.yml/badge.svg)](https://github.com/pkmdev-sec/aveli/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![MIT license](https://img.shields.io/badge/license-MIT-2A743F)](LICENSE)

```text
   A    V   V  EEEEE  L      IIIII
  A A   V   V  E      L        I
 AAAAA  V   V  EEEE   L        I
 A   A   V V   E      L        I
 A   A    V    EEEEE  LLLLL  IIIII
```

Aveli is a Python browser agent that lets models choose from controls already found on the page. [TypeSafe's Jev](https://docs.typesafe.ai/introduction) selects an operation and a compatible target. A separate text model writes content only for `TYPE_TEXT`.

The recorded Google Flights example completes a Zurich-to-London search in 7.073 seconds. It includes generated city names, browser work, and page-load waits.

<a href="docs/demo.mp4"><img src="docs/demo.gif" alt="Aveli completing a Google Flights search at original speed" width="100%" /></a>

[Watch the MP4](docs/demo.mp4) · [Read the measurements](docs/performance.md) · [Inspect the agent loop](aveli/agent.py)

## How Aveli works

Each observation produces an indexed table of visible controls:

```text
[1] button    Change ticket type · Round trip
[2] combobox  Where from?        · San Francisco
[3] combobox  Where to?          · empty
[4] textbox   Departure          · empty
```

Aveli supports `CLICK`, `TYPE_TEXT`, `SELECT`, `SCROLL_UP`, `SCROLL_DOWN`, `WAIT`, `DONE`, and `BLOCKED`. The model receives only targets that support the proposed operation. It never emits selectors, coordinates, JavaScript, or shell commands.

```mermaid
flowchart LR
    public["Inspector or library<br/>URL + goal"]
    worker["Internal worker<br/>job JSON"]
    runner["IsolatedChrome + ProductionRunner<br/>policy · approval · verification"]
    agent["Agent<br/>predict → act → observe"]
    typesafe["TypeSafe Jev<br/>operation + compatible target"]
    text["Text model<br/>TYPE_TEXT only"]
    browser["Browser + snapshot.js<br/>CDP · observed nodes · freshness guards"]
    chrome["Chrome page"]
    state["Inspector or library<br/>state + trace"]
    result["Worker outputs<br/>audit JSONL + verified result"]

    public -->|create| agent
    worker -->|validate job| runner
    runner -->|predict or approved act| agent
    agent -->|proposal or final page| runner
    chrome -->|visible DOM| browser
    browser -->|page + indexed actions| agent
    agent -->|state + target heads| typesafe
    typesafe -->|operation + target| agent
    agent -.->|field context| text
    text -.->|validated JSON text| agent
    agent -->|observed action| browser
    browser -->|CDP input| chrome
    agent -->|snapshot| state
    runner -->|events + result| result
```

The detailed design explains node identity, freshness checks, text caching, waits, and execution boundaries in [docs/design.md](docs/design.md).

## Quick start

Requirements:

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)
- Chrome with remote debugging enabled for [Browser Harness](https://github.com/browser-use/browser-harness)
- TypeSafe and text-model API keys

```bash
uv sync
cp .env.example .env
# Add TYPESAFE_API_KEY and TEXT_MODEL_API_KEY to .env.
uv run aveli
```

Open `http://127.0.0.1:8766`. Select **Start demo**, then select **Run automatically**. If Chrome does not connect, run `uv run browser-harness --doctor`.

See [configuration and development](docs/development.md) for provider settings, browser checks, recording commands, and the experimental Moli probe.

## Use the library

```python
from aveli import Agent

with Agent(
    "https://www.google.com/travel/flights?hl=en",
    "Find one-way flights from Zurich to London on September 20, 2026, "
    "for one adult in economy. Stop when matching flight options are visible.",
) as agent:
    for state in agent.run():
        print(state["elapsed_ms"], state["status"])
```

Run the example with your environment file:

```bash
uv run --env-file .env python examples/run.py \
  --url https://en.wikipedia.org/wiki/Main_Page \
  --goal 'Find and open the Wikipedia article about Gödel’s incompleteness theorems.'
```

Each yielded value is a snapshot of the agent state. Your application must verify the final page independently. `DONE` is a model choice, not proof of success.

## Safety boundaries

- One TypeSafe request carries the operation and compatible target heads.
- Every executable target comes from the current DOM snapshot.
- The browser checks freshness, visibility, geometry, and click occlusion before input.
- Text-model output must be a bounded JSON object.
- Aveli never retries a browser mutation.

The DOM reader supports common HTML and ARIA controls. It does not yet support shadow roots, frames, canvas, uploads, pop-up tabs, nested scrolling, or arbitrary keyboard widgets.

The inspector is not a production service. Bounded internal jobs use a separate fail-closed worker with host and action policy, isolated Chrome, audit events, approval hooks, and independent verification. See the [internal production runbook](docs/internal-production.md).

## Evidence

The current video records one Google Flights task at original speed. All six matched comparison runs passed, but they cover one task on one browser profile. They do not establish general browser-agent reliability.

The full report records model versions, source hashes, timings, failures, and measurement boundaries in [docs/performance.md](docs/performance.md).

## Project map

| Area | Source |
| --- | --- |
| Agent loop | [`aveli/agent.py`](aveli/agent.py) |
| Browser snapshot and execution | [`aveli/browser.py`](aveli/browser.py), [`aveli/snapshot.js`](aveli/snapshot.js) |
| Model boundary | [`aveli/model.py`](aveli/model.py) |
| Production worker | [`aveli/runner.py`](aveli/runner.py), [`aveli/worker.py`](aveli/worker.py) |

## Development

```bash
uv run ruff check .
uv run pytest
node --check aveli/static/app.js
node --check aveli/snapshot.js
uv build
```

Tests do not call paid APIs. Live examples and recording scripts do. Read [docs/development.md](docs/development.md) before running browser checks or recordings.

Contributions are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## Documentation

[Documentation index](docs/README.md) · [Design](docs/design.md) · [Configuration and development](docs/development.md) · [Performance](docs/performance.md) · [Internal production](docs/internal-production.md)

Built with [Browser Use](https://github.com/browser-use/browser-use), [Browser Harness](https://github.com/browser-use/browser-harness), and [TypeSafe speculative fan-out](https://docs.typesafe.ai/patterns/fan-out).
