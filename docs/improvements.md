# Improvements
- End to end tests
- Set limits for who can change settings
- Remove remaining print statements and replace with logging
- Redis integration
- Add game teaching you how to code?
- Add more games
- Add twitch game API integration
- Add steam game stats API integration


# Analytics
We should track current users of steam games every hour.
This should add to the DB with a timestamp. We also want to make sure 
if the app crashes that it doesn't do it again immediately for the same time frame. It should only happen once an hour and be done like a job?
Games should be saved to the DB under table games