ARG PYTHON_IMAGE=python:3.13.11-slim-bookworm@sha256:20080e807bfc404f8450b185cf0fc95d553462673598549613735f70a5b4d5d0
FROM --platform=linux/amd64 ${PYTHON_IMAGE}

ARG UV_WHEEL_URL=https://files.pythonhosted.org/packages/f2/b3/4b9580d62e1245df52e8516cf3e404ff39cc72634d2d749d47b1dada4161/uv-0.10.4-py3-none-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
ARG UV_WHEEL_SHA256=82978155e571f2ac3dd57077bd746bfe41b65fa19accc3c92d1f09632cd36c63
ARG CHROME_DEB_URL=https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_153.0.8010.52-1_amd64.deb
ARG CHROME_DEB_SHA256=29e0e4b5af01213915ffdb7f4e49a11956dc5fc591165c85af8688dcdff907ac

RUN python -c 'import sys,urllib.request; urllib.request.urlretrieve(sys.argv[1], sys.argv[2])' "${UV_WHEEL_URL}" /tmp/uv.whl \
    && python -c 'import sys,urllib.request; urllib.request.urlretrieve(sys.argv[1], sys.argv[2])' "${CHROME_DEB_URL}" /tmp/chrome.deb \
    && echo "${UV_WHEEL_SHA256}  /tmp/uv.whl" | sha256sum --check --strict \
    && echo "${CHROME_DEB_SHA256}  /tmp/chrome.deb" | sha256sum --check --strict \
    && apt-get update \
    && apt-get install -y --no-install-recommends /tmp/chrome.deb \
    && pip install --no-cache-dir /tmp/uv.whl \
    && rm -f /tmp/uv.whl /tmp/chrome.deb \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 10001 aveli
WORKDIR /app
COPY pyproject.toml uv.lock README.md LICENSE ./
COPY aveli ./aveli
COPY scripts/container_healthcheck.py ./scripts/container_healthcheck.py
RUN uv sync --frozen --no-dev --no-editable \
    && mkdir -p /var/log/aveli /tmp/aveli \
    && chown -R aveli:aveli /app /var/log/aveli /tmp/aveli

USER 10001:10001
ENV PATH="/app/.venv/bin:${PATH}" \
    AVELI_CHROME_PATH=/usr/bin/google-chrome \
    AVELI_AUDIT_DIR=/var/log/aveli \
    AVELI_RUNTIME_ROOT=/tmp/aveli \
    PYTHONUNBUFFERED=1

VOLUME ["/var/log/aveli"]
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD ["python", "scripts/container_healthcheck.py"]
ENTRYPOINT ["aveli-internal-worker"]
