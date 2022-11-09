# Social Network Parsing Bot
Telegram bot that downloads media files from social networks. The bot can download videos from TikTok and Instagram, and audio tracks from Youtube videos. You need to provide a video URL and the bot will send you a media file in response.

## Using the bot
- Go to http://t.me/social_network_parsing_bot and start a chat with the bot
- Send the video URL to the bot from one of the supported social networks
- After a while, the bot will send you the requested file

## Your own bot
If you create your own bot, you can view overall statistics info, with `/get_stats` command

### Creating a bot
- Install docker for your system: https://docs.docker.com/get-docker/
- Start docker service
- Create a new bot in BotFather using /newbot command
- Get API token
- Find out your user id using a bot https://t.me/userinfobot
- Execute these commands:
```
mkdir social_network_parsing
cd social_network_parsing
echo TELEGRAM_API_TOKEN={YOUR_TELEGRAM_API_TOKEN} > .env
echo INSTAGRAM_USERNAME={YOUR_INSTAGRAM_USERNAME} >> .env
echo INSTAGRAM_PASSWORD={YOUR_INSTAGRAM_PASSWORD} >> .env
echo ADMIN_ID={YOUR_USER_ID_IN_TELEGRAM} >> .env
sudo docker run --env-file .env mikhailsinyakov/social_network_parsing
``` 
