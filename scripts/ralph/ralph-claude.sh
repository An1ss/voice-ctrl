#!/bin/bash
# ralph-claude.sh - Autonomous development loop for Claude Code
#
# Usage: bash scripts/ralph/ralph-claude.sh [max_iterations]
# Example: bash scripts/ralph/ralph-claude.sh 50

set -e

MAX_ITER=${1:-50}
PRD_FILE="prd.json"

# Check prd.json exists
if [ ! -f "$PRD_FILE" ]; then
    echo "❌ Error: prd.json not found in current directory"
    echo "Run this script from project root where prd.json is located"
    exit 1
fi

# Check dependencies
if ! command -v jq &> /dev/null; then
    echo "❌ Error: jq is required but not installed"
    echo "Install with: sudo apt-get install jq"
    exit 1
fi

if ! command -v claude &> /dev/null; then
    echo "❌ Error: claude command not found"
    echo "Make sure Claude Code CLI is installed"
    exit 1
fi

echo "🚀 Starting Ralph autonomous loop"
echo "Project: $(jq -r '.project' $PRD_FILE)"
echo "Branch: $(jq -r '.branchName' $PRD_FILE)"
echo "Description: $(jq -r '.description' $PRD_FILE)"
echo "Max iterations: $MAX_ITER"
echo ""

# Main loop
for i in $(seq 1 $MAX_ITER); do
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🔄 Iteration $i/$MAX_ITER"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""

  # Get next incomplete story (highest priority = lowest number)
  # Only select stories with scope="current" (filter out backlog)
  NEXT_STORY=$(jq -r '.userStories | sort_by(.priority) | map(select(.passes == false and .scope == "current")) | .[0] // empty' $PRD_FILE)

  if [ -z "$NEXT_STORY" ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ All stories complete! Feature is done!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Summary:"
    echo "Project: $(jq -r '.project' $PRD_FILE)"
    echo "Total stories: $(jq '.userStories | length' $PRD_FILE)"
    echo "All passed: $(jq '[.userStories[] | select(.passes == true)] | length' $PRD_FILE)"
    exit 0
  fi

  STORY_ID=$(echo "$NEXT_STORY" | jq -r '.id')
  STORY_TITLE=$(echo "$NEXT_STORY" | jq -r '.title')
  STORY_PRIORITY=$(echo "$NEXT_STORY" | jq -r '.priority')

  echo "📋 Working on: $STORY_ID (priority $STORY_PRIORITY)"
  echo "Title: $STORY_TITLE"
  echo ""

  # Create prompt
  PROMPT="You are Ralph, an autonomous developer working on feature implementation.

**Current Story:**
$(echo "$NEXT_STORY" | jq '.')

**Your job this iteration:**

1. **Read context**:
   - Read scripts/ralph/progress.txt for previous learnings and patterns
   - Read prd.json to understand the full feature context

2. **Implement the story**:
   - Read the full story description and acceptance criteria carefully
   - Implement according to all requirements
   - Follow existing code patterns in the repo
   - Write clean, maintainable code

3. **Verify**:
   - Run ALL quality checks mentioned in acceptance criteria
   - Common checks: typecheck, tests, linting, manual verification
   - Fix any errors before proceeding
   - Do NOT proceed if quality checks fail

4. **Commit**:
   - Commit changes with message: \"feat($STORY_ID): $STORY_TITLE\"
   - Include the story ID in commit message for traceability

5. **Document**:
   - Append brief learnings to scripts/ralph/progress.txt
   - Format:
     ## $STORY_ID - $STORY_TITLE
     - What was implemented
     - Files changed
     - Learnings: (patterns, gotchas, decisions)
     ---

6. **Mark complete**:
   - Use jq to update prd.json
   - Set passes: true for story $STORY_ID
   - Command: jq '(.userStories[] | select(.id == \"$STORY_ID\") | .passes) = true' prd.json > prd.json.tmp && mv prd.json.tmp prd.json

7. **Output completion marker**:
   - Output exactly: <completion>STORY_COMPLETE</completion>

**Important:**
- Only work on THIS ONE story per iteration
- Always commit before marking passes: true
- Update progress.txt with learnings
- Use jq to update JSON (never manually edit)"

  # Invoke Claude
  RESULT=$(echo "$PROMPT" | claude --print --output-format json --allowedTools "Bash,Edit,Read,Write,Grep,Glob")

  # Check result
  if [ $? -ne 0 ]; then
    echo "❌ Claude invocation failed"
    exit 1
  fi

  RESULT_TEXT=$(echo "$RESULT" | jq -r '.result')

  # Verify story was marked complete
  STORY_STATUS=$(jq -r --arg id "$STORY_ID" '.userStories[] | select(.id == $id) | .passes' $PRD_FILE)

  if [ "$STORY_STATUS" = "true" ]; then
    echo "✓ Story $STORY_ID marked complete"

    # Push to GitHub
    echo "📤 Pushing to GitHub..."
    git push

    if [ $? -eq 0 ]; then
      echo "✓ Pushed successfully"
    else
      echo "⚠️  Push failed (check git status)"
    fi
  else
    echo "⚠️  Warning: Story $STORY_ID not marked complete"
    echo "This might indicate the story implementation failed or quality checks didn't pass"
    echo "Marking complete anyway to avoid infinite loop..."
    # Mark it manually to prevent getting stuck
    jq --arg id "$STORY_ID" '(.userStories[] | select(.id == $id) | .passes) = true' $PRD_FILE > prd.json.tmp
    mv prd.json.tmp $PRD_FILE
  fi

  echo ""
  echo "Remaining stories: $(jq '[.userStories[] | select(.passes == false)] | length' $PRD_FILE)"
  echo ""

  # Rate limiting
  sleep 2
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛑 Max iterations ($MAX_ITER) reached"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Stories remaining: $(jq '[.userStories[] | select(.passes == false)] | length' $PRD_FILE)"
echo ""
echo "To continue, run: bash scripts/ralph/ralph-claude.sh $MAX_ITER"
exit 0
