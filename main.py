import os
import asyncio
import json
import speech_recognition as sr
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, 
    InlineKeyboardButton, FSInputFile
)
from pydub import AudioSegment
from googletrans import Translator
import logging
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the bot token and remove any whitespace
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()

# Validate token
if not TOKEN:
    logger.error("No Telegram bot token provided. Please set the TELEGRAM_BOT_TOKEN environment variable.")

# Allowed file formats and size limit
ALLOWED_FORMATS = ["mp4", "mp3", "mov"]
MAX_FILE_SIZE_MB = 624  # File size limit in MB
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024  # Convert MB to bytes

# Supported languages
LANGUAGES = {
    "en": "English",
    "so": "Soomaali",
    "ar": "عربي (Arabic)",
    "fr": "Français (French)",
    "es": "Español (Spanish)",
    "de": "Deutsch (German)",
    "it": "Italiano (Italian)",
    "tr": "Türkçe (Turkish)",
    "ru": "Русский (Russian)",
    "hi": "हिन्दी (Hindi)"
}

# File path for storing user preferences
USER_PREFERENCES_FILE = "user_preferences.json"

# Store user's preferred language
user_languages = {}

def save_user_preferences():
    """Save user language preferences to a JSON file."""
    try:
        # Convert user IDs (which are integers) to strings for JSON serialization
        serializable_preferences = {str(user_id): lang for user_id, lang in user_languages.items()}
        with open(USER_PREFERENCES_FILE, 'w') as f:
            json.dump(serializable_preferences, f)
        logger.info("User preferences saved successfully")
    except Exception as e:
        logger.error(f"Error saving user preferences: {e}")

def load_user_preferences():
    """Load user language preferences from a JSON file."""
    global user_languages
    try:
        if os.path.exists(USER_PREFERENCES_FILE):
            with open(USER_PREFERENCES_FILE, 'r') as f:
                # Convert string keys back to integers for user IDs
                loaded_preferences = json.load(f)
                user_languages = {int(user_id): lang for user_id, lang in loaded_preferences.items()}
            logger.info(f"Loaded preferences for {len(user_languages)} users")
        else:
            logger.info("No saved preferences found, starting with empty preferences")
    except Exception as e:
        logger.error(f"Error loading user preferences: {e}")
        # Continue with empty preferences if file is corrupted
        user_languages = {}

def create_language_keyboard():
    """Create an inline keyboard with language options."""
    buttons = []
    for code, name in LANGUAGES.items():
        buttons.append([InlineKeyboardButton(text=name, callback_data=f"lang_{code}")])
    
    # Create keyboard with buttons in rows of 2
    keyboard_rows = []
    for i in range(0, len(buttons), 2):
        row = buttons[i:i+2]
        keyboard_rows.extend([button[0] for button in row])  # Flatten the row
        if len(keyboard_rows) == 2 or i+2 >= len(buttons):  # Row is full or last items
            buttons.append(keyboard_rows)
            keyboard_rows = []
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def convert_to_wav(file_path):
    """Convert MP4/MOV/MP3 to WAV for transcription."""
    try:
        audio_path = file_path.rsplit(".", 1)[0] + ".wav"
        audio = AudioSegment.from_file(file_path)
        audio.export(audio_path, format="wav")
        return audio_path
    except Exception as e:
        logger.error(f"Error converting audio: {e}")
        raise

async def transcribe_audio(file_path, language="en"):
    """Transcribe audio using Google Speech Recognition."""
    recognizer = sr.Recognizer()

    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio, language=language)
        return text
    except sr.UnknownValueError:
        logger.info("No speech detected in audio")
        return ""  # Return empty string instead of an error message
    except sr.RequestError as e:
        logger.error(f"Speech recognition request error: {e}")
        raise  # Let the caller handle this error with a generic message
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise  # Let the caller handle this error with a generic message

async def check_file_size(message: Message, file_id: str, bot: Bot):
    """Check if the file size is within the allowed limit."""
    file_info = await bot.get_file(file_id)
    if file_info.file_size > MAX_FILE_SIZE_BYTES:
        await message.reply(
            f"The file is too large. Maximum allowed size is {MAX_FILE_SIZE_MB}MB. "
            f"Please send a smaller file."
        )
        return False
    return True

async def process_file(message: Message, file_id: str, file_name: str, bot: Bot):
    """Download the file, convert it if needed, and transcribe it."""
    # Get the user's preferred language or default to English
    user_id = message.from_user.id
    language = user_languages.get(user_id, "en")
    
    # Check file extension
    file_ext = file_name.split(".")[-1].lower() if "." in file_name else ""
    if file_ext not in ALLOWED_FORMATS:
        await message.reply(
            f"Unsupported file format. Please send a file in one of these formats: {', '.join(ALLOWED_FORMATS)}."
        )
        return
    
    # Check file size
    if not await check_file_size(message, file_id, bot):
        return
    
    # Inform user that processing has started (minimal message)
    processing_msg = await message.reply("Processing...")
    
    # Initialize paths to None
    file_path = None
    audio_path = None
    
    try:
        # Download the file
        file = await bot.get_file(file_id)
        os.makedirs("downloads", exist_ok=True)
        file_path = f"downloads/{file_id}_{file_name}"
        await bot.download_file(file.file_path, destination=file_path)
        
        # Convert to WAV if needed
        if file_ext in ALLOWED_FORMATS:
            audio_path = convert_to_wav(file_path)
        else:
            audio_path = file_path
        
        # Transcribe the audio
        transcription = await transcribe_audio(audio_path, language=language)
        
        # If no speech was detected, show a specific message
        if not transcription:
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=processing_msg.message_id,
                text="No speech detected."
            )
        else:
            # Send the clean transcription text without any additional phrases or markers
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=processing_msg.message_id,
                text=f"{transcription}"
            )
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=processing_msg.message_id,
            text="Could not transcribe audio."
        )
    finally:
        # Clean up files
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            if audio_path and os.path.exists(audio_path) and audio_path != file_path:
                os.remove(audio_path)
        except Exception as e:
            logger.error(f"Error cleaning up files: {e}")

async def main():
    # Load user preferences from file
    load_user_preferences()
    
    # Create bot and dispatcher instances
    from aiogram.client.default import DefaultBotProperties
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    # Register the handlers
    dp.message(CommandStart())(start_command)
    dp.message(Command("language"))(language_command)
    dp.message(Command("settings"))(settings_command)
    dp.callback_query(F.data.startswith("lang_"))(process_language_callback)
    dp.message(F.document)(handle_document)
    dp.message(F.audio)(handle_audio)
    dp.message(F.video)(handle_video)
    dp.message(F.voice)(handle_voice)
    dp.message(F.video_note)(handle_video_note)
    dp.message(~F.media_group_id)(handle_text)
    
    # Set up translator
    global translator
    translator = Translator()
    
    logger.info("Starting Transcription Bot")
    # Create downloads directory if it doesn't exist
    os.makedirs("downloads", exist_ok=True)
    
    # Start the bot
    await dp.start_polling(bot)

async def start_command(message: Message):
    """Welcome the user when they start the bot."""
    await message.reply(
        f"Send me audio/video files to transcribe.\n\n"
        f"Commands:\n"
        f"/language - Set language\n"
        f"/settings - View settings"
    )

async def language_command(message: Message):
    """Display available languages and allow selection."""
    keyboard = create_language_keyboard()
    await message.reply(
        "Select language:",
        reply_markup=keyboard
    )

async def settings_command(message: Message):
    """Display current user settings."""
    user_id = message.from_user.id
    
    # Get current language or default
    current_language_code = user_languages.get(user_id, "en")
    current_language_name = LANGUAGES.get(current_language_code, "English")
    
    # Create settings message with current preferences
    settings_message = f"Current language: {current_language_name}"
    
    await message.reply(settings_message)

async def process_language_callback(callback: CallbackQuery):
    """Handle language selection from inline keyboard."""
    language_code = callback.data.split('_')[1]
    user_id = callback.from_user.id
    
    # Save user's language preference
    user_languages[user_id] = language_code
    
    # Save preferences to file
    save_user_preferences()
    
    # Send confirmation to user
    await callback.answer()
    await callback.message.reply(
        f"Language set to {LANGUAGES[language_code]}."
    )

async def handle_document(message: Message, bot: Bot):
    """Handle files sent as documents."""
    if message.document and hasattr(message.document, 'file_name'):
        await process_file(message, message.document.file_id, message.document.file_name, bot)
    else:
        await message.reply("Please send a valid document file.")

async def handle_audio(message: Message, bot: Bot):
    """Handle audio files."""
    if message.audio and hasattr(message.audio, 'file_id'):
        file_name = message.audio.file_name or f"audio_{message.message_id}.mp3"
        await process_file(message, message.audio.file_id, file_name, bot)
    else:
        await message.reply("Please send a valid audio file.")

async def handle_video(message: Message, bot: Bot):
    """Handle video files."""
    if message.video and hasattr(message.video, 'file_id'):
        file_name = message.video.file_name or f"video_{message.message_id}.mp4"
        await process_file(message, message.video.file_id, file_name, bot)
    else:
        await message.reply("Please send a valid video file.")

async def handle_voice(message: Message, bot: Bot):
    """Handle voice messages."""
    if message.voice and hasattr(message.voice, 'file_id'):
        # Generate a filename for the voice message
        file_name = f"voice_message_{message.message_id}.ogg"
        await process_file(message, message.voice.file_id, file_name, bot)
    else:
        await message.reply("Please send a valid voice message.")

async def handle_video_note(message: Message, bot: Bot):
    """Handle video notes (round videos)."""
    if message.video_note and hasattr(message.video_note, 'file_id'):
        # Generate a filename for the video note
        file_name = f"video_note_{message.message_id}.mp4"
        await process_file(message, message.video_note.file_id, file_name, bot)
    else:
        await message.reply("Please send a valid video note.")

async def handle_text(message: Message):
    """Handle text messages."""
    # Only respond to pure text messages, not media captions
    if not message.media_group_id and message.text and not message.text.startswith('/'):
        await message.reply(
            "Please send me an audio or video file to transcribe.\n\n"
            "You can use /language to change the transcription language or "
            "/settings to view your current preferences."
        )

if __name__ == "__main__":
    # Import and start the keep-alive server
    from keep_alive import keep_alive
    keep_alive()
    
    # Run the main function
    asyncio.run(main())
