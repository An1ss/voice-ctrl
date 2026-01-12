#!/usr/bin/env python3
"""
Parse markdown PRD into JSON format compatible with prd.json

Usage:
  python scripts/ralph/parse-prd.py tasks/prd-voice-dictation-app.md > new-stories.json
"""

import json
import re
import sys


def parse_story(story_text, story_id, story_title, is_backlog):
    """Parse a single user story from markdown section"""

    # Extract description
    desc_match = re.search(
        r'\*\*Description:\*\*\s+(.+?)(?=\n\n|\*\*)',
        story_text,
        re.DOTALL
    )
    description = desc_match.group(1).strip() if desc_match else ""

    # Extract acceptance criteria
    criteria = []
    criteria_section = re.search(
        r'\*\*Acceptance Criteria:\*\*(.+?)(?=\n\n#{1,4}|\*\*[A-Z]|\Z)',
        story_text,
        re.DOTALL
    )

    if criteria_section:
        criteria_text = criteria_section.group(1)
        # Find all checkboxes
        criteria = [
            line.strip('- [ ] ').strip()
            for line in criteria_text.split('\n')
            if line.strip().startswith('- [ ]')
        ]

    # Extract notes if present
    notes_match = re.search(
        r'\*\*Technical Notes:\*\*\s+(.+?)(?=\n\n#{1,4}|\Z)',
        story_text,
        re.DOTALL
    )
    notes = notes_match.group(1).strip() if notes_match else ""

    # Extract priority from ID (US-007 -> priority 7)
    priority = int(story_id.split('-')[1])

    # Set scope based on backlog flag
    scope = "backlog" if is_backlog else "current"

    return {
        "id": story_id,
        "title": story_title,
        "description": description,
        "acceptanceCriteria": criteria,
        "priority": priority,
        "passes": False,
        "scope": scope,
        "notes": notes
    }


def parse_prd(prd_content):
    """Parse entire PRD markdown into structured JSON"""

    stories = []

    # Find all user stories by matching the pattern: #### US-XXX: Title
    story_pattern = r'####\s+(US-\d+):\s+(.+?)(?:\s+\[BACKLOG\])?\s*\n'
    matches = list(re.finditer(story_pattern, prd_content))

    for i, match in enumerate(matches):
        story_id = match.group(1)
        story_title = match.group(2).strip()

        # Check for [BACKLOG] tag
        is_backlog = '[BACKLOG]' in match.group(0)
        # Remove [BACKLOG] from title if present
        story_title = story_title.replace('[BACKLOG]', '').strip()

        # Get the text from this story to the next story (or end of file)
        start = match.end()
        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(prd_content)

        story_text = prd_content[start:end]

        # Parse the story
        story = parse_story(story_text, story_id, story_title, is_backlog)
        stories.append(story)

    return {
        "project": "VoiceControl",
        "branchName": "ralph/mvp-phase-1",
        "description": "System-wide voice dictation tool for Ubuntu using OpenAI Whisper API",
        "userStories": stories
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python parse-prd.py <prd-markdown-file>", file=sys.stderr)
        sys.exit(1)

    prd_file = sys.argv[1]

    with open(prd_file, 'r') as f:
        prd_content = f.read()

    result = parse_prd(prd_content)
    print(json.dumps(result, indent=2))
