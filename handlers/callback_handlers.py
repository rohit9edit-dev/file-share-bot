import logging
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from utils.force_join import is_user_joined
from utils.helpers import get_join_channels_keyboard
from database import Database
from config import ADMIN_ID, FORCE_CHANNEL_1, FORCE_CHANNEL_2, STORAGE_CHANNEL_ID

logger = logging.getLogger(__name__)
db = Database()

@Client.on_callback_query(filters.regex("^check_membership$"))
async def check_membership_callback(client: Client, callback_query: CallbackQuery):
    """Handle membership check callback"""
    if await is_user_joined(client, callback_query.from_user.id):
        # User has joined, get the file ID from the message
        message = callback_query.message
        if "FILE_" in message.text:
            # Extract unique key from the message
            start_param = None
            for entity in message.entities:
                if entity.type == "url":
                    url = message.text[entity.offset:entity.offset + entity.length]
                    if "start=FILE_" in url:
                        start_param = url.split("start=FILE_")[1]
                        break
            
            if start_param:
                message_id = db.get_file_message_id(start_param)
                if message_id:
                    try:
                        await client.copy_message(
                            chat_id=callback_query.from_user.id,
                            from_chat_id=STORAGE_CHANNEL_ID,
                            message_id=message_id,
                            reply_to_message_id=callback_query.message.id
                        )
                        await callback_query.answer("✅ File sent successfully!")
                    except Exception as e:
                        logger.error(f"Error sending file: {str(e)}")
                        await callback_query.answer("❌ Error retrieving the file. Please try again later.")
                    return
        
        # If we get here, we couldn't find the file ID
        await callback_query.answer("❌ Could not find the file. Please try the link again.")
    else:
        # User still hasn't joined
        await callback_query.answer("❌ You still need to join the channels!", show_alert=True)
        await callback_query.message.edit_reply_markup(
            reply_markup=get_join_channels_keyboard(FORCE_CHANNEL_1, FORCE_CHANNEL_2)
        )
