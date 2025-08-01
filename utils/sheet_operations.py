import gspread
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from collections import Counter
from datetime import datetime
from googleapiclient.discovery import build
from dotenv import load_dotenv
import os,json,base64,time

load_dotenv()

# Define SCOPES for both Sheets and Drive access
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file"
]

def get_main_account_credentials():
    main_token=json.loads(base64.b64decode(os.getenv('MAIN_TOKEN')).decode("utf-8"))
    # main_credentials=json.loads(base64.b64decode(os.getenv('MAIN_CREDENTIALS')).decode("utf-8"))

    creds = None
    # token.json stores access and refresh tokens
    creds = Credentials.from_authorized_user_info(main_token, SCOPES)

    # If no token or invalid, do OAuth login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise RuntimeError("OAuth token is missing or invalid, and cannot re-authenticate on a server.")

    return creds

# Get authorized gspread client and credentials (for Drive API)
def get_gsheet_client_and_creds():
    creds = service_account.Credentials.from_service_account_info(json.loads(base64.b64decode(os.getenv('SERVICE_ACCOUNT_CREDENTIALS')).decode('utf-8')), scopes=SCOPES)
    gc = gspread.authorize(creds)

    return gc, creds


# Append a row of data to the first sheet
def append_to_sheet(data, sheet_name):

    gc, creds = get_gsheet_client_and_creds()

    try:
        sheet = gc.open_by_key('1A-cmA5pITg1y-Vc0TFn0XG6MGTPSlk5I5vnN52k8wOQ').sheet1

    except gspread.exceptions.SpreadsheetNotFound:
        main_creds = get_main_account_credentials()
        main_gc = gspread.authorize(main_creds)

        # Create Drive service
        drive_service = build('drive', 'v3', credentials=main_creds)


        # Create/get the folder
        folder_id = get_or_create_folder("Masjid-e-Abu Bakr", drive_service)
        # Create the new spreadsheet inside the folder
        sheet_metadata = {
            'name': sheet_name,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
            'parents': [folder_id]
        }
        file = drive_service.files().create(body=sheet_metadata, fields='id').execute()
        spreadsheet_id = file['id']

        #Give editor access to the developer email
        permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': os.getenv('CLIENT_EMAIL')
        }
        drive_service.permissions().create(
            fileId=spreadsheet_id,
            body=permission,
            sendNotificationEmail=False
        ).execute()

        # Open the newly created spreadsheet
        sheet = main_gc.open_by_key(spreadsheet_id).sheet1
        # 👇 Add column headers
        headers = ['Name', 'Amount', 'Payment_Method', 'Time']
        sheet.append_row(headers, value_input_option='USER_ENTERED')
    # Append the row
    sheet.append_row(data, value_input_option='USER_ENTERED')

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
    folder_id = folder.get('id')

    # 🔐 Give editor access to your Gmail
    permission = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': os.getenv('CLIENT_EMAIL')
    }

    drive_service.permissions().create(
        fileId=folder_id,
        body=permission,
        fields='id',
        sendNotificationEmail=True  # Set to True if you want email notification
    ).execute()

    return folder_id

def get_month_year(sheet_name):
    gc, creds = get_gsheet_client_and_creds()
    sheet = gc.open(sheet_name).sheet1
    data = sheet.get_all_records()

    month_year_counter = Counter()

    for row in data:
        timestamp = row.get("time")  # Make sure this matches your header
        if timestamp:
            try:
                dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                month_year = (dt.year, dt.strftime("%B"))
                month_year_counter[month_year] += 1
            except ValueError:
                continue

    if not month_year_counter:
        raise ValueError("No valid timestamps found to determine dominant month/year.")

    return month_year_counter.most_common(1)[0][0]


# Archive old sheet and create new one
def archive_and_create_new_sheet(old_sheet_name, new_title):
    main_creds = get_main_account_credentials()
    main_gc = gspread.authorize(main_creds)
    main_drive_service = build('drive','v3',credentials=main_creds)

    # Step 1: Setup clients
    gc, creds = get_gsheet_client_and_creds()
    old_sheet = gc.open(old_sheet_name)
    # Step 3: Rename the sheet
    old_sheet.update_title(new_title)

    # Getting folder id of Masjid-e-Abu bakr folder
    drive_service = build('drive', 'v3', credentials=creds)
    file_id = old_sheet.id
    folder_id = get_or_create_folder("Masjid-e-Abu Bakr", drive_service)

    # Step 4: Move old sheet to folder
    file = main_drive_service.files().get(fileId=file_id, fields='parents').execute()
    parents = file.get('parents', [])


    # Only move if not already in the desired folder
    if folder_id not in parents:
        previous_parents = ",".join(parents)
        main_drive_service.files().update(
            fileId=file_id,
            addParents=folder_id,
            removeParents=previous_parents,
            fields='id, parents'
        ).execute()
    else:
        print("File is already in the target folder. Skipping move operation.")

    # Step 5: Create new sheet
    new_sheet_name = get_current_sheet_name()

    # Step 2: Define metadata with MIME type and parent folder
    file_metadata = {
    'name': new_sheet_name,
    'mimeType': 'application/vnd.google-apps.spreadsheet',
    'parents': [folder_id]  # 📁 This ensures the sheet is created inside this folder
}

    # Step 3: Create the sheet (file) on Google Drive
    new_file = main_drive_service.files().create(
        body=file_metadata,
        fields='id'
    ).execute()

    time.sleep(2)
    new_sheet = new_file.get('id')

    # drive_service.files().update(
    #     fileId=new_sheet,
    #     addParents=folder_id,
    #     removeParents=previous_parents,
    #     fields='id, parents'
    # ).execute()

    # Step 6: Make sheet public (view-only)
    main_drive_service.permissions().create(
        fileId=new_sheet,
        body={"role": "reader", "type": "anyone"},
        fields="id"
    ).execute()

    # ✅ Step 6.1: Give editor access to service account
    main_drive_service.permissions().create(
        fileId=new_sheet,
        body={
            "type": "user",
            "role": "writer",
            "emailAddress": os.getenv('CLIENT_EMAIL')
        },
        fields="id"
    ).execute()


    # Open the newly created spreadsheet
    sheet = main_gc.open_by_key(new_sheet)
    worksheets = sheet.worksheets()
    if not worksheets:
        print("No worksheets found in the spreadsheet.")
    else:
        sheet = worksheets[0]
        headers = ['Name', 'Amount', 'Payment_Method', 'Time']
        sheet.append_row(headers, value_input_option='USER_ENTERED')

    # Step 7: Lock the file (prevent deletion/edit)
    main_drive_service.files().update(
        fileId=new_sheet,
        body={
            "contentRestrictions": [
                {
                    "readOnly": True,
                    "reason": "Locked to prevent accidental deletion or modification"
                }
            ]
        }).execute()
    

