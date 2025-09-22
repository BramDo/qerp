from __future__ import annotations
import json, pathlib

def save_json(obj, path):
    path = pathlib.Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f: json.dump(obj, f, indent=2)

def load_json(path):
    with open(path) as f: return json.load(f)
