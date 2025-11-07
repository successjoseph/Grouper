import csv
import json

# --- CONFIGURATION ---
CSV_FILE_NAME = 'students.csv'
JSON_OUTPUT_FILE = 'groups.json'

# Column names from your CSV
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
                
                # Use a tuple for the member info
                member_info = (student_name.strip(), student_email.strip())
                
                # Check all 3 course/group pairs
                for i in range(3):
                    course = row.get(COURSE_COLS[i])
                    group_code = row.get(GROUP_COLS[i])
                    
                    # Only create a group if both fields exist
                    if course and group_code:
                        group_key = (course.strip(), group_code.strip())
                        
                        if group_key not in groups:
                            groups[group_key] = []
                        
                        # Add student to this group if not already present
                        if member_info not in groups[group_key]:
                            groups[group_key].append(member_info)
                            
    except FileNotFoundError:
        print(f"ERROR: CSV file not found at '{csv_file}'")
        return None
    except Exception as e:
        print(f"An error occurred reading the CSV: {e}")
        return None
        
    return groups

def main():
    print(f"Reading CSV file: {CSV_FILE_NAME}...")
    all_groups_dict = build_groups(CSV_FILE_NAME)
    
    if all_groups_dict is None:
        print("Exiting due to CSV error.")
        return
        
    if not all_groups_dict:
        print("No groups were found or built. Check your CSV.")
        return

    # Convert the dictionary with tuple keys to a JSON-friendly list
    json_output_list = []
    for (course, group_code), members in all_groups_dict.items():
        json_output_list.append({
            "course": course,
            "group_code": group_code,
            "members": members  # 'members' is a list of (name, email) tuples
        })

    # Save the clean list to a JSON file
    try:
        with open(JSON_OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(json_output_list, f, indent=4)
        print(f"\nSuccess! Built {len(json_output_list)} groups.")
        print(f"All group data saved to '{JSON_OUTPUT_FILE}'.")
    except IOError as e:
        print(f"ERROR: Could not write JSON file. Reason: {e}")

if __name__ == "__main__":
    main()