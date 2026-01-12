#!/bin/bash
# Sync markdown PRD to prd.json while preserving completed work
#
# Usage: bash scripts/ralph/sync-prd.sh

set -e

PRD_MARKDOWN="tasks/prd-voice-dictation-app.md"
PRD_JSON="prd.json"
TEMP_JSON="/tmp/prd-new-stories.json"

echo "🔄 Syncing PRD to prd.json..."
echo ""

# Check files exist
if [ ! -f "$PRD_MARKDOWN" ]; then
    echo "❌ Error: $PRD_MARKDOWN not found"
    exit 1
fi

if [ ! -f "$PRD_JSON" ]; then
    echo "❌ Error: $PRD_JSON not found"
    exit 1
fi

# Backup existing prd.json
cp "$PRD_JSON" "${PRD_JSON}.backup"
echo "✓ Backed up prd.json to ${PRD_JSON}.backup"

# Parse markdown PRD into temporary JSON
echo "📖 Parsing markdown PRD..."
python3 scripts/ralph/parse-prd.py "$PRD_MARKDOWN" > "$TEMP_JSON"

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to parse PRD markdown"
    exit 1
fi

echo "✓ Parsed $(jq '.userStories | length' $TEMP_JSON) stories from markdown"
echo ""

# Show what's being added/updated
echo "📊 Changes:"
echo ""

# Count existing completed stories
COMPLETED=$(jq '[.userStories[] | select(.passes == true)] | length' "$PRD_JSON")
echo "  Completed stories (will be preserved): $COMPLETED"

# Count new stories
NEW_STORIES=$(jq --slurpfile existing "$PRD_JSON" '[.userStories[] | select(.id as $id | $existing[0].userStories | map(.id) | contains([$id]) | not)] | length' "$TEMP_JSON")
echo "  New stories (will be added): $NEW_STORIES"

# Count incomplete existing stories
INCOMPLETE=$(jq '[.userStories[] | select(.passes == false)] | length' "$PRD_JSON")
echo "  Incomplete stories (may be updated): $INCOMPLETE"

echo ""
read -p "Continue with sync? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Sync cancelled"
    rm "$TEMP_JSON"
    rm "${PRD_JSON}.backup"
    exit 0
fi

# Merge stories
echo "🔀 Merging stories..."
cat "$PRD_JSON" | python3 scripts/ralph/merge-stories.py "$TEMP_JSON" > "${PRD_JSON}.new"

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to merge stories"
    rm "$TEMP_JSON"
    exit 1
fi

# Replace prd.json
mv "${PRD_JSON}.new" "$PRD_JSON"
rm "$TEMP_JSON"

echo "✅ Sync complete!"
echo ""
echo "Summary:"
jq -r '"  Total stories: " + (.userStories | length | tostring) + "\n  Completed: " + ([.userStories[] | select(.passes == true)] | length | tostring) + "\n  In progress: " + ([.userStories[] | select(.passes == false and .scope == "current")] | length | tostring) + "\n  Backlog: " + ([.userStories[] | select(.scope == "backlog")] | length | tostring)' "$PRD_JSON"

echo ""
echo "💡 Tip: Review changes with: git diff prd.json"
echo "    Then run Ralph: bash scripts/ralph/ralph-claude.sh"
