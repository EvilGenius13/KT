# Commands
KT comes with a myriad of commands. They are split by category below. Most commands use the prefix `*` unless explicitly stated.

## Register & Settings
When you first invite the bot to your server, you need to register your server with KT. 

- `*register` - Registers your server with KT 

!> The only information used in registration is the server ID and name


- `*toggle_voice_settings`
There are three toggles and one dropdown:
  - Voice Greeting (On/Off) - When a user joins a voice channel, KT will greet them.
  - Checkin (On/Off) - KT will check in with users in a voice channel every two hours and ask if they should take a break.
  - Recurring (On/Off) - KT will check in with users in a voice channel at a specified time every day and ask if they should take a break.
  - Timezone (EST/PST/UTC) - The timezone KT should use for recurring and bi-hourly checkins.

- `*set_scheduled_break` - Sets the time for recurring checkins. Takes a time in the format `HH:MM` (24 hour time). 
  - For example, `*set_scheduled_break 18:00` would set the recurring checkin to 6:00 PM.


## Text Commands
- `*hello` - Says hello to the user who sent the command

## Music Commands
- `*dj` - Explains how to use the music bot.
- `*play <youtubeURL>` - Plays a song
  - Example: `*play https://www.youtube.com/watch?v=yEOra-A-mFs`
  - If more than one song is asked to be played, it will be added to the queue.
- `*pause` - Paused the current song
- `*resume` - Resumes the current song
- `*stop` - Stops the music bot and clears the queue

## Steam Commands
Steam commands have more embedded functionality. The main two commands are `*steam_fetch` and `*watchlist`.
Once you have fetched a game, it will give you basic info such as the game name, description, price, and discount %. Two buttons will show up under the game info. One to add the game to your watchlist, and one to visit the store page. If you click on the watchlist button, it will add the game to your watchlist. You can view your watchlist by typing `*watchlist`. You can remove a game from your watchlist by clicking the `Remove` button next to the game.

- Steam Commands
  - `*steam_fetch <appid>` - Fetches steam game info
    - Example: `*steam_fetch 361420` will fetch info for Astroneer
  - `*watchlist` - Lists all games on watchlist