# Slack Bot Setup

Current version of the Slack bot only use webhook to send message.

You can find the most of the actions needed [here](https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks).

## Step 1. Create a Slack Application and Develop It to Your Workspace

Create a Slack application here: [`https://api.slack.com/apps?new_app=1`](https://api.slack.com/apps?new_app=1).

## Step 2. Enable the Webhook and Get the Webhook URL

After creating the application, you will be redirected to the application configuration page, where you can modify the application settings. Here, we need to enable the webhook and get the webhook URL.

1. Find the `Features` > `Incoming Webhooks` section on the left sidebar and click it. Then you will see a section titled "Activate Incoming Webhooks".
2. There will be a toggle button on the right and it will be `Off` by default. **Turn it on**. After that, section "Webhook URLs for Your Workspace" will be shown.
3. Click **"Add New Webhook to Workspace"** button on the bottom, select the the channel you want the bot to send messages to. (You'd better to create a **private channel** or maybe **yourself** so that no one else will be spammed. ☺️)
   - Personally I would prefer to integrate the bot into direct messages with myself, so that I can still delete the messages even I am not the admin.
4. You will see a new "Webhook URL" item appeared. Click **Copy** button to get the hook URL. **This URL should be filled into the "hook" field in the configuration file.**
