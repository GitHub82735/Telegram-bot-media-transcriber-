# Telegram Media Transcriber Bot (@anyTranscribeBot)

A Telegram bot that provides advanced audio and video transcription services with multi-language support and robust file processing capabilities.

## Features

- Transcribes audio from voice messages, audio files, videos, and video notes
- Supports multiple languages for transcription (10+ languages including English, Somali, Arabic, etc.)
- Handles various file formats (MP3, MP4, MOV, etc.)
- User-specific language preferences saved between sessions
- Clean, formatted transcription output
- Automatic file cleanup to maintain server storage
- Keep-alive mechanism to ensure 24/7 availability

## How to Use the Bot

1. **Start the bot**: Send `/start` to begin
2. **Set your language**: Use `/language` to select your preferred transcription language
3. **Send media**: Send any audio/video file, voice message, or video note
4. **Get transcription**: The bot will process your media and return the transcribed text
5. **View settings**: Use `/settings` to see your current preferences

## Supported Languages

- English (en)
- Somali (so)
- Arabic (ar)
- French (fr)
- Spanish (es)
- German (de)
- Italian (it)
- Turkish (tr)
- Russian (ru)
- Hindi (hi)

## Technologies

- Python 3.10+
- aiogram 3.18.0+ for Telegram Bot API
- SpeechRecognition for audio transcription
- pydub for audio processing
- Flask for keep-alive functionality
- Google Translate for language support
- FFmpeg for media conversion

## Local Setup and Development

1. Clone this repository
2. Set up environment variables:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from BotFather
3. Install dependencies using Poetry:
   ```
   poetry install
   ```
4. Ensure FFmpeg is installed on your system
5. Run the bot:
   ```
   poetry run python main.py
   ```

## Deployment on Render

This bot is configured for deployment on Render with the included `render.yaml` file:

1. Connect your GitHub repository to Render
2. Add the `TELEGRAM_BOT_TOKEN` environment variable in the Render dashboard
3. Deploy the service - Render will automatically:
   - Install Python 3.10.8
   - Install dependencies using Poetry
   - Run the bot with `python main.py`

## File Structure

- `main.py`: Core bot implementation with handlers and transcription logic
- `keep_alive.py`: Web server for maintaining uptime
- `pyproject.toml`: Poetry dependencies configuration
- `render.yaml`: Render deployment configuration
- `user_preferences.json`: Stores user language preferences

## License

MIT