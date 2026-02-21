import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from utils.helpers import generate_unique_key, create_deep_link
from database import Database
from config import ADMIN_ID, STORAGE_CHANNEL_ID, BOT_USERNAME, FORCE_CHANNEL_1, FORCE_CHANNEL_2
from utils.broadcast import Broadcast
from utils.force_join import is_user_joined

logger = logging.getLogger(__name__)
db = Database()
broadcast = Broadcast()

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    """Handle /start command"""
    # Add user to database
    db.add_user(message.from_user.id)
    
    # Check if there's a start parameter (deep link)
    if len(message.command) > 1:
        start_param = message.command[1]
        if start_param.startswith("FILE_"):
            # This is a file deep link
            unique_key = start_param[5:]
            message_id = db.get_file_message_id(unique_key)
            
            if message_id:
                # Check force join
                if not await is_user_joined(client, message.from_user.id):
                    await message.reply_text(
                        "To access this content, you need to join our channels first.\n\n"
                        "Please join the channels below and then click 'Try Again'.",
                        reply_markup=get_join_channels_keyboard(FORCE_CHANNEL_1, FORCE_CHANNEL_2)
                    )
                    return
                
                # Send the file from storage channel
                try:
                    await client.copy_message(
                        chat_id=message.chat.id,
                        from_chat_id=STORAGE_CHANNEL_ID,
                        message_id=message_id,
                        reply_to_message_id=message.id
                    )
                    return
                except Exception as e:
                    logger.error(f"Error sending file: {str(e)}")
                    await message.reply_text("❌ Error retrieving the file. Please try again later.")
                    return
    
    # Regular /start command
    if message.from_user.id == ADMIN_ID:
        # Admin welcome message
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("📤 Upload File", callback_data="upload_file")],
                [InlineKeyboardButton("📊 Broadcast", callback_data="start_broadcast")],
                [InlineKeyboardButton("ℹ️ Help", callback_data="admin_help")]
            ]
        )
        await message.reply_text(
            "👋 Welcome, Admin!\n\n"
            "You can use the buttons below to manage the bot.",
            reply_markup=keyboard
        )
    else:
        # Regular user welcome message
        await message.reply_text(
            "👋 Welcome to the File Sharing Bot!\n\n"
            "Send me a file deep link to access shared content."
        )

@Client.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
async def broadcast_command(client: Client, message: Message):
    """Handle /broadcast command"""
    await broadcast.start_broadcast(client, message)

@Client.on_message(filters.private & filters.user(ADMIN_ID))
async def admin_file_handler(client: Client, message: Message):
    """Handle file uploads from admin"""
    # Check if this is part of a broadcast message
    if await broadcast.process_broadcast_message(client, message):
        return
    
    # Check if the message contains a file
    if not (message.photo or message.video or message.document or message.audio):
        return
    
    try:
        # Copy the file to storage channel
        copied_message = await client.copy_message(
            chat_id=STORAGE_CHANNEL_ID,
            from_chat_id=message.chat.id,
            message_id=message.id
        )
        
        # Generate unique key and save to database
        unique_key = generate_unique_key()
        db.add_file(unique_key, copied_message.id)
        
        # Create deep link
        deep_link = create_deep_link(BOT_USERNAME, unique_key)
        
        # Send success message with deep link
        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🔗 Copy Deep Link", url=deep_link)],
                [InlineKeyboardButton("📤 New File", callback_data="upload_file")]
            ]
        )
        
        await message.reply_text(
            "✅ File uploaded successfully!\n\n"
            f"🔗 Deep Link: `{deep_link}`\n\n"
            "You can share this link with users. They'll need to join the required channels to access the file.",
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        await message.reply_text(f"❌ Error uploading file: {str(e)}")

@Client.on_callback_query(filters.regex("^upload_file$") & filters.user(ADMIN_ID))
async def upload_file_callback(client: Client, callback_query):
    """Handle upload file callback"""
    await callback_query.answer()
    await callback_query.message.edit_text(
        "📤 Please send the file you want to upload.\n\n"
        "You can send any type of file: photo, video, document, audio, etc."
    )

@Client.on_callback_query(filters.regex("^start_broadcast$") & filters.user(ADMIN_ID))
async def start_broadcast_callback(client: Client, callback_query):
    """Handle start broadcast callback"""
    await callback_query.answer()
    await broadcast.start_broadcast(client, callback_query.message)

@Client.on_callback_query(filters.regex("^admin_help$") & filters.user(ADMIN_ID))
async def admin_help_callback(client: Client, callback_query):
    """Handle admin help callback"""
    await callback_query.answer()
    help_text = (
        "ℹ️ **Admin Help**\n\n"
        "1. **Upload Files**\n"
        "   - Click 'Upload File' or use the command\n"
        "   - Send the file you want to share\n"
        "   - Get a deep link to share with users\n\n"
        "2. **Broadcast Messages**\n"
        "   - Click 'Broadcast' or use /broadcast\n"
        "   - Send the message to broadcast\n"
        "   - The bot will send it to all users\n"
        "   - Rate limited to 10 messages/minute\n\n"
        "3. **Force Join Channels**\n"
        "   - Users must join both channels to access files\n"
        "   - Configured in environment variables"
    )
    await callback_query.message.edit_text(help_text, parse_mode="markdown")
