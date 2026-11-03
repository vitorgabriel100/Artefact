"""Resolve project paths independently of the current working directory."""

import os
from pathlib import Path

# A instalação documentada é editável: src/emporio fica dentro do projeto extraído.
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def data_directory() -> Path:
    """Allow an environment override without modifying the original CSVs."""
    return Path(os.environ.get('EMPORIO_DATA_DIR', PROJECT_ROOT / 'data')).resolve()
