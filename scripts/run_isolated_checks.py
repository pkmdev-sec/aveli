"""Run the real-browser guard suite in an ephemeral Chrome profile."""

import os
import runpy
from pathlib import Path

from aveli.isolation import ChromeConfig, IsolatedChrome


def main():
    config = ChromeConfig.from_env(os.environ)
    with IsolatedChrome("browser-checks", config):
        runpy.run_path(str(Path(__file__).with_name("check_guards.py")), run_name="__main__")


if __name__ == "__main__":
    main()
