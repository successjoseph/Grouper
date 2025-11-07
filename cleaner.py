import csv
import re  # Import regular expressions

# --- CONFIGURATION ---
RAW_CSV_FILE = 'raw_responses.csv' 
CLEAN_CSV_FILE = 'students.csv'

# Column names to clean
COL_WHATSAPP = "Your WhatsApp Number e.g. +2348012345678 (Optional)"
COURSE_COLS = ["Course Code 1", "Course Code 2", "Course Code 3"]
GROUP_COLS = ["Group Code 1", "Group Code 2", "Group Code 3"]
# --- END CONFIGURATION ---


def clean_phone_number(phone_str, row_num):
    """Standardizes Nigerian phone numbers to +234 format."""
    phone_str = phone_str.strip().replace(" ", "")
    
    if not phone_str:
        return ""
    
    if phone_str.startswith('0') and len(phone_str) == 11:
        return '+234' + phone_str[1:]
    
    if phone_str.startswith('234') and len(phone_str) == 13:
        return '+' + phone_str
        
    if phone_str.startswith(('80', '81', '90', '91', '70')) and len(phone_str) == 10:
        return '+234' + phone_str
        
    if phone_str.startswith('+234') and len(phone_str) == 14:
        return phone_str
    
    print(f"  > Warning [Row {row_num}]: Non-standard phone format, leaving as-is: {phone_str}")
    return phone_str


def clean_course_code(code, row_num):
    """
    Cleans course codes.
    - cos201 -> COS 201
    - cos 201 -> COS 201
    """
    if not code:
        return ""
    
    # 1. Remove all spaces and uppercase: "cos 201" -> "COS201"
    clean_code = code.strip().upper().replace(" ", "")
    
    # 2. Use regex to find "LETTERS" followed by "NUMBERS"
    #    ^([A-Z]+) = Capture group 1: one or more letters at the start
    #    (\d+)     = Capture group 2: one or more digits
    #    $         = End of the string
    match = re.match(r"^([A-Z]+)(\d+)$", clean_code)
    
    if match:
        # Re-format as "LETTERS" "NUMBERS"
        return f"{match.group(1)} {match.group(2)}"
    
    # If it's already in the correct format (e.g., "COS 201"), the
    # .replace(" ", "") would have been skipped, but just in case,
    # let's check for the original format.
    if re.match(r"^[A-Z]+ \d+$", code.strip().upper()):
        return code.strip().upper()
        
    # If no pattern matches, just uppercase it and flag it
    print(f"  > Warning [Row {row_num}]: Non-standard course code format, just uppercasing: '{code}'")
    return code.strip().upper()


def clean_group_code(code, row_num):
    """
    Cleans group codes.
    - Fixes case
    - Fixes missing hyphen in "MANCOS"
    - Flags if it doesn't end in a number
    """
    if not code:
        return ""
        
    # 1. Fix case and whitespace
    clean_code = code.strip().upper()
    
    # 2. Fix missing hyphen (e.g., "MANCOS JAN25 G1" -> "MAN-COS JAN25 G1")
    if clean_code.startswith("MANCOS "):
        clean_code = clean_code.replace("MANCOS ", "MAN-COS ", 1)
        
    # 3. Flag if it does not end in a number
    #    (but only if the code isn't empty)
    if clean_code and not clean_code[-1].isdigit():
        print(f"  > Warning [Row {row_num}]: Group code '{clean_code}' (original: '{code}') does not end in a number.")
        
    return clean_code


def main():
    print("--- 🧹 CSV Data Cleaner ---")
    
    print("\nSelect cleaning options (y/n):")
    do_clean_phone = input("  1. Standardize phone numbers (e.g., 080 -> +234)? [y/n]: ").lower().strip() == 'y'
    do_clean_codes = input("  2. Fix course/group codes (e.g., cos201 -> COS 201)? [y/n]: ").lower().strip() == 'y'

    print("\nStarting cleaning process...")
    cleaned_rows = []
    original_headers = None  # <-- Initialize here
        
    try:
        
        with open(RAW_CSV_FILE, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            original_headers = reader.fieldnames
            
            # --- ADDED CHECK ---
            # If the file is empty or corrupt, headers will be None
            if original_headers is None:
                print(f"FATAL ERROR: Could not read headers from '{RAW_CSV_FILE}'.")
                print("The file might be empty, corrupt, or not a valid CSV.")
                return
            # ---
            
            # Start at 2 because 1 is the header row
            for row_num, row in enumerate(reader, start=2):
            
            # Start at 2 because 1 is the header row
                cleaned_row = row.copy()
                
                # --- Clean Phone Numbers ---
                if do_clean_phone and COL_WHATSAPP in cleaned_row:
                    original_phone = cleaned_row[COL_WHATSAPP]
                    if original_phone:
                        cleaned_row[COL_WHATSAPP] = clean_phone_number(original_phone, row_num)
                
                # --- Clean Course/Group Codes ---
                if do_clean_codes:
                    # Clean Course Codes
                    for col_name in COURSE_COLS:
                        if col_name in cleaned_row and cleaned_row[col_name]:
                            cleaned_row[col_name] = clean_course_code(cleaned_row[col_name], row_num)
                    
                    # Clean Group Codes
                    for col_name in GROUP_COLS:
                        if col_name in cleaned_row and cleaned_row[col_name]:
                            cleaned_row[col_name] = clean_group_code(cleaned_row[col_name], row_num)
                
                cleaned_rows.append(cleaned_row)

    except FileNotFoundError:
        print(f"FATAL ERROR: Raw input file not found at '{RAW_CSV_FILE}'.")
        print("Please download your CSV from Forms and save it with that name.")
        return
    except Exception as e:
        print(f"An error occurred while reading: {e}")
        return

    # 3. Write the cleaned data to the new file
    if not cleaned_rows:
        print("No data was read. Output file not created.")
        return

    try:
        with open(CLEAN_CSV_FILE, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=original_headers)
            writer.writeheader()
            writer.writerows(cleaned_rows)
        
        print(f"\n✨ Success! Cleaned {len(cleaned_rows)} rows.")
        print(f"Cleaned data saved to '{CLEAN_CSV_FILE}'.")
        print("You can now run 'sorter.py'.")

    except IOError as e:
        print(f"FATAL ERROR: Could not write to '{CLEAN_CSV_FILE}'. Reason: {e}")

if __name__ == "__main__":
    main()