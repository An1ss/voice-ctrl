# Agent Preferences and Configuration

## Git/GitHub Preferences

### Authentication Method
**Preference:** SSH (Option 2)

When pushing to GitHub repositories:
- Use SSH authentication (git@github.com:...)
- Do NOT use HTTPS with tokens
- SSH keys are already configured and added to GitHub

**Commands:**
```bash
# Set remote to SSH
git remote set-url origin git@github.com:<username>/<repo>.git

# Push
git push -u origin <branch>
```

### GitHub Operations
- Remote URL format: `git@github.com:<username>/<repo>.git`
- SSH key already generated and added to GitHub account
- No need to prompt for authentication tokens

---

## Ralph - Autonomous Development Agent

### Overview

Ralph is an autonomous development agent that implements user stories from a PRD (Product Requirements Document) automatically. It reads `prd.json`, picks incomplete stories, implements them, commits changes, and pushes to GitHub.

### Project Structure

```
voice-ctrl/
├── prd.json                           # User stories with status
├── tasks/
│   ├── prd-voice-dictation-app.md    # Human-readable PRD
│   └── prd-voice-dictation-app.v1.0.0.md  # Archived version (when created)
└── scripts/ralph/
    ├── ralph-claude.sh               # Main autonomous loop
    ├── sync-prd.sh                   # Sync markdown PRD → prd.json
    ├── parse-prd.py                  # Parse markdown to JSON
    ├── merge-stories.py              # Merge with existing stories
    └── progress.txt                  # Ralph's learnings log
```

### Using the /ralph Skill

**Purpose:** Set up Ralph for a new feature or project

**When to use:**
- Starting a new project from scratch
- Planning a new major feature

**What it does:**
1. Chats with you about the feature idea
2. Breaks it down into user stories
3. Creates `prd.json` with structured stories
4. Sets up project structure

**Example:**
```
User: /ralph
Claude: [Launches ralph skill to set up new feature]
```

### Using the /prd Skill

**Purpose:** Generate a comprehensive Product Requirements Document

**When to use:**
- Planning a new feature in detail
- Need a structured PRD before implementation
- Want to document requirements for a project

**What it does:**
1. Asks clarifying questions about your feature
2. Generates detailed PRD markdown with:
   - User stories
   - Acceptance criteria
   - Technical considerations
   - Success metrics

**Example:**
```
User: /prd for a voice dictation app
Claude: [Launches prd skill to create detailed PRD]
```

**Output:** Creates a markdown PRD file (e.g., `tasks/prd-voice-dictation-app.md`)

### Ralph Workflow

#### 1. Initial Setup (One Time)

**Option A: Start with /ralph**
```bash
# Let Ralph set up everything
User: /ralph
# Follow prompts, Ralph creates prd.json
```

**Option B: Start with /prd then /ralph**
```bash
# Create detailed PRD first
User: /prd for my feature
# Then set up Ralph
User: /ralph
```

#### 2. Running Ralph

**Start the autonomous loop:**
```bash
cd /home/aniss/dev/voice-ctrl
bash scripts/ralph/ralph-claude.sh
```

**What Ralph does per iteration:**
1. Reads `prd.json`
2. Picks next incomplete story (by priority, scope="current")
3. Implements the story following acceptance criteria
4. Runs tests/quality checks
5. Commits changes: `feat(US-XXX): Story title`
6. **Pushes to GitHub automatically**
7. Updates `prd.json` marking story complete
8. Logs learnings to `progress.txt`
9. Repeats until all stories complete

**Default:** Runs up to 50 iterations

**Custom iterations:**
```bash
bash scripts/ralph/ralph-claude.sh 100  # Run up to 100 iterations
```

#### 3. Managing Scope with [BACKLOG]

**Mark stories as backlog:**
```markdown
#### US-008: Load config file [BACKLOG]
```

**Stories without [BACKLOG] are in "current" scope**

Ralph **only works on current scope stories**, skipping backlog.

#### 4. Updating the PRD

**When you want to make changes to requirements:**

**Step 1: Archive current version**
```bash
cp tasks/prd-voice-dictation-app.md tasks/prd-voice-dictation-app.v1.0.0.md
```

**Step 2: Edit the PRD**
```bash
vim tasks/prd-voice-dictation-app.md
# Add new stories
# Modify incomplete stories
# Tag backlog items with [BACKLOG]
```

**Step 3: Sync to prd.json**
```bash
bash scripts/ralph/sync-prd.sh
```

**What sync does:**
- Parses markdown PRD
- Preserves completed stories (immutable)
- Adds new stories
- Updates incomplete stories
- Sets scope based on [BACKLOG] tags
- Shows summary of changes

**Step 4: Run Ralph**
```bash
bash scripts/ralph/ralph-claude.sh
```

### PRD Versioning Rules

**Immutability:**
- Stories with `passes: true` are **never modified** by sync
- They represent completed work and historical record

**Scope changes:**
- Remove `[BACKLOG]` tag to move story to current scope
- Add `[BACKLOG]` tag to defer a story

**Story modifications:**
- Can modify incomplete stories (`passes: false`)
- Completed stories stay unchanged even if PRD changes

### Common Workflows

#### Add a New Phase of Features

```bash
# 1. Edit PRD - add new stories
vim tasks/prd-voice-dictation-app.md

# 2. Sync to prd.json
bash scripts/ralph/sync-prd.sh

# 3. Run Ralph
bash scripts/ralph/ralph-claude.sh
```

#### Move Backlog to Current

```bash
# 1. Remove [BACKLOG] tags from stories
vim tasks/prd-voice-dictation-app.md
# Change: #### US-008: Story [BACKLOG]
# To:     #### US-008: Story

# 2. Sync
bash scripts/ralph/sync-prd.sh

# 3. Run Ralph
bash scripts/ralph/ralph-claude.sh
```

#### Check Ralph's Progress

```bash
# View prd.json status
jq '.userStories[] | {id, title, passes, scope}' prd.json

# View learnings
cat scripts/ralph/progress.txt

# Check recent commits
git log --oneline -10

# View GitHub repository
# https://github.com/<username>/<repo>
```

#### Pause and Resume Ralph

Ralph can be interrupted with `Ctrl+C` and resumed:

```bash
# Start Ralph
bash scripts/ralph/ralph-claude.sh

# Interrupt: Ctrl+C

# Resume later - Ralph picks up where it left off
bash scripts/ralph/ralph-claude.sh
```

### prd.json Structure

```json
{
  "project": "VoiceControl",
  "branchName": "ralph/mvp-phase-1",
  "description": "...",
  "userStories": [
    {
      "id": "US-001",
      "title": "Story title",
      "description": "...",
      "acceptanceCriteria": ["...", "..."],
      "priority": 1,
      "passes": true,      // Completed
      "scope": "current",  // or "backlog"
      "notes": "..."
    }
  ]
}
```

### Troubleshooting

**Ralph skips a story:**
- Check if it has `scope: "backlog"` in prd.json
- Change scope or remove [BACKLOG] from markdown and sync

**Sync doesn't update a story:**
- Check if story has `passes: true` (completed stories are immutable)
- Only incomplete stories can be updated

**Git push fails in Ralph:**
- Check SSH keys: `ssh -T git@github.com`
- Verify remote: `git remote -v`
- Should show: `git@github.com:<user>/<repo>.git`

**Want to modify a completed story:**
- Don't modify the completed story
- Create a new story (e.g., US-013: Fix/enhance US-003)
- This preserves history

### Best Practices

1. **Archive before major changes**
   ```bash
   cp tasks/prd-voice-dictation-app.md tasks/prd-voice-dictation-app.v1.0.0.md
   ```

2. **Use semantic versioning for archives**
   - `v1.0.0` - Initial MVP
   - `v1.1.0` - Minor additions
   - `v2.0.0` - Major changes

3. **Review sync changes before Ralph**
   ```bash
   bash scripts/ralph/sync-prd.sh
   git diff prd.json  # Review what changed
   ```

4. **Keep phases manageable**
   - 5-10 stories per phase is ideal
   - Use [BACKLOG] to defer lower priority work

5. **Let Ralph commit and push**
   - Don't manually commit during Ralph execution
   - Ralph handles all commits and pushes automatically

6. **Monitor Ralph's progress**
   - Watch the console output
   - Check `progress.txt` for learnings
   - Review commits on GitHub

### File Naming Conventions

**PRD Archives:**
- Current: `prd-voice-dictation-app.md`
- Archived: `prd-voice-dictation-app.v1.0.0.md`

**Format:** `prd-<project-name>.v<version>.md`

### Quick Reference

```bash
# Start Ralph
bash scripts/ralph/ralph-claude.sh

# Sync PRD
bash scripts/ralph/sync-prd.sh

# Check status
jq '.userStories[] | select(.passes == false) | {id, title, scope}' prd.json

# View completed
jq '.userStories[] | select(.passes == true) | {id, title}' prd.json

# Count progress
jq '[.userStories[] | select(.passes == true)] | length' prd.json

# Archive PRD
cp tasks/prd-voice-dictation-app.md tasks/prd-voice-dictation-app.v1.0.0.md
```

---

*This file documents user preferences and workflows for agent behavior.*
