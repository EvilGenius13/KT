# KT
![Dev Build](https://github.com/EvilGenius13/KT/actions/workflows/ci.yml/badge.svg)
![Release Build](https://github.com/EvilGenius13/KT/actions/workflows/cd.yml/badge.svg)

KT is a multipurpose discord bot.

## Features
- Voice responses for players joining channel, scheduled messages, and more.
- A server wide wishlist for steam games. Add games to the wishlist and see details about them.
- Custom commands

## Commands (Replace with docs link)
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
- Ephemeral Messages
  - Change setting messages to be ephemeral.
- VoiceEvents
- SteamCommands
  - Steam watchlist buttons need to update on add/remove
  - Find a way to announce if a game is on sale
  - Need to finish caching wishlist with update when game added or removed
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
- Do we move caching to something like redis or memcache? (currently using in memory cache)
- XP System and leveling
- Docsify
- End to end tests

### Bugs
- VoiceEvents
  - Voice sometimes loads super speedy

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/jfaigan)
