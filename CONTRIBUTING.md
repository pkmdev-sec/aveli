# Contributing

## Set up the project

Install Python 3.12 or newer and [uv](https://docs.astral.sh/uv/), then run:

```bash
uv sync
cp .env.example .env
```

Add provider credentials to `.env` only when you run a live example. Tests do not use paid APIs.

## Make a change

Keep the agent loop small:

```text
page -> indexed elements -> operation and target -> execution
```

Follow these rules:

- Accept one natural-language goal. Do not add site-specific plans or hard-coded field values.
- Let TypeSafe choose one operation and its compatible target in one request.
- Map every target to an observed element and a supported operation.
- Do not let a model emit selectors or executable code.
- Use the text model only for `TYPE_TEXT` values.
- Do not retry browser mutations.
- Verify final outcomes independently. A `DONE` choice is not proof of success.
- Keep credentials in `.env`. Do not commit them.

## Run the checks

```bash
uv run ruff check .
uv run pytest
node --check aveli/static/app.js
node --check aveli/snapshot.js
uv build
uv run python scripts/check_secrets.py
```

If you change browser behavior, run the relevant smoke check described in [docs/development.md](docs/development.md). Keep README claims, measurement files, model-call counts, and recorded media consistent.

## Submit the change

Open a focused pull request. Explain the observable behavior, limits, and verification you ran. Do not include generated build output, local browser data, credentials, or internal planning notes.
