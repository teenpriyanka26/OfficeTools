"""Compatibility shim for environments that still invoke setup.py directly."""

from setuptools import setup


# Project metadata lives in pyproject.toml so modern and legacy entry points
# cannot drift apart.
setup()
