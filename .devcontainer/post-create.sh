#!/usr/bin/env bash

# Ensure pip is up to date
python3 -m pip install --upgrade pip

# Install essential dev tools
pip install black flake8 isort mypy pytest debugpy

# Optional: install data science packages
pip install numpy pandas matplotlib jupyter protobuf

# Clean up if needed
pip cache purge
