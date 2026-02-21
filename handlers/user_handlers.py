import logging
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.force_join import is_user_joined
from utils.helpers import get_join_channels_keyboard
from database import Database
from config import ADMIN_ID, FORCE_CHANNEL_1, FORCE_CHANNEL_2, STORAGE_CHANNEL_ID

logger = logging.getLogger(__name__)
db = Database()

@Client.on_message(filters.private & ~filters.user(ADMIN_ID))
async def user_start_handler(client: Client, message: Message):
    """Handle messages from regular users"""
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
    
    # Regular message from user
    await message.reply_text(
        "👋 Welcome to the File Sharing Bot!\n\n"
        "Send me a file deep link to access shared content."
    )
