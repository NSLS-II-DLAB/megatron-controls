from __future__ import annotations

import importlib.metadata

import megatron_controls as m


def test_version():
    assert importlib.metadata.version("megatron_controls") == m.__version__
