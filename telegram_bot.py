import logging
import requests
from telegram import Update, InlineQueryResultVideo, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, InlineQueryHandler, CommandHandler, ContextTypes
import hashlib

# Bot configuration
BOT_TOKEN = "8353864491:AAED87RQDPrvG1O3wXs2C3u345c_UOYrSqQ"
CDN_SERVER = "https://transmental-wendy-divertingly.ngrok-free.dev"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def is_youtube_url(text):
    """Check if text contains YouTube URL"""
    youtube_domains = ['youtube.com', 'youtu.be']
    return any(domain in text for domain in youtube_domains)

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline queries"""
    query = update.inline_query.query
    
    logger.info(f"Received inline query: '{query}'")
    
    # Show placeholder if no query
    if not query:
        results = [
            InlineQueryResultArticle(
                id="help",
                title="📺 Paste a YouTube URL",
                description="Example: https://youtube.com/shorts/...",
                input_message_content=InputTextMessageContent(
                    message_text="Please provide a YouTube URL to download"
                )
            )
        ]
        await update.inline_query.answer(results, cache_time=0)
        return
    
    if not is_youtube_url(query):
        results = [
            InlineQueryResultArticle(
                id="invalid",
                title="❌ Invalid URL",
                description="Please provide a valid YouTube URL",
                input_message_content=InputTextMessageContent(
                    message_text="Invalid YouTube URL provided"
                )
            )
        ]
        await update.inline_query.answer(results, cache_time=0)
        return
    
    # Extract URL from query
    url = query.strip()
    
    try:
        # Request CDN server to process video
        logger.info(f"Processing video: {url}")
        response = requests.post(
            f"{CDN_SERVER}/process",
            json={"url": url, "base_url": CDN_SERVER},
            timeout=30
        )
        
        if response.status_code != 200:
            logger.error(f"CDN error: {response.text}")
            await update.inline_query.answer([])
            return
        
        data = response.json()
        video_url = data['url']
        video_id = data['video_id']
        
        logger.info(f"Video ready: {video_url}")
        
        # Create inline results with both video and article options
        results = [
            # Option 1: Direct video result
            InlineQueryResultVideo(
                id=f"{video_id}_video",
                video_url=video_url,
                mime_type="video/mp4",
                thumbnail_url=video_url,
                title="📹 Send as Video",
                description="Send the video directly"
            ),
            # Option 2: Article with buttons
            InlineQueryResultArticle(
                id=f"{video_id}_article",
                title="📋 Send with Button",
                description="Send message with video button",
                input_message_content=InputTextMessageContent(
                    message_text=f"🎬 YouTube Video Ready!\n\n🔗 {url}"
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🎥 Watch Video", url=video_url)]
                ])
            )
        ]
        
        await update.inline_query.answer(results, cache_time=0)
        
    except Exception as e:
        logger.error(f"Error processing inline query: {e}", exc_info=True)
        await update.inline_query.answer([])

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    await update.message.reply_text(
        "👋 Welcome to YouTube Downloader Bot!\n\n"
        "🎬 To use inline mode:\n"
        "1. Type @snapGobot in any chat\n"
        "2. Paste a YouTube URL\n"
        "3. Select a result to send\n\n"
        "Example: @snapGobot https://youtube.com/shorts/..."
    )
    logger.info(f"User {update.effective_user.id} started the bot")

def main():
    """Start the bot"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(InlineQueryHandler(inline_query))
    
    logger.info("Bot started. Use inline mode: @snapGobot <youtube_url>")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
