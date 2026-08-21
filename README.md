# Grouper

![Language](https://img.shields.io/badge/language-Python-blue)
![License](https://img.shields.io/badge/license-none-lightgrey)

## Table of Contents
- [About](#about)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
- [Contributing](#contributing)
- [Authors and License](#authors-and-license)

## About
Grouper is a small collection of three standalone Python scripts for processing a course-registration/form-response CSV (e.g. from a Google Form), organizing students into course/group cohorts, and emailing each student their group's member list. It looks purpose-built for a specific community/course context — string literals reference "Techies," course codes like "COS 201," and a "MAN-COS" group-naming convention — consistent with organizing study/project groups for a student cohort. Note: a separate, unrelated JS repo named `ai-tab-grouper` exists on this account and is a distinct project.

The three scripts form a linear pipeline:
1. **`cleaner.py`** — reads a raw form-export CSV (`raw_responses.csv`), interactively (via `y`/`n` prompts) standardizes Nigerian phone numbers to `+234` format and normalizes course/group code formatting (e.g. `cos201` → `COS 201`), and writes the cleaned result to `students.csv`.
2. **`sorter.py`** — reads `students.csv`, groups students by up to three `(course, group_code)` pairs per student (each student can belong to up to 3 course groups), and writes the grouped roster to `groups.json`.
3. **`group_mailer.py`** — reads `groups.json` and emails every member of every group a personalized message listing all of their groupmates' names, emails, and WhatsApp numbers, via Gmail SMTP. It tracks progress in `sent_log.json` so re-running the script skips already-sent emails, and waits 10 seconds between sends to avoid rate limiting.

## Prerequisites
- Python 3 (`cleaner.py`/`sorter.py` use only the standard library; `group_mailer.py` additionally needs `python-dotenv`)
- A Gmail account with an app password for SMTP sending (used by `group_mailer.py`)

## Installation
```bash
git clone https://github.com/successjoseph/Grouper.git
cd Grouper
pip install -r requirements.txt
```

## Configuration
- **`cleaner.py`**: `RAW_CSV_FILE` (`raw_responses.csv`) and `CLEAN_CSV_FILE` (`students.csv`) filenames, plus the exact form column names (`COL_WHATSAPP`, `COURSE_COLS`, `GROUP_COLS`) are hardcoded constants at the top of the file and must match your actual form export headers.
- **`sorter.py`**: `CSV_FILE_NAME`, `JSON_OUTPUT_FILE`, and the same kind of hardcoded column-name constants (`COL_NAME`, `COL_EMAIL`, `COL_WHATSAPP`, `COURSE_COLS`, `GROUP_COLS`).
- **`group_mailer.py`**: reads its Gmail sender/app password from environment variables via a local, gitignored `.env` (loaded with `python-dotenv`): `GROUPER_GMAIL_SENDER` and `GROUPER_GMAIL_APP_PASSWORD`. **Security note:** these were previously hardcoded in plaintext directly in `group_mailer.py`'s `SMTP_CONFIG` dict and committed to git; they have been moved to `.env` and flagged for rotation, but since they were already exposed in git history, the Gmail app password should still be regenerated. `DELAY_BETWEEN_EMAILS` (seconds between sends) remains a hardcoded constant in the same file.
- **`.gitignore`** excludes all `*.json` and `*.csv` files (so student data like `raw_responses.csv`/`students.csv`/`groups.json`/`sent_log.json` is never committed) and now also excludes `.env`.

## Usage
Run the three stages in order from the repo root, with your raw CSV placed alongside the scripts:
```bash
python cleaner.py       # interactive: prompts to standardize phone numbers and/or course codes
                         # raw_responses.csv -> students.csv
python sorter.py        # students.csv -> groups.json
python group_mailer.py  # emails each group's roster to its members, using groups.json
```

## Testing
No automated tests are currently included.

## Contributing
This is a personal utility script for organizing a specific course/community cohort — notes for future you rather than an open contribution target.

## Authors and License
- **Author:** [successjoseph](https://github.com/successjoseph)
- **License:** No license file included — all rights reserved by default.
