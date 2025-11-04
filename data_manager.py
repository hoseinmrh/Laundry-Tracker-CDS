import csv
import os
import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# File paths
MACHINES_FILE = "machines.csv"
USERS_FILE = "users.csv"

# Machine types
WASHING_MACHINES = 4
DRYERS = 3

def init_csv_files():
    """Initialize CSV files if they don't exist."""
    
    # Initialize machines.csv
    if not os.path.exists(MACHINES_FILE):
        with open(MACHINES_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['machine_id', 'machine_type', 'status', 'user_id', 'username', 'code', 'end_time'])
            
            # Create washing machines
            for i in range(1, WASHING_MACHINES + 1):
                writer.writerow([f'WM{i}', 'washing_machine', 'free', '', '', '', ''])
            
            # Create dryers
            for i in range(1, DRYERS + 1):
                writer.writerow([f'D{i}', 'dryer', 'free', '', '', '', ''])
    
    # Initialize users.csv
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['user_id', 'username', 'subscribed'])

def generate_code(length=6):
    """Generate a random alphanumeric code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def add_user(user_id: int, username: str):
    """Add a new user to the users file if they don't exist."""
    users = get_all_users()
    
    # Check if user already exists
    for user in users:
        if user['user_id'] == str(user_id):
            return
    
    # Add new user
    with open(USERS_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([user_id, username or 'Unknown', 'yes'])

def get_all_users() -> List[Dict]:
    """Get all subscribed users."""
    users = []
    with open(USERS_FILE, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['subscribed'] == 'yes':
                users.append(row)
    return users

def get_all_machines() -> List[Dict]:
    """Get all machines with their current status."""
    machines = []
    with open(MACHINES_FILE, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            machines.append(row)
    return machines

def get_machine_by_id(machine_id: str) -> Optional[Dict]:
    """Get a specific machine by its ID."""
    machines = get_all_machines()
    for machine in machines:
        if machine['machine_id'] == machine_id:
            return machine
    return None

def use_machine(machine_id: str, user_id: int, username: str, duration_minutes: int) -> str:
    """Mark a machine as in use and return the access code."""
    machines = get_all_machines()
    code = generate_code()
    end_time = datetime.now() + timedelta(minutes=duration_minutes)
    
    # Update the machine
    with open(MACHINES_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['machine_id', 'machine_type', 'status', 'user_id', 'username', 'code', 'end_time'])
        
        for machine in machines:
            if machine['machine_id'] == machine_id:
                writer.writerow([
                    machine_id,
                    machine['machine_type'],
                    'in_use',
                    user_id,
                    username or 'Unknown',
                    code,
                    end_time.isoformat()
                ])
            else:
                writer.writerow([
                    machine['machine_id'],
                    machine['machine_type'],
                    machine['status'],
                    machine['user_id'],
                    machine['username'],
                    machine['code'],
                    machine['end_time']
                ])
    
    return code

def collect_machine(machine_id: str, code: str) -> tuple[bool, str]:
    """
    Verify code and free the machine.
    Returns (success, message)
    """
    machine = get_machine_by_id(machine_id)
    
    if not machine:
        return False, "Machine not found."
    
    if machine['status'] != 'in_use':
        return False, "This machine is not currently in use."
    
    if machine['code'] != code:
        return False, "Incorrect code. Please check and try again."
    
    # Free the machine
    machines = get_all_machines()
    with open(MACHINES_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['machine_id', 'machine_type', 'status', 'user_id', 'username', 'code', 'end_time'])
        
        for m in machines:
            if m['machine_id'] == machine_id:
                writer.writerow([
                    machine_id,
                    m['machine_type'],
                    'free',
                    '',
                    '',
                    '',
                    ''
                ])
            else:
                writer.writerow([
                    m['machine_id'],
                    m['machine_type'],
                    m['status'],
                    m['user_id'],
                    m['username'],
                    m['code'],
                    m['end_time']
                ])
    
    return True, f"Machine {machine_id} is now free. Thank you!"

def get_status_message() -> str:
    """Generate a status message for all machines."""
    machines = get_all_machines()
    
    message = "🏠 *Laundry Room Status*\n\n"
    
    # Washing Machines
    message += "🌀 *Washing Machines:*\n"
    for machine in machines:
        if machine['machine_type'] == 'washing_machine':
            status_emoji = "✅"
            status_text = "Free"
            
            if machine['status'] == 'in_use' and machine['end_time']:
                try:
                    end_time = datetime.fromisoformat(machine['end_time'])
                    time_left = end_time - datetime.now()
                    if time_left.total_seconds() > 0:
                        minutes_left = int(time_left.total_seconds() / 60)
                        status_emoji = "⏳"
                        status_text = f"In Use ({minutes_left} min left)"
                    else:
                        status_emoji = "🧺"
                        status_text = "Finished (Ready to collect)"
                except:
                    status_emoji = "⏳"
                    status_text = "In Use"
            
            message += f"{status_emoji} {machine['machine_id']}: {status_text}\n"
    
    # Dryers
    message += "\n🔥 *Dryers:*\n"
    for machine in machines:
        if machine['machine_type'] == 'dryer':
            status_emoji = "✅"
            status_text = "Free"
            
            if machine['status'] == 'in_use' and machine['end_time']:
                try:
                    end_time = datetime.fromisoformat(machine['end_time'])
                    time_left = end_time - datetime.now()
                    if time_left.total_seconds() > 0:
                        minutes_left = int(time_left.total_seconds() / 60)
                        status_emoji = "⏳"
                        status_text = f"In Use ({minutes_left} min left)"
                    else:
                        status_emoji = "🧺"
                        status_text = "Finished (Ready to collect)"
                except:
                    status_emoji = "⏳"
                    status_text = "In Use"
            
            message += f"{status_emoji} {machine['machine_id']}: {status_text}\n"
    
    return message

def check_finished_machines() -> List[Dict]:
    """Check for machines that have finished and return their info."""
    finished = []
    machines = get_all_machines()
    now = datetime.now()
    
    for machine in machines:
        if machine['status'] == 'in_use' and machine['end_time']:
            try:
                end_time = datetime.fromisoformat(machine['end_time'])
                if now >= end_time:
                    finished.append(machine)
            except:
                pass
    
    return finished
