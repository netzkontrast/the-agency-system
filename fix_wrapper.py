import re

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # The issue is that the decorator doesn't copy type hints, causing Pydantic TypeAdapter
    # (used by fastmcp tool parsing) to crash with KeyError: 'view'.
    # Wait, the tool is modified in projection.py.
    # Let's check projection.py.
