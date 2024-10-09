from flask import Flask, jsonify, Response
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from selenium.webdriver.firefox.options import Options as FirefoxOptions

import pytz
import pandas as pd
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Access variables
url = os.getenv('EXTRACTION_URL')
FOLDER_ID = os.getenv('GDRIVE_FOLDER_ID')
SCOPES = [os.getenv('GDRIVE_SCOPES')]

# Configure Service Account Info with variables
SERVICE_ACCOUNT_INFO = {
    "type": os.getenv('GDRIVE_TYPE'),
    "project_id": os.getenv('GDRIVE_PROJECT_ID'),
    "private_key_id": os.getenv('GDRIVE_PRIVATE_KEY_ID'),
    "private_key": os.getenv('GDRIVE_PRIVATE_KEY').replace("\\n", "\n"),  # Ensure formatting
    "client_email": os.getenv('GDRIVE_CLIENT_EMAIL'),
    "client_id": os.getenv('GDRIVE_CLIENT_ID'),
    "auth_uri": os.getenv('GDRIVE_AUTH_URI'),
    "token_uri": os.getenv('GDRIVE_TOKEN_URI'),
    "auth_provider_x509_cert_url": os.getenv('GDRIVE_AUTH_PROVIDER_CERT_URL'),
    "client_x509_cert_url": os.getenv('GDRIVE_CLIENT_CERT_URL')
}

app = Flask(__name__)
# # URL of the website
# url = 'https://eal.iitk.ac.in'

# # Google Drive configuration
# # SERVICE_ACCOUNT_FILE = "ee677project-f6a83a843635.json"
# SERVICE_ACCOUNT_INFO = {
#   "type": "service_account",
#   "project_id": "ee677project",
#   "private_key_id": "f6a83a843635c8d894cdad6bcd00e0b0238d38c6",
#   "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDLZ+y002VxCLeh\nBSUMTfbARjqGzCqn8B+TtvqirMWq8mJCHZoS89cStFEwLV6xqBx1XtfDeEXgcxiP\ng/c3uPscdWaUpTUtPWE6AsninmR6nB/KLfBE9UWPILSo9FohTHAhMjmj/DS6S3zd\nQVbTReZVoUGyGTuXJQb/N8mFXj1V12U7Sp/hfmvY8tkIi9Mk3LW8n2IrjWbIgL+k\nO8MxLC0u2AQ/PTcnA6A2JAZz5VBhtkkOBgEi0kFTfoasJswZYgQDwp+asbZGaH8q\nx4B+unpGd8DpbxmYSMu8sUFSc11c3MNxXZlkE9Ii160IwAMEJv/7LEFxAqEy+2eu\nfw+hIE/lAgMBAAECggEAHfF66hUN+OQvTBfwH+3rkNswdcmLz1R3rDd35rIHw1Dn\n4BMa1wa9tuDZQX4G/kuLgke8/DyHZNxCAFaNR88GaxET/HaO682pCMYs/BxpxEGZ\neG+SJZn0bHaEbIl+1H9mflc2HwrbTurFQzkBfsaVJYPrTObkBoMKkvrzwptgl3Mu\nFwmXHWiTv2359baaTtq+jitSJ5yeyo1/Biwvo+BjMO6kmBCjdfHOsCMTUbSfxPvw\nft4JCy1AIW0LoqPeEqVCtNAE3HL0RMLc0/ubUQIvY4Xln8D2d5bZarQmtNvuL+Ec\n/YBt58ttLclkDqQnRX+aarMShBDXUc8W59mJJCGIXQKBgQD9qdGFKX5gleMD1Tty\n3KV6aWf/DxU0s7/S3xUyRBINdRG9BWBsQrq8kEp4xzkaOsJR3mGprvpljbh4YqdV\nL5nD5GaeBhFk30ef0tvYbrR/zidotzCVhPEIxkTtjOfn9eQTEOwehOox1njkHv4b\naL0KtYSyajyxGA+q1OBDRkpXZwKBgQDNR5c1Z3CDMxhbneqUKdT2StfscuiWOmPj\nE3MZB+tVDWh7JRjfD3w8NsovuqGuqFhO0X/rnircQj6IErCh6aZJCUol4rbso7+U\nbj4Xr/91PLDvwVlfSthwJCwFsmMo4W5SWybV1hi3HNlKtBAYuT4SVCEuIEpRt/zj\nBs5wASXK0wKBgQCXIQQpuC0JUoPslrBSoM8efYpuVggmXCmfczXnutKene8xlPB7\nz8395mHYT6nfzL5VlI7PT+bzdlo/r1dO04tjQMM6xxa56KV9vV0qN9rmgmbMZshV\nbN1GgwoyFc9dTgzSpzRmgn4dr1BbaXOv1Nk8diVXPyBlypYbC7WJn2lPZQKBgQCq\np9CSChtkRw8B40eHwzsTQec9381yTrqJpbqy3X2L6Kiqb428qu/6UwZFJZ+SRsub\nQtlYtNYm5D99+iOzhz3BTCLDWjX+hqcXK4sdQChce4cQ2qmE6gEDQV8DoWiELNz9\nRGAFt4Y2fJo8W3NiSmXK8Pvgj+GZDB8FUbw/KwUTFwKBgQD5teyf9KuGbYsd+YZi\naM7JPFRpezVbq9DEGNhkZ5RTkLkwxTTT2+t/mQ8osiIwDhSyCxt5Fo3epaY9g2RZ\nGNVT7eSY7UR8ryBY3Ahxaf0dpZD1T6gL2vD742FyhqGwg5hP0z0EjmXLt9WdfAkz\nTOxUmogvW720rgY2nKP62F5aeQ==\n-----END PRIVATE KEY-----\n",
#   "client_email": "ee677project@ee677project.iam.gserviceaccount.com",
#   "client_id": "107150382352112745087",
#   "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#   "token_uri": "https://oauth2.googleapis.com/token",
#   "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#   "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/ee677project%40ee677project.iam.gserviceaccount.com",
#   "universe_domain": "googleapis.com"
# }

# SCOPES = ['https://www.googleapis.com/auth/drive.file']
# FOLDER_ID = '1yoGBP0vAxieJfdbew66Mtt_0j7KNRzxE'  # Replace with your folder ID
# Function to upload a file to Google Drive
def upload_to_drive(file_name, new_df):
    credentials = service_account.Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)
    # Check if the file already exists in Google Drive by searching with the file name
    results = service.files().list(q=f"'{FOLDER_ID}' in parents and name='{file_name}'", spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])

    if len(items) > 0:
        # File exists, get its ID and download the file as .xlsx
        file_id = items[0]['id']

        # Download the file as an Excel file
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO(request.execute())
        
        # Load the existing data from the file into a DataFrame
        existing_df = pd.read_excel(fh)

        # Append new data to the existing data
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)

        # Save the updated data locally
        combined_df.to_excel(file_name, index=False)

        # Delete the existing file on Drive
        service.files().delete(fileId=file_id).execute()

        # Upload the updated file as a new file
        file_metadata = {'name': file_name, 'parents': [FOLDER_ID]}
        media = MediaFileUpload(file_name, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    else:
        # If the file doesn't exist, create a new one and upload it
        new_df.to_excel(file_name, index=False)
        file_metadata = {'name': file_name, 'parents': [FOLDER_ID]}
        media = MediaFileUpload(file_name, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()



# Function to round time to the nearest 15-minute interval
def round_to_15_minutes(dt):
    minutes = (dt.minute // 15) * 15
    return dt.replace(minute=minutes, second=0, microsecond=0)

# Function to extract data
def extract_data():
    while True:
        # driver = webdriver.Chrome()  # Initialize the Chrome driver here
        options = FirefoxOptions()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        try:
            # Open the website
            driver.get(url)
            attempts = 0
            india_total_demand = None
            while attempts < 50:
                try:
                    india_total_demand = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "india_total_demand"))
                    )
                    demand_last_updated = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "india_total_demand_last_updated"))
                    )
                    if india_total_demand.text.strip() and demand_last_updated.text.strip():
                        break
                except:
                    print("Element not found or not populated yet.")
                time.sleep(5)
                attempts += 1

            if india_total_demand and india_total_demand.text.strip() and demand_last_updated and demand_last_updated.text.strip():
                demand_text = india_total_demand.text.strip()
                last_updated_text = demand_last_updated.text.strip()
                if last_updated_text == "just now":
                    last_updated_text = "0 minutes ago"
                minutes_ago = int(''.join(filter(str.isdigit, last_updated_text)))
                current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
                adjusted_time = current_time - timedelta(minutes=minutes_ago)
                rounded_time = round_to_15_minutes(adjusted_time)
                end_time = rounded_time + timedelta(minutes=15)
                data = {
                    "Start Time": [rounded_time.strftime('%Y-%m-%d %H:%M:%S')],
                    "End Time": [end_time.strftime('%Y-%m-%d %H:%M:%S')],
                    "Demand": [demand_text]
                }
                df = pd.DataFrame(data)
                file_name = f"demand_data_{adjusted_time.strftime('%Y-%m-%d')}.xlsx"
                # if os.path.exists(file_name):
                #     with pd.ExcelWriter(file_name, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                #         start_row = writer.sheets['Sheet1'].max_row
                #         df.to_excel(writer, sheet_name='Sheet1', index=False, header=False, startrow=start_row)
                # else:
                #     df.to_excel(file_name, index=False)

                        # Upload the extracted data to Google Drive
                upload_to_drive(file_name, df)
                print("Data extraction completed successfully.")
            else:
                print("Data extraction failed.")
        
        except Exception as e:
            print(f"Error: {e}")
        
        finally:
            driver.quit()
        
        # Wait for 180 seconds before running again
        time.sleep(25)

# Flask route to trigger the extraction
@app.route('/extract', methods=['GET'])
def extract_route():
    def generate():
        while True:
            extract_data()
            yield f"data: Running extraction at {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    return Response(generate(), mimetype='text/event-stream')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
















