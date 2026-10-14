# Trenny 

A Telegram bot that sends my workouts to [TrenDen](https://github.com/farron65/tren-den).
I copy a workout from the Strong app, paste it to the bot, and it lands in Trenden. 
No more opening the site, clicking import, pasting, and submitting.

## How it works
 
```
Telegram  ->  Trenny  ->  POST /import/strong  ->  parser  ->  saved workout
```

1. I paste a Strong workout into the chat.
2. Trenny checks the message is from me and looks like a workout.
3. It pings Trenden's `/health` endpoint. If Trenden is asleep (free hosting), it tells me and keeps pinging until it wakes up.
4. It sends the text once to `POST /import/strong` with an API key.
5. Trenden parses and saves the workout, and Trenny replies with a confirmation (name, date, exercise and set counts) or the parser's error message.

All parsing lives in the Trenden backend, so the bot is a thin relay.
 
## Setup
 
Requires Python 3.13+ (or Docker).
 
1. Create a bot with [@BotFather](https://t.me/BotFather) and copy the token.
2. Find your numeric Telegram user ID (for example with @userinfobot).
3. Copy `.env.example` to `.env` and fill in:
| Variable | Description |
   |---|---|
   | `BOT_TOKEN` | Token from BotFather |
   | `BOT_API_KEY` | Must match `BOT_API_KEY` on the Trenden backend |
   | `ALLOWED_USER_ID` | Your Telegram user ID. Everyone else is ignored |
   | `TREN_DEN_URL` | Base URL of the Trenden backend, no trailing slash |
 
The bot refuses to start if any of these are missing.
 
### Run locally
 
```
pip install -r requirements.txt
python main.py
```
 
### Run with Docker
 
```
docker build -t trenny .
docker run --rm --env-file .env trenny
```
 
If the backend runs on your machine and the bot runs in Docker, set `TREN_DEN_URL=http://host.docker.internal:8000`.
 
## Usage
 
- `/start`: check that the bot is alive.
- Paste a workout copied from Strong (Share, then Copy Workout). Messages that don't look like a workout are rejected locally, without waking the backend.

## Design notes
 
- **Long polling, not webhooks.** The bot only makes outbound connections, so it needs no public URL.
- **User-ID filter.** Handlers only accept messages from `ALLOWED_USER_ID`. Strangers get no reply at all.
- **Static API key.** The bot authenticates with an `X-API-Key` header instead of a login session, so there's no token refresh to manage. The backend compares it in constant time.
- **Wake-up loop.** Trenden's free host sleeps when idle and can take a few minutes to wake. The bot polls `/health` (10 s interval, 180 s deadline) and sends the import exactly once afterwards. It never retries the POST itself, which would risk saving a workout twice.
- **Cheap local gate.** A loose check (multi-line text with a `Set N:` line) runs before any network call, so stray messages don't wake the server. The backend parser stays the source of truth for validity.
- **Pinned dependencies.** `requirements.txt` is fully pinned so rebuilds don't pick up breaking releases.
## Limitations
 
- Strong format only.
- Timezone is hardcoded to `America/New_York` (confirmation times and, on the backend, workout times).
- Single user.
