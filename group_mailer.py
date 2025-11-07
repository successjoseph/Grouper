import csv
import smtplib
import ssl
from email.message import EmailMessage

# --- CONFIGURATION ---

# 1. Update this with your CSV file's name
CSV_FILE_NAME = 'students.csv' 

# 2. Add your email credentials (SEE NOTES BELOW)
SMTP_CONFIG = {
    "server": "smtp.gmail.com",  # Example for Gmail
    "port": 465,                 # For SSL
    "sender_email": "REDACTED",
    "sender_password": "REDACTED"  # Use App Passwords for Gmail
}

# 3. Define the exact column names from your CSV
COL_NAME = "Your Full Name (School Format)"
COL_EMAIL = "Your School Mail (please check your capitalization)"
COURSE_COLS = ["Course Code 1", "Course Code 2", "Course Code 3"]
GROUP_COLS = ["Group Code 1", "Group Code 2", "Group Code 3"]

# --- END CONFIGURATION ---


def build_groups(csv_file):
    """Reads the CSV and builds a dictionary of groups."""
    groups = {}  # Key: (course, group_code), Value: [(name, email)]
    
    try:
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                student_name = row.get(COL_NAME)
                student_email = row.get(COL_EMAIL)
                
                if not student_name or not student_email:
                    print(f"Skipping row with missing name or email: {row}")
                    continue
                
                member_info = (student_name, student_email)
                
                # Check all 3 course/group pairs
                for i in range(3):
                    course = row.get(COURSE_COLS[i])
                    group_code = row.get(GROUP_COLS[i])
                    
                    # Only create a group if both fields exist
                    if course and group_code:
                        group_key = (course.strip(), group_code.strip())
                        
                        if group_key not in groups:
                            groups[group_key] = []
                        
                        # Add student to this group
                        if member_info not in groups[group_key]:
                            groups[group_key].append(member_info)
                            
    except FileNotFoundError:
        print(f"ERROR: CSV file not found at '{csv_file}'")
        return None
    except Exception as e:
        print(f"An error occurred reading the CSV: {e}")
        return None
        
    return groups


def send_group_email(group_key, members, config):
    """Sends a single email to all members of a group."""
    
    course, group_code = group_key
    subject = f"Your Group Members for: {course} - {group_code}"
    
    # --- Create the email body ---
    body = f"Hello,\n\nHere is the member list for your group in {course} ({group_code}):\n\n"
    
    for name, email in members:
        body += f"* {name} ({email})\n"
        
    body += "\nBest,\nTechies Grouper Bot"

    body += "\n\n---\nThis is an automated message. Please do not reply."

    body += "\n To join the Techies WhatsApp Community, click here: https://chat.whatsapp.com/JjHYvV3wPNFIf0ohGG3ZLZ"
    # ---
    
    # Get the list of all recipient emails
    recipient_emails = [email for name, email in members]
    
    # Create the email message
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = config["sender_email"]
    msg['To'] = ", ".join(recipient_emails)  # Join all emails with a comma
    msg.set_content(body)
    
    print(f"Attempting to send email for group '{course} - {group_code}' to {len(recipient_emails)} members...")
    
    # Send the email
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(config["server"], config["port"], context=context) as server:
            server.login(config["sender_email"], config["sender_password"])
            server.send_message(msg)
        print(f"  > SUCCESS: Email sent for {course} - {group_code}.")
    except smtplib.SMTPException as e:
        print(f"  > ERROR: Failed to send email for {course} - {group_code}. Reason: {e}")


def main():
    # 1. Build the groups from the CSV
    print(f"Reading CSV file: {CSV_FILE_NAME}...")
    all_groups = build_groups(CSV_FILE_NAME)
    
    if all_groups is None:
        print("Exiting due to CSV error.")
        return
        
    if not all_groups:
        print("No groups were found or built. Check your CSV.")
        return

    print(f"Successfully built {len(all_groups)} unique groups.")
    
    # 2. Loop and send emails
    print("\nStarting to send emails...")
    for group_key, members in all_groups.items():
        send_group_email(group_key, members, SMTP_CONFIG)
        
    print("\nAll tasks complete.")

# Run the script
if __name__ == "__main__":
    main()