import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

import data_manager as dm

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Conversation states
WAITING_FOR_CODE = 1

# Time options (in minutes)
WASHING_MACHINE_TIMES = [2, 50, 60]
DRYER_TIMES = [45, 55, 65]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message and show main menu."""
    user = update.effective_user
    
    # Add user to database
    dm.add_user(user.id, user.username)
    
    keyboard = [
        [InlineKeyboardButton("📊 Status", callback_data="status")],
        [InlineKeyboardButton("🔧 Use a Machine", callback_data="use_machine")],
        [InlineKeyboardButton("✅ Collect Laundry", callback_data="collect")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 Hello {user.first_name}!\n\n"
        "Welcome to the Laundry Room Manager Bot 🧺\n\n"
        "What would you like to do?",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "status":
        await show_status(query)
    
    elif data == "use_machine":
        await show_machine_types(query)
    
    elif data == "washing_machines":
        await show_washing_machines(query)
    
    elif data == "dryers":
        await show_dryers(query)
    
    elif data.startswith("machine_"):
        # Format: machine_WM1 or machine_D1
        machine_id = data.split("_")[1]
        await show_time_options(query, machine_id)
    
    elif data.startswith("time_"):
        # Format: time_WM1_40
        parts = data.split("_")
        machine_id = parts[1]
        duration = int(parts[2])
        await start_machine(query, machine_id, duration, context)
    
    elif data.startswith("custom_"):
        # Format: custom_WM1
        machine_id = data.split("_")[1]
        await request_custom_time(query, machine_id, context)
    
    elif data == "collect":
        await start_collect(query)
    
    elif data == "back_to_main":
        await back_to_main(query)
    
    elif data == "back_to_machines":
        await show_machine_types(query)

async def show_status(query):
    """Show the status of all machines."""
    status_message = dm.get_status_message()
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        status_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_machine_types(query):
    """Show machine type selection."""
    keyboard = [
        [InlineKeyboardButton("🌀 Washing Machines", callback_data="washing_machines")],
        [InlineKeyboardButton("🔥 Dryers", callback_data="dryers")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        "Select machine type:",
        reply_markup=reply_markup
    )

async def show_washing_machines(query):
    """Show available washing machines."""
    machines = dm.get_all_machines()
    washing_machines = [m for m in machines if m['machine_type'] == 'washing_machine']
    
    keyboard = []
    for machine in washing_machines:
        status_emoji = "✅" if machine['status'] == 'free' else "⏳"
        button_text = f"{status_emoji} {machine['machine_id']}"
        
        if machine['status'] == 'free':
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"machine_{machine['machine_id']}")])
        else:
            keyboard.append([InlineKeyboardButton(f"{button_text} (In Use)", callback_data="noop")])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_machines")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        "🌀 *Washing Machines*\n\nSelect a free machine:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_dryers(query):
    """Show available dryers."""
    machines = dm.get_all_machines()
    dryers = [m for m in machines if m['machine_type'] == 'dryer']
    
    keyboard = []
    for machine in dryers:
        status_emoji = "✅" if machine['status'] == 'free' else "⏳"
        button_text = f"{status_emoji} {machine['machine_id']}"
        
        if machine['status'] == 'free':
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"machine_{machine['machine_id']}")])
        else:
            keyboard.append([InlineKeyboardButton(f"{button_text} (In Use)", callback_data="noop")])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_machines")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        "🔥 *Dryers*\n\nSelect a free machine:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_time_options(query, machine_id: str):
    """Show time duration options for the selected machine."""
    machine = dm.get_machine_by_id(machine_id)
    
    if machine['machine_type'] == 'washing_machine':
        times = WASHING_MACHINE_TIMES
        title = f"🌀 {machine_id} - Select Duration"
    else:
        times = DRYER_TIMES
        title = f"🔥 {machine_id} - Select Duration"
    
    keyboard = []
    for time in times:
        keyboard.append([InlineKeyboardButton(f"{time} minutes", callback_data=f"time_{machine_id}_{time}")])
    
    # Add custom time option
    keyboard.append([InlineKeyboardButton("✏️ Custom Time", callback_data=f"custom_{machine_id}")])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_machines")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        title,
        reply_markup=reply_markup
    )

async def request_custom_time(query, machine_id: str, context: ContextTypes.DEFAULT_TYPE):
    """Request custom time input from user."""
    # Store machine_id in user_data
    context.user_data['waiting_custom_time'] = machine_id
    
    keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        f"✏️ *Custom Time for {machine_id}*\n\n"
        f"Please enter the duration in minutes (as a number).\n\n"
        f"Example: `45` or `90`",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def start_machine(query, machine_id: str, duration: int, context: ContextTypes.DEFAULT_TYPE):
    """Start using a machine."""
    user = query.from_user
    
    # Use the machine
    code = dm.use_machine(machine_id, user.id, user.username, duration)
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        f"✅ *Machine {machine_id} is now reserved for you!*\n\n"
        f"⏱ Duration: {duration} minutes\n"
        f"🔑 Your collection code: `{code}`\n\n"
        f"_Please save this code. You'll need it to collect your laundry._\n\n"
        f"You'll receive a notification when it's finished!",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    # Schedule notification using job queue
    context.job_queue.run_once(
        send_machine_notification,
        duration * 60,
        data={'machine_id': machine_id, 'user_id': user.id},
        name=f"notification_{machine_id}_{user.id}"
    )

async def start_collect(query):
    """Start the collection process."""
    keyboard = [[InlineKeyboardButton("🔙 Cancel", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        "✅ *Collect Laundry*\n\n"
        "Please send me your 6-digit collection code.\n\n"
        "Format: `XXXXXX`",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_code_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle code input from user or custom time."""
    text = update.message.text.strip()
    user = update.effective_user
    
    # Check if user is entering custom time
    if 'waiting_custom_time' in context.user_data:
        machine_id = context.user_data['waiting_custom_time']
        
        # Try to parse as integer
        try:
            duration = int(text)
            if duration <= 0 or duration > 300:  # Max 5 hours
                keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(
                    "❌ Please enter a valid duration between 1 and 300 minutes.",
                    reply_markup=reply_markup
                )
                return
            
            # Clear the waiting state
            del context.user_data['waiting_custom_time']
            
            # Start the machine with custom time
            code = dm.use_machine(machine_id, user.id, user.username, duration)
            
            keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                f"✅ *Machine {machine_id} is now reserved for you!*\n\n"
                f"⏱ Duration: {duration} minutes\n"
                f"🔑 Your collection code: `{code}`\n\n"
                f"_Please save this code. You'll need it to collect your laundry._\n\n"
                f"You'll receive a notification when it's finished!",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            # Schedule notification using job queue
            context.job_queue.run_once(
                send_machine_notification,
                duration * 60,
                data={'machine_id': machine_id, 'user_id': user.id},
                name=f"notification_{machine_id}_{user.id}"
            )
            return
            
        except ValueError:
            keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "❌ Invalid format. Please enter a number (e.g., 45 or 90).",
                reply_markup=reply_markup
            )
            return
    
    # Otherwise, treat as collection code
    code = text.upper()
    user = update.effective_user
    
    # Find which machine has this code
    machines = dm.get_all_machines()
    found_machine = None
    
    for machine in machines:
        if machine['code'] == code and machine['status'] == 'in_use':
            found_machine = machine
            break
    
    if not found_machine:
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "❌ Invalid code or machine not in use.\n\n"
            "Please check your code and try again.",
            reply_markup=reply_markup
        )
        return
    
    # Collect the machine
    success, message = dm.collect_machine(found_machine['machine_id'], code)
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if success:
        await update.message.reply_text(
            f"✅ {message}",
            reply_markup=reply_markup
        )
        
        # Notify all users that machine is free
        await notify_all_users(
            context.bot,
            f"🎉 Machine {found_machine['machine_id']} is now FREE!"
        )
    else:
        await update.message.reply_text(
            f"❌ {message}",
            reply_markup=reply_markup
        )

async def back_to_main(query):
    """Return to main menu."""
    keyboard = [
        [InlineKeyboardButton("📊 Status", callback_data="status")],
        [InlineKeyboardButton("🔧 Use a Machine", callback_data="use_machine")],
        [InlineKeyboardButton("✅ Collect Laundry", callback_data="collect")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text(
        "🧺 *Laundry Room Manager*\n\nWhat would you like to do?",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def send_machine_notification(context: ContextTypes.DEFAULT_TYPE):
    """Job queue callback to send notification when machine finishes."""
    job_data = context.job.data
    machine_id = job_data['machine_id']
    user_id = job_data['user_id']
    
    # Check if machine is still in use (user might have collected early)
    machine = dm.get_machine_by_id(machine_id)
    if machine and machine['status'] == 'in_use' and machine['user_id'] == str(user_id):
        # Notify the user who started it
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"⏰ *Your laundry is ready!*\n\n"
                     f"Machine {machine_id} has finished.\n"
                     f"Please collect your laundry using your code: `{machine['code']}`",
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Could not send message to user {user_id}: {e}")
        
        # Notify all other users
        await notify_all_users(
            context.bot,
            f"🔔 Machine {machine_id} has finished and will be free soon!"
        )

async def notify_all_users(bot, message: str):
    """Send a notification to all subscribed users."""
    users = dm.get_all_users()
    
    for user in users:
        try:
            await bot.send_message(
                chat_id=int(user['user_id']),
                text=message
            )
        except Exception as e:
            print(f"Could not send message to user {user['user_id']}: {e}")

def main():
    """Start the bot."""
    # Initialize CSV files
    dm.init_csv_files()
    
    if not BOT_TOKEN:
        print("❌ Error: BOT_TOKEN not found in .env file")
        print("Please create a .env file with your bot token.")
        print("See .env.example for reference.")
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code_message))
    
    # Start the bot
    print("🤖 Bot is starting...")
    print("✅ Bot is running! Press Ctrl+C to stop.")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
