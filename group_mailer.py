import json
import smtplib
import ssl
from email.message import EmailMessage
import time
import os  # Added os

# --- CONFIGURATION ---
JSON_FILE_NAME = 'groups.json' # The file created by sorter.py
PROGRESS_FILE = 'sent_log.json' # New file to track sent emails

SMTP_CONFIG = {
    "server": "smtp.gmail.com",
    "port": 465,
    "sender_email": "REDACTED",
    "sender_password": "REDACTED" # Your App Password
}

DELAY_BETWEEN_EMAILS = 1 # in seconds
# --- END CONFIGURATION ---


def load_progress(progress_file):
    """Loads the set of already sent email keys."""
    if not os.path.exists(progress_file):
        return set()
    try:
        with open(progress_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return set(data)
    except json.JSONDecodeError:
        print(f"Warning: Could not read '{progress_file}'. Starting fresh.")
        return set()

def save_progress(progress_file, progress_set):
    """Saves the set of sent email keys back to the file."""
    try:
        with open(progress_file, 'w', encoding='utf-8') as f:
            # Convert set to list for JSON serialization
            json.dump(list(progress_set), f)
    except IOError as e:
        print(f"  > CRITICAL WARNING: Could not save progress to log! Reason: {e}")


def send_personalized_email(recipient_info, group_info, all_members, config):
    """
    Sends one personalized email to one group member.
    Returns True on success, False on failure.
    """
    
    recipient_name, recipient_email = recipient_info
    course = group_info["course"]
    group_code = group_info["group_code"]
    
    subject = f"Your Group Members for: {course} - {group_code}"
    
    # --- Create the personalized email body ---
    body = f"Hello {recipient_name},\n\n"
    body += f"Here is the member list for your group in {course} ({group_code}):\n\n"
    
    for name, email in all_members:
        body += f"* {name} ({email})\n"
        
    body += "\nBest,\nTechies Grouper Bot"
    body += "\n\n---\nThis is an automated message. Please do not reply."
    body += "\nTo join the Techies WhatsApp Community, click here: https://chat.whatsapp.com/JjHYvV3wPNFIf0ohGG3ZLZ"
    # ---
    
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = config["sender_email"]
    msg['To'] = recipient_email
    msg.set_content(body)
    
    print(f"  > Sending to: {recipient_name} ({recipient_email})...", end="")
    
    # Send the email
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(config["server"], config["port"], context=context) as server:
            server.login(config["sender_email"], config["sender_password"])
            server.send_message(msg)
        print(" SUCCESS.")
        return True # <-- Return True on success
        
    except smtplib.SMTPException as e:
        print(f" FAILED. Reason: {e}")
        return False # <-- Return False on failure
    except Exception as e:
        print(f" FAILED. Unexpected error: {e}")
        return False # <-- Return False on failure


def main():
    # 1. Load the groups from the JSON file
    try:
        with open(JSON_FILE_NAME, 'r', encoding='utf-8') as f:
            all_groups_list = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: '{JSON_FILE_NAME}' not found.")
        print("Please run 'sorter.py' first to create the file.")
        return
    except json.JSONDecodeError:
        print(f"ERROR: Could not read '{JSON_FILE_NAME}'. File might be empty or corrupt.")
        return

    # 2. Load the progress log
    progress_set = load_progress(PROGRESS_FILE)
    print(f"Loaded {len(all_groups_list)} groups.")
    print(f"Found {len(progress_set)} previously sent emails in log.")

    total_emails_to_send = sum(len(group["members"]) for group in all_groups_list)
    print(f"Total emails to process: {total_emails_to_send}\n")
    print("--- Starting Mailer ---")
    
    for group in all_groups_list:
        group_members = group["members"]
        group_info = {"course": group["course"], "group_code": group["group_code"]}
        
        print(f"\nProcessing Group: {group_info['course']} - {group_info['group_code']} ({len(group_members)} members)")
        
        for member_tuple in group_members:
            recipient_name, recipient_email = member_tuple
            
            # Create a unique key for this specific email
            log_key = f"{recipient_email}|{group_info['course']}|{group_info['group_code']}"
            
            # --- CHECK THE LOG ---
            if log_key in progress_set:
                print(f"  > SKIPPING: {recipient_name} (already sent for this group).")
                continue # Skip to the next person
            
            # --- SEND THE EMAIL ---
            success = send_personalized_email(
                recipient_info=member_tuple,
                group_info=group_info,
                all_members=group_members,
                config=SMTP_CONFIG
            )
            
            # --- LOG ON SUCCESS ---
            if success:
                progress_set.add(log_key)
                save_progress(PROGRESS_FILE, progress_set)
            
            time.sleep(DELAY_BETWEEN_EMAILS)
            
    print("\n--- All tasks complete ---")

# Run the script
if __name__ == "__main__":
    main()