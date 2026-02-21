import logging
from pyrogram import Client
from config import FORCE_CHANNEL_1, FORCE_CHANNEL_2, ADMIN_ID
from utils.helpers import get_join_channels_keyboard
from database import Database

logger = logging.getLogger(__name__)
db = Database()

async def is_user_joined(client: Client, user_id: int) -> bool:
    """Check if user is a member of both force join channels"""
    if user_id == ADMIN_ID:
        return True  # Admin bypasses force join
    
    try:
        # Check channel 1
        member1 = await client.get_chat_member(FORCE_CHANNEL_1, user_id)
        if member1.status not in ["member", "administrator", "creator"]:
            return False
        
        # Check channel 2
        member2 = await client.get_chat_member(FORCE_CHANNEL_2, user_id)
        if member2.status not in ["member", "administrator", "creator"]:
            return False
            
        return True
    except Exception as e:
        logger.error(f"Error checking membership for user {user_id}: {str(e)}")
        return False
