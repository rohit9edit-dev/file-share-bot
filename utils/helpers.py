import uuid
import logging
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)

def generate_unique_key():
    """Generate a unique key for file identification"""
    return str(uuid.uuid4()).replace("-", "")[:16]

def create_deep_link(bot_username, unique_key):
    """Create a deep link for file access"""
    return f"https://t.me/{bot_username}?start=FILE_{unique_key}"

def get_unique_key_from_start_param(start_param):
    """Extract unique key from start parameter"""
    if start_param.startswith("FILE_"):
        return start_param[5:]
    return None

def get_join_channels_keyboard(force_channel_1, force_channel_2):
    """Create inline keyboard for force join channels"""
    buttons = []
    
    # Add channel 1 button
    if force_channel_1.startswith("@"):
        buttons.append([InlineKeyboardButton("Join Channel 1", url=f"https://t.me/{force_channel_1[1:]}")])
    else:
        buttons.append([InlineKeyboardButton("Join Channel 1", url=f"https://t.me/c/{force_channel_1}")])
    
    # Add channel 2 button
    if force_channel_2.startswith("@"):
        buttons.append([InlineKeyboardButton("Join Channel 2", url=f"https://t.me/{force_channel_2[1:]}")])
    else:
        buttons.append([InlineKeyboardButton("Join Channel 2", url=f"https://t.me/c/{force_channel_2}")])
    
    # Add try again button
    buttons.append([InlineKeyboardButton("Try Again", callback_data="check_membership")])
    
    return InlineKeyboardMarkup(buttons)
