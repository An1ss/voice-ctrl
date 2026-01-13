# Agent Preferences

## Git/GitHub
- **Authentication:** SSH only (`git@github.com:...`)
- SSH keys already configured
- Never use HTTPS tokens

## Ralph & PRD Skills

### /ralph Skill
Sets up new projects: chats about features → creates prd.json → sets up structure

### /prd Skill
Generates detailed PRD markdown with user stories and acceptance criteria

### Ralph Workflow

**Run Ralph:**
```bash
bash scripts/ralph/ralph-claude.sh
```

**What Ralph does per story:**
1. Picks next `scope: "current"` story (skips backlog)
2. Implements with tests
3. Commits: `feat(US-XXX): title`
4. **Auto-pushes to GitHub**
5. Marks `passes: true` in prd.json
6. Logs to progress.txt

**Update PRD & Sync:**
```bash
# 1. Archive (optional)
cp tasks/prd.md tasks/prd.v1.0.0.md

# 2. Edit PRD - tag backlog with [BACKLOG]
vim tasks/prd-voice-dictation-app.md

# 3. Sync (preserves completed stories)
bash scripts/ralph/sync-prd.sh

# 4. Run Ralph
bash scripts/ralph/ralph-claude.sh
```

### Key Rules
- **Immutable:** Stories with `passes: true` never modified
- **Scope:** Remove `[BACKLOG]` tag to move to current scope
- **Versioning:** Use semantic versions (v1.0.0, v1.1.0, v2.0.0)

### Quick Commands
```bash
# Check status
jq '.userStories[] | {id, passes, scope}' prd.json

# View incomplete
jq '.userStories[] | select(.passes == false)' prd.json
```
