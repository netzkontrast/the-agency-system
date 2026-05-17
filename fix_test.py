import re

filepath = 'tests/unit/music/test_handlers_smoke.py'
with open(filepath, 'r') as f:
    content = f.read()

content = content.replace('if not name.startswith("_") and name != "status"', 'if not name.startswith("_")')
with open(filepath, 'w') as f:
    f.write(content)
