import os
import glob
import re

for path in glob.glob('skills/music/*/SKILL.md'):
    with open(path, 'r') as f:
        content = f.read()

    # Only replace exactly the first occurrence of "name: " within the frontmatter block
    # We can rely on re.sub with count=1 because "name: " will generally be the only thing we want to change there
    # But to be perfectly safe, let's just find the line starting with "name: "
    lines = content.split('\n')
    in_frontmatter = False
    for i, line in enumerate(lines):
        if line == '---':
            if not in_frontmatter:
                in_frontmatter = True
            else:
                break # Reached end of frontmatter
        elif in_frontmatter and line.startswith('name: '):
            slug = line.split('name: ')[1].strip()
            # In case someone already prefixed it or ran the script twice, skip if already music-
            if not slug.startswith('music-'):
                lines[i] = f'name: music-{slug}'
            break # only replace once

    new_content = '\n'.join(lines)
    with open(path, 'w') as f:
        f.write(new_content)

print("Renamed frontmatter.")
