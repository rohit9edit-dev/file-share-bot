import logging
import os
from pyrogram import Client
from config import API_ID, API_HASH, BOT_TOKEN

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Initialize the bot
app = Client(
    "file_share_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Import handlers (must be done after app is initialized)
from handlers import admin_handlers, user_handlers, callback_handlers

if __name__ == "__main__":
    logging.info("Starting the bot...")
    
    # Register handlers
    app.add_handler(admin_handlers.start_handler)
    app.add_handler(admin_handlers.broadcast_command)
    app.add_handler(admin_handlers.admin_file_handler)
    app.add_handler(admin_handlers.upload_file_callback)
    app.add_handler(admin_handlers.start_broadcast_callback)
    app.add_handler(admin_handlers.admin_help_callback)
    app.add_handler(user_handlers.user_start_handler)
    app.add_handler(callback_handlers.check_membership_callback)
    
    # Start the bot
    app.run()
    logging.info("Bot stopped.")
