#!/bin/bash

# Test script to process SRS and generate sprints
# This simulates what the MCP tool does

API_URL="http://localhost:8000"
SRS_CONTENT=$(cat <<'EOF'
# Software Requirements Specification

## DevAI Manager - Notification System

**Project:** DevAI Manager  
**Version:** 1.0

---

## Overview

Add a notification system to DevAI Manager that alerts users about project events, anomalies, and updates from GitHub and Jira integrations.

---

## Functional Requirements

### FR-1: User Notification Preferences
Users can configure notification preferences:
- Enable/disable notification types
- Set notification frequency (real-time, daily, weekly)
- Choose notification channels (in-app, email)

### FR-2: Anomaly Detection Alerts
System sends alerts when anomalies are detected:
- Zero commits on in-progress tickets (3+ days)
- PRs merged without linked Jira tickets
- High commit activity on closed tickets
- Tickets in review without open PRs

### FR-3: Sprint Notifications
System sends notifications for sprint events:
- Sprint start and end dates
- 24-hour deadline warnings
- Progress updates and milestones

### FR-4: Issue Status Notifications
System sends notifications for issue changes:
- Status changes (To Do → In Progress → Done)
- New comments and assignments
- High-priority issue alerts
- Overdue issue warnings

### FR-5: Notification Center
Users can view and manage notifications:
- View all notifications in one place
- Mark notifications as read/unread
- Filter by type and priority
- Search notifications

---

## User Stories

### US-1: Configure Notification Settings
As a user, I want to configure my notification preferences so I only receive relevant alerts.

### US-2: Receive Anomaly Alerts
As a project manager, I want to receive alerts when anomalies are detected so I can address issues quickly.

### US-3: Sprint Start Notification
As a team member, I want to be notified when a sprint starts so I know when to begin work.

### US-4: Sprint Deadline Warning
As a project manager, I want to be notified 24 hours before sprint end so I can assess progress.

### US-5: Issue Status Change Notification
As an assignee, I want to be notified when my issue status changes so I know the current state.

### US-6: High-Priority Issue Alert
As a team member, I want to be notified when high-priority issues are created so I can respond quickly.

### US-7: View Notification Center
As a user, I want to view all my notifications in one place so I can stay updated.

### US-8: Mark Notifications as Read
As a user, I want to mark notifications as read so I can track what I've seen.

---

## Technical Requirements

### TR-1: GitHub Integration
- Integrate with GitHub MCP server
- Listen for GitHub webhook events
- Fetch commit and PR data

### TR-2: Jira Integration
- Integrate with Jira MCP server
- Listen for Jira webhook events
- Fetch issue and sprint data

### TR-3: Real-Time Delivery
- Notifications delivered within 5 seconds
- Support WebSocket for real-time updates
- Handle 1000+ concurrent users

---

## Success Criteria

- 90% of users configure notification preferences
- Notifications delivered within 5 seconds
- 95% of users find notifications useful
- System handles 1000+ concurrent users

---

## Timeline

**Phase 1 (Week 1-2):** User preferences and basic notification center  
**Phase 2 (Week 3-4):** GitHub and Jira integrations  
**Phase 3 (Week 5-6):** Anomaly detection and sprint notifications  
**Phase 4 (Week 7-8):** Testing and polish

---

**End of Document**
EOF
)

echo "Testing SRS processing..."
echo "Sending SRS content to backend..."

curl -X POST "${API_URL}/api/srs/process" \
  -H "Content-Type: application/json" \
  -d "{
    \"content\": $(echo "$SRS_CONTENT" | jq -Rs .),
    \"document_name\": \"Notification System SRS\",
    \"document_url\": \"https://docs.google.com/document/d/test\"
  }" | jq .

echo ""
echo "Fetching generated sprints..."
curl -s "${API_URL}/api/srs/sprints" | jq .

