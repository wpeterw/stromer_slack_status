Stromer Slack status

Update your Slack status with data from your Stromer bike.

Usage:

Create a config.json file in this format:

{

    "username": "<stromer_username>",

    "password": "<stromer_password>",
    
    "client_id": "<stromer_api_client_id>",
    
    "client_secret": ">stromer_api_client_secret",
    
    "slack_api_token": "<slack_api_legacy_token",
    
    "slack_user": "<slack_user_id>"
}

Google for the stromer api client_id and client_secret.
Slack api token: https://api.slack.com/custom-integrations/legacy-tokens

Create a cron-job to run the script