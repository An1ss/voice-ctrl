#!/usr/bin/env python3
"""
Merge new PRD stories into prd.json while preserving completed work.

Usage:
  cat prd.json | python scripts/ralph/merge-stories.py new-stories.json > updated-prd.json
"""

import json
import sys


def merge(existing_json, new_stories_json):
    """
    Merge new stories with existing prd.json

    Rules:
    - Keep all stories with passes=true (immutable)
    - Add new stories from new PRD
    - Update incomplete stories if they changed
    - Parse [BACKLOG] tags and set scope field
    """
    existing = json.loads(existing_json)
    new = json.loads(new_stories_json)

    # Keep completed stories (immutable)
    completed = [s for s in existing['userStories'] if s.get('passes', False)]
    completed_ids = {s['id'] for s in completed}

    # Add new/updated stories that aren't complete
    new_stories = [s for s in new['userStories'] if s['id'] not in completed_ids]

    # Merge
    merged = completed + new_stories

    # Parse [BACKLOG] from titles and set scope
    for story in merged:
        title = story.get('title', '')
        if '[BACKLOG]' in title:
            story['scope'] = 'backlog'
            story['title'] = title.replace('[BACKLOG]', '').strip()
        else:
            # Default to current if not already set
            if 'scope' not in story:
                story['scope'] = 'current'

    # Sort by priority
    existing['userStories'] = sorted(merged, key=lambda s: s.get('priority', 999))

    return json.dumps(existing, indent=2)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: cat prd.json | python merge-stories.py new-stories.json", file=sys.stderr)
        sys.exit(1)

    # Read existing prd.json from stdin
    existing = sys.stdin.read()

    # Read new stories from file argument
    with open(sys.argv[1], 'r') as f:
        new = f.read()

    # Merge and output
    result = merge(existing, new)
    print(result)
