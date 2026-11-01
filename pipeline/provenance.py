# -*- coding: utf-8 -*-
"""Provenance helpers shared by pipeline steps (Step 6 support)."""
import subprocess
from datetime import datetime, timezone


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def git_sha():
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return out.stdout.strip() or None
    except Exception:
        return None


def stamp(model, model_version, prompt_version, schema_version, auditor=None):
    return {
        "model": model,
        "model_version": model_version,
        "prompt_version": prompt_version,
        "schema_version": schema_version,
        "timestamp": now_iso(),
        "git_sha": git_sha(),
        "auditor": auditor,
        "adjudication_status": "not_adjudicated",
    }
