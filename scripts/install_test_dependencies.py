#!/usr/bin/env python3
"""Install the test dependencies declared by pyproject.toml."""

from __future__ import annotations

import subprocess
import sys
import tomllib


with open("pyproject.toml", "rb") as file:
    dependencies = tomllib.load(file)["project"]["optional-dependencies"]["test"]

oracle = next(item for item in dependencies if item.startswith("Brotli"))
subprocess.run([sys.executable, "-m", "pip", "install", oracle], check=True)
