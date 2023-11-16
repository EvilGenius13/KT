# KT
![Dev Build](https://github.com/EvilGenius13/KT/actions/workflows/ci.yml/badge.svg)
![Release Build](https://github.com/EvilGenius13/KT/actions/workflows/cd.yml/badge.svg)

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
- Music Commands
  - `*dj` - See how to use the music bot
  - `*play <youtubeURL>` - Plays a song
  - `*pause` - Paused the current song
  - `*resume` - Resumes the current song
  - `*stop` - Stops the music bot


### ToDo
- TODO: voice events timing needs to move to DB
- TODO: Steam needs to move to DB
- Ephemeral Messages
  - Add ephemeral messages to all commands
- Scheduled Events
  - Have KT create events at a set time
- VoiceEvents
  - Add more voice events
  - Add more voice responses
  - Set up recurring time states
  - Allow timezone to be set
- SteamCommands
- TextCommands
  - Add More Text Commands
- MusicEvents
  - Add text response when next song starts.
  - Add queue command to see what songs are in queue.
- Add Shop / Site(TWS)
  - Add currency
  - Add shop items
  - Add shop commands
- Add mod mail
  - Add mod mail commands
  - Add mod mail events
- OpenAI
  - Add OpenAI assistant using context about TWS
### Improvements
- Set limits for who can change settings
- Logging
- Spans and timing for functions

### Bugs
- VoiceEvents
  - Voice sometimes loads super speedy

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/jfaigan)
