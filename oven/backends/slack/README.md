# Slack Backend

## 🔔 Slack Bot Integration for Notifications

This project includes a Slack bot backend to send notifications (e.g., task progress or completion) directly to your Slack workspace. This enhances real-time collaboration and visibility.

### 📌 Features

- Sends custom Slack messages like task updates or completions.
- Optionally updates messages to show real-time progress.
- Configurable via environment variables.
- Easy to integrate and maintain.

---

### 🚀 Setup Instructions

#### 1. **Create a Slack App**

- Visit [https://api.slack.com/apps](https://api.slack.com/apps)
- Click **"Create New App"** → Choose **"From scratch"**
- Name your app and select your Slack workspace.

#### 2. **Enable Bot Features**

- Go to **OAuth & Permissions** in the left sidebar.
- Under **Bot Token Scopes**, add:
  - `chat:write`
  - `chat:write.public` (optional for wider scope)
- Click **"Install App to Workspace"**
- Copy the **Bot User OAuth Token** (`xoxb-...`)

---

### 🛠️ Environment Variables

Create a `.env` file in your project root and add the following:

```env
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_CHANNEL_ID=your-channel-id-here
