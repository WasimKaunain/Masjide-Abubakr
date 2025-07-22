import gspread
from google.oauth2.service_account import Credentials
from collections import Counter
from datetime import datetime
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv()

# Define SCOPES for both Sheets and Drive access
SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']

# Get authorized gspread client and credentials (for Drive API)
def get_gsheet_client_and_creds():
    service_account_info = {
        "type": os.getenv("GOOGLE_TYPE"),
        "project_id": os.getenv("GOOGLE_PROJECT_ID"),
        "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
        "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_CERT_URL"),
        "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_CERT_URL")
    }

    creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    gc = gspread.authorize(creds)
    return gc, creds

# Append a row of data to the first sheet
def append_to_sheet(data, sheet_name):
    gc, _ = get_gsheet_client_and_creds()
    sheet = gc.open(sheet_name).sheet1
    sheet.append_row(data)

# Returns the current working sheet name
def get_current_sheet_name():
    return "Imam's Salary transaction"

# Save current sheet (rename & archive)
def save_current_sheet():
    sheet_name = get_current_sheet_name()
    archive_and_create_new_sheet(sheet_name)

# Create folder if not exists and return folder ID
def get_or_create_folder(folder_name, drive_service):
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    response = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    files = response.get('files', [])
    
    if files:
        return files[0]['id']
    
    # Create folder if not found
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = drive_service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')

# Archive old sheet and create new one
def archive_and_create_new_sheet(old_sheet_name):
    # Step 1: Setup clients
    gc, creds = get_gsheet_client_and_creds()
    old_sheet = gc.open(old_sheet_name)
    sheet_data = old_sheet.sheet1.get_all_records()

    # Step 2: Extract most common month/year from "Timestamp"
    month_year_counter = Counter()
    for row in sheet_data:
        timestamp = row.get("Timestamp")
        if timestamp:
            try:
                dt = datetime.strptime(timestamp, "%m/%d/%Y %H:%M:%S")
                month_year = (dt.year, dt.strftime("%B"))
                month_year_counter[month_year] += 1
            except ValueError:
                continue

    if not month_year_counter:
        raise ValueError("No valid timestamps found to determine dominant month/year.")

    most_common_year, most_common_month = month_year_counter.most_common(1)[0][0]

    # Step 3: Rename the sheet
    new_title = f"Donation {most_common_year} {most_common_month}"
    old_sheet.update_title(new_title)

    # Step 4: Move old sheet to folder
    drive_service = build('drive', 'v3', credentials=creds)
    file_id = old_sheet.id
    folder_id = get_or_create_folder("Masjid-e-Abu Bakr", drive_service)
    drive_service.files().update(fileId=file_id, addParents=folder_id).execute()

    # Step 5: Create new sheet
    new_sheet_name = get_current_sheet_name()
    new_sheet = gc.create(new_sheet_name)

    # Step 6: Make sheet public (view-only)
    drive_service.permissions().create(
        fileId=new_sheet.id,
        body={"role": "reader", "type": "anyone"},
        fields="id"
    ).execute()

    # Step 7: Append headers to new sheet
    new_sheet.sheet1.append_row(['Name', 'Amount', 'Payment Method', 'Email', 'Timestamp'])
