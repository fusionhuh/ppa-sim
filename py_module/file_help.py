from pathlib import Path
import os

def create_file_parents(path: str):
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)

def write_text(path: str, text: str):
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(text)

def read_text(path: str):
    file = Path(path)
    return file.read_text()