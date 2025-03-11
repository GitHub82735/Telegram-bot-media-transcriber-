# Telegram Media Transcriber Bot

A Telegram bot that provides advanced audio and video transcription services with multi-language support and robust file processing capabilities.

## Features

- Transcribes audio from voice messages, audio files, videos, and video notes
- Supports multiple languages for transcription
- Handles various file formats (MP3, MP4, MOV, etc.)
- User-specific language preferences saved between sessions
- Clean, formatted transcription output

## Technologies

- Python 3.10+
- aiogram 3.18.0+ for Telegram Bot API
- SpeechRecognition for audio transcription
- Flask for keep-alive functionality
- Google Translate for language support

## Setup and Deployment

1. Clone this repository
2. Set up environment variables:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from BotFather
3. Install dependencies using Poetry:
   ```
   poetry install
   ```
4. Run the bot:
   ```
   poetry run python main.py
   ```

## Deployment on Render

This bot is configured for deployment on Render. The build command will automatically install dependencies using Poetry.

## License

MIT