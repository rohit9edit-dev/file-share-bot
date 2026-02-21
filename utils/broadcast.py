import time
import logging
from pyrogram import Client
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated
from database import Database
from config import ADMIN_ID

logger = logging.getLogger(__name__)
db = Database()

class Broadcast:
    def __init__(self):
        self.is_broadcasting = False
        self.broadcast_message = None
        self.rate_limit = 10  # messages per minute
        self.last_broadcast_time = 0
        self.progress_msg_id = None
    
    async def start_broadcast(self, client: Client, message):
        """Start the broadcast process"""
        if self.is_broadcasting:
            await message.reply_text("A broadcast is already in progress.")
            return
        
        self.is_broadcasting = True
        self.broadcast_message = None
        
        await message.reply_text(
            "Please send the message you want to broadcast.\n\n"
            "You can send any type of message: text, photo, video, document, etc."
        )
    
    async def process_broadcast_message(self, client: Client, message):
        """Process the message to be broadcasted"""
        if not self.is_broadcasting or self.broadcast_message is not None:
            return False
        
        self.broadcast_message = message
        await message.reply_text(
            "Broadcast message received. Starting broadcast to all users...\n\n"
            "This may take some time depending on the number of users."
        )
        
        await self.send_broadcast(client)
        return True
    
    async def send_broadcast(self, client: Client):
        """Send the broadcast message to all users"""
        users = db.get_all_users()
        total_users = len(users)
        successful = 0
        blocked = 0
        deactivated = 0
        flood_wait = 0
        other_errors = 0
        
        start_time = time.time()
        
        for i, user_id in enumerate(users):
            if not self.is_broadcasting:
                break
                
            try:
                # Rate limiting: 10 messages per minute
                elapsed = time.time() - start_time
                if i > 0:
                    # Calculate time since last message
                    time_since_last = time.time() - self.last_broadcast_time
                    if time_since_last < 6:  # Less than 6 seconds since last message
                        time.sleep(6 - time_since_last)
                
                # Send the message based on its type
                if self.broadcast_message.text:
                    await client.send_message(
                        user_id,
                        self.broadcast_message.text,
                        reply_markup=self.broadcast_message.reply_markup
                    )
                elif self.broadcast_message.photo:
                    await client.send_photo(
                        user_id,
                        self.broadcast_message.photo.file_id,
                        caption=self.broadcast_message.caption,
                        reply_markup=self.broadcast_message.reply_markup
                    )
                elif self.broadcast_message.video:
                    await client.send_video(
                        user_id,
                        self.broadcast_message.video.file_id,
                        caption=self.broadcast_message.caption,
                        reply_markup=self.broadcast_message.reply_markup
                    )
                elif self.broadcast_message.document:
                    await client.send_document(
                        user_id,
                        self.broadcast_message.document.file_id,
                        caption=self.broadcast_message.caption,
                        reply_markup=self.broadcast_message.reply_markup
                    )
                elif self.broadcast_message.audio:
                    await client.send_audio(
                        user_id,
                        self.broadcast_message.audio.file_id,
                        caption=self.broadcast_message.caption,
                        reply_markup=self.broadcast_message.reply_markup
                    )
                
                successful += 1
                self.last_broadcast_time = time.time()
                
                # Update progress every 10 users
                if (i + 1) % 10 == 0 or i == total_users - 1:
                    await self.update_progress(client, i + 1, total_users, successful, blocked, deactivated, flood_wait, other_errors)
            
            except FloodWait as e:
                flood_wait += 1
                logger.warning(f"FloodWait error for user {user_id}: waiting {e.value} seconds")
                time.sleep(e.value)
                # Try sending again after waiting
                try:
                    if self.broadcast_message.text:
                        await client.send_message(
                            user_id,
                            self.broadcast_message.text,
                            reply_markup=self.broadcast_message.reply_markup
                        )
                    successful += 1
                except Exception:
                    other_errors += 1
            
            except UserIsBlocked:
                blocked += 1
                db.remove_user(user_id)  # Remove blocked users
            
            except InputUserDeactivated:
                deactivated += 1
                db.remove_user(user_id)  # Remove deactivated users
            
            except Exception as e:
                other_errors += 1
                logger.error(f"Error sending broadcast to {user_id}: {str(e)}")
        
        self.is_broadcasting = False
        
        # Send final report
        await self.send_report(client, total_users, successful, blocked, deactivated, flood_wait, other_errors)
    
    async def update_progress(self, client: Client, current, total, successful, blocked, deactivated, flood_wait, other_errors):
        """Update broadcast progress"""
        progress = (current / total) * 100
        report = (
            f"📊 Broadcast Progress: {progress:.1f}%\n"
            f"📤 Total: {current}/{total}\n"
            f"✅ Successful: {successful}\n"
            f"❌ Blocked: {blocked}\n"
            f"👻 Deactivated: {deactivated}\n"
            f"⏳ FloodWait: {flood_wait}\n"
            f"⚠️ Errors: {other_errors}"
        )
        
        try:
            if self.progress_msg_id:
                # Try to edit the last progress message
                await client.edit_message_text(
                    ADMIN_ID,
                    self.progress_msg_id,
                    report
                )
            else:
                msg = await client.send_message(ADMIN_ID, report)
                self.progress_msg_id = msg.id
        except Exception as e:
            logger.error(f"Error updating broadcast progress: {str(e)}")
            try:
                msg = await client.send_message(ADMIN_ID, report)
                self.progress_msg_id = msg.id
            except Exception as e2:
                logger.error(f"Error sending new progress message: {str(e2)}")
    
    async def send_report(self, client: Client, total, successful, blocked, deactivated, flood_wait, other_errors):
        """Send final broadcast report"""
        report = (
            "✅ Broadcast Completed!\n\n"
            f"📬 Total Users: {total}\n"
            f"✅ Delivered: {successful}\n"
            f"❌ Blocked: {blocked}\n"
            f"👻 Deactivated: {deactivated}\n"
            f"⏳ FloodWait: {flood_wait}\n"
            f"⚠️ Errors: {other_errors}\n\n"
            f"📊 Success Rate: {successful/total*100:.1f}%"
        )
        
        try:
            await client.send_message(ADMIN_ID, report)
        except Exception as e:
            logger.error(f"Error sending broadcast report: {str(e)}")
