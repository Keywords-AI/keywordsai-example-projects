# Webhook + Slack Alert for Rate / Budget Limit

This example demonstrates how to configure a Slack webhook notification that triggers when a user exceeds their rate limit or budget limit in Keywords AI.

The setup is UI-based and does not require any code.

## Overview

When a user reaches a configured rate or budget limit:

- API requests are blocked
- A `402 (exceeded budget limit)` error is returned
- A Slack notification is sent via webhook

## Prerequisites

- A Keywords AI project
- A user with a rate limit or budget limit configured
- A Slack Incoming Webhook URL  
  https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks

## Setup

### Configure Slack Notification

1. Go to **Settings → Notifications**
2. Select **Slack** as the notification type
3. Paste your Slack Incoming Webhook URL
4. Save the configuration

### Configure User Limits

1. Go to **Users**
2. Select a user
3. Set a rate limit or budget limit
4. Save the changes

### Trigger the Alert

Send requests using the user’s API key until the configured limit is exceeded.

## Expected Result

Once the limit is reached:

- Requests return a `402 (exceeded budget limit)` error
- A Slack message is sent via the configured webhook

## Notes

- This example uses UI-based configuration only
- No scripts or code are required
