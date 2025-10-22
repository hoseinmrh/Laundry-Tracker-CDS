# 🧺 Laundry Room Manager Bot

A Telegram bot for managing washing machines and dryers in a university residence laundry room.

## Features

- 📊 **Check Status**: View which machines are free or in use with remaining time
- 🔧 **Use a Machine**: Reserve a washing machine or dryer for a specific duration
- ✅ **Collect Laundry**: Use your unique code to mark a machine as free after collection
- 🔔 **Notifications**: Get notified when your laundry is ready and when machines become available

## Machine Configuration

- **4 Washing Machines** (WM1, WM2, WM3, WM4)
  - Duration options: 40, 50, or 60 minutes

- **3 Dryers** (D1, D2, D3)
  - Duration options: 45, 55, or 65 minutes

## Setup Instructions

### 1. Get a Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the instructions
3. Choose a name and username for your bot
4. Copy the bot token that BotFather gives you

### 2. Clone or Download the Project

```bash
cd /Users/hoseinmirhoseini/Desktop/Projects/laundry-tracker
```

### 3. Create a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file and add your bot token:
   ```
   BOT_TOKEN=your_actual_bot_token_here
   ```

### 6. Run the Bot

```bash
python bot.py
```

You should see:
```
🤖 Bot is starting...
✅ Bot is running! Press Ctrl+C to stop.
```

## Usage

### Starting the Bot

1. Open Telegram and search for your bot by username
2. Send `/start` to begin
3. You'll see the main menu with three options:
   - 📊 Status
   - 🔧 Use a Machine
   - ✅ Collect Laundry

### Using a Machine

1. Click "🔧 Use a Machine"
2. Select washing machine or dryer
3. Choose an available machine (only free machines are selectable)
4. Select duration
5. Save your 6-digit collection code!

### Collecting Your Laundry

1. Click "✅ Collect Laundry"
2. Send your 6-digit code
3. The machine will be marked as free
4. All users will be notified

### Checking Status

1. Click "📊 Status"
2. See all machines with their status and time remaining

## Data Storage

The bot uses CSV files for data persistence:
- `machines.csv` - Machine status, current user, codes, and end times
- `users.csv` - Registered users for notifications

These files are created automatically when you first run the bot.

## How It Works

1. **Reservation**: When you use a machine, it's marked as "in use" with your user ID and a unique code
2. **Timer**: The bot calculates when the machine will finish based on your selected duration
3. **Notifications**: 
   - After the duration, you get a personal notification with your code
   - All other users get notified that a machine is finishing
4. **Collection**: You enter your code to free the machine
5. **Freedom**: All users are notified that the machine is now free

## Stopping the Bot

Press `Ctrl+C` in the terminal to stop the bot.

## Testing Locally

1. Make sure the bot is running (`python bot.py`)
2. Open Telegram and start a chat with your bot
3. Try the different features:
   - Check status when all machines are free
   - Reserve a machine (you can test with shorter times if needed)
   - Check status again to see the machine in use
   - Use your code to collect
   - Check that notifications are working

## Future Improvements

- Replace CSV with a proper database (SQLite, PostgreSQL)
- Add admin panel for managing machines
- Add waiting list/queue system
- Send reminders if laundry isn't collected after finished
- Add statistics and usage reports

## Troubleshooting

### Bot doesn't respond
- Check that the bot token is correct in `.env`
- Make sure the bot is running (`python bot.py`)
- Verify internet connection

### Import errors
- Make sure you've installed dependencies: `pip install -r requirements.txt`
- Activate your virtual environment if using one

### CSV file errors
- The CSV files are created automatically
- If you want to reset, just delete `machines.csv` and `users.csv` and restart the bot

## License

This is a prototype project for personal/educational use.
