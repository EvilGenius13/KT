# KT
KT is a multipurpose discord bot.

## Features
- Voice responses for players joining channel
- Break messages that can be sent to a channel at a set interval
- Custom commands

## Commands
- Regular Commands
  - `*hello` - Says hello
- Voice Commands
  - `*toggle_voice_settings` - Toggle voice responses
- Steam Commands
  - `*steam_fetch <appid>` - Fetches steam game info
  - `*watchlist` - Lists all games on watchlist

### ToDo
- Add more voice responses
- More Text Commands
- Check if voice settings are server wide or for the bot itself
- Allow timezone to be set
- Allow timers to be set
- Set up a database for storing settings
- Set limits for who can change settings

### Bugs
- `discord.errors.ClientException: Already playing audio.` When playing a sound even when nothing else is playing (Low severity)

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/jfaigan)
