# Configuration and development

This guide covers local provider settings, browser checks, recordings, and the optional Moli compatibility probe.

## Configure providers

Copy the example environment file:

```bash
cp .env.example .env
```

Set these required values:

```dotenv
TYPESAFE_API_KEY=
TEXT_MODEL_API_KEY=
```

Aveli sends operation and target decisions to TypeSafe. It sends text-generation requests only when TypeSafe selects `TYPE_TEXT`.

The example configuration uses OpenRouter for the text model. You can use another OpenAI-compatible endpoint by changing `TEXT_MODEL_BASE_URL` and `TEXT_MODEL`. Keep `TYPESAFE_MODEL` set to a pinned TypeSafe Jev model in production.

Do not commit `.env`. Aveli loads credentials on the server side and does not send them to the inspector.

## Connect Chrome

Browser Harness connects Aveli to a running Chrome instance. Enable remote debugging when Chrome asks for permission.

Check the connection before running Aveli:

```bash
uv run browser-harness --doctor
```

Start the inspector:

```bash
uv run aveli
```

Open `http://127.0.0.1:8766`.

## Run checks

Run the offline checks before publishing a change:

```bash
uv run ruff check .
uv run pytest
node --check aveli/static/app.js
node --check aveli/snapshot.js
uv build
```

Run the local browser guard suite when Browser Harness can connect to Chrome:

```bash
uv run python scripts/check_guards.py
```

The guard suite uses local fixtures and does not call model APIs.

## Probe Moli compatibility

Moli is experimental and does not replace the default Chrome runtime. Install Moli 1.1.9, then run:

```bash
AVELI_MOLI_PATH=/path/to/moli uv run python scripts/check_moli.py
```

The probe rejects other versions. It starts Moli on loopback, runs the same local guard suite, and fails on protocol or behavior differences. It does not call model APIs.
