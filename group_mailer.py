import json
import smtplib
import ssl
from email.message import EmailMessage
import time
import os
from dotenv import load_dotenv

load_dotenv()

# --- CONFIGURATION ---
JSON_FILE_NAME = 'groups.json'
PROGRESS_FILE = 'sent_log.json'

SMTP_CONFIG = {
    "server": "smtp.gmail.com",
    "port": 465,
    "sender_email": os.getenv("GROUPER_GMAIL_SENDER"),
    "sender_password": os.getenv("GROUPER_GMAIL_APP_PASSWORD")  # Rotate this — was hardcoded here, now in .env
}

DELAY_BETWEEN_EMAILS = 10 
# --- END CONFIGURATION ---


def load_progress(progress_file):
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
    try:
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(list(progress_set), f)
    except IOError as e:
        print(f"  > CRITICAL WARNING: Could not save progress to log! Reason: {e}")


def send_personalized_email(recipient_info, group_info, all_members, config):
    """
    Sends one personalized email to one group member.
    Returns True on success, False on failure.
    """
    
    # --- MODIFIED ---
    # Unpack the recipient info (name, email, phone). We only need name and email.
    recipient_name, recipient_email, _ = recipient_info 
    # ---
    
    course = group_info["course"]
    group_code = group_info["group_code"]
    
    subject = f"Your Group Members for: {course} - {group_code}"
    
    # --- Create the personalized email body (MODIFIED) ---
    body = f"Hello {recipient_name},\n\n"
    body += f"Here is the member list for your group in {course} ({group_code}):\n\n"
    
    # --- MODIFIED ---
    # Now loops through (name, email, phone) tuples
    for name, email, phone in all_members:
        body += f"* {name} - {email} - (Phone: {phone})\n"
    # ---
        
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
    
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(config["server"], config["port"], context=context) as server:
            server.login(config["sender_email"], config["sender_password"])
            server.send_message(msg)
        print(" SUCCESS.")
        return True 
        
    except smtplib.SMTPException as e:
        print(f" FAILED. Reason: {e}")
        return False 
    except Exception as e:
        print(f" FAILED. Unexpected error: {e}")
        return False 


def main():
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
            # --- MODIFIED ---
            # Unpack to get the email for the log_key
            recipient_name, recipient_email, _ = member_tuple
            # ---
            
            log_key = f"{recipient_email}|{group_info['course']}|{group_info['group_code']}"
            
            if log_key in progress_set:
                print(f"  > SKIPPING: {recipient_name} (already sent for this group).")
                continue 
            
            success = send_personalized_email(
                recipient_info=member_tuple, # Pass the full (name, email, phone) tuple
                group_info=group_info,
                all_members=group_members,
                config=SMTP_CONFIG
            )
            
            if success:
                progress_set.add(log_key)
                save_progress(PROGRESS_FILE, progress_set)
            
            time.sleep(DELAY_BETWEEN_EMAILS)
            
    print("\n--- All tasks complete ---")

if __name__ == "__main__":
    main()