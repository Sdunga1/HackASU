#!/bin/bash

# Script to help generate commits for demo tickets
# Usage: ./scripts/generate_commits.sh SCRUM-XXX "Commit message"

TICKET_ID=$1
COMMIT_MESSAGE=$2
COMMIT_DATE=${3:-$(date +"%Y-%m-%d %H:%M:%S")}

if [ -z "$TICKET_ID" ] || [ -z "$COMMIT_MESSAGE" ]; then
    echo "Usage: $0 SCRUM-XXX 'Commit message' [YYYY-MM-DD HH:MM:SS]"
    echo "Example: $0 SCRUM-6 'Add MFA implementation' '2025-11-10 09:00:00'"
    exit 1
fi

# Format commit message with ticket ID
FULL_MESSAGE="${TICKET_ID}: ${COMMIT_MESSAGE}"

# Create commit with optional date
if [ -n "$COMMIT_DATE" ]; then
    GIT_AUTHOR_DATE="$COMMIT_DATE" GIT_COMMITTER_DATE="$COMMIT_DATE" git commit -m "$FULL_MESSAGE"
else
    git commit -m "$FULL_MESSAGE"
fi

echo "✅ Created commit: $FULL_MESSAGE"
echo "   Date: ${COMMIT_DATE:-$(date +"%Y-%m-%d %H:%M:%S")}"

