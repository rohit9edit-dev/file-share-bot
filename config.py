import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    STORAGE_CHANNEL_ID = int(os.getenv("STORAGE_CHANNEL_ID"))
    FORCE_CHANNEL_1 = os.getenv("FORCE_CHANNEL_1")
    FORCE_CHANNEL_2 = os.getenv("FORCE_CHANNEL_2")
    ADMIN_ID = int(os.getenv("ADMIN_ID"))
    BOT_USERNAME = os.getenv("BOT_USERNAME", "YourBotName")
    
    # Validate required environment variables
    required_vars = [
        "API_ID", "API_HASH", "BOT_TOKEN", 
        "STORAGE_CHANNEL_ID", "FORCE_CHANNEL_1", 
        "FORCE_CHANNEL_2", "ADMIN_ID"
    ]

    for var in required_vars:
        if not os.getenv(var):
            raise ValueError(f"Missing required environment variable: {var}")
            
    logger.info("Configuration loaded successfully")
    
except Exception as e:
    logger.critical(f"Configuration error: {str(e)}")
    raise
