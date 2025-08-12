import os, json, base64
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]

def _creds_from_env():
    raw = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not raw:
        raise RuntimeError("Missing GOOGLE_SERVICE_ACCOUNT_JSON")
    try:
        data = json.loads(raw)              # raw JSON
    except json.JSONDecodeError:
        data = json.loads(base64.b64decode(raw).decode("utf-8"))  # base64 support
    return service_account.Credentials.from_service_account_info(data, scopes=SCOPES)

def get_drive_service():
    return build("drive", "v3", credentials=_creds_from_env())

def get_or_create_subfolder(service, parent_id: str, name: str) -> str:
    q = f"mimeType='application/vnd.google-apps.folder' and name='{name}' and '{parent_id}' in parents and trashed=false"
    res = service.files().list(q=q, fields="files(id,name)", pageSize=1).execute()
    if res.get("files"):
        return res["files"][0]["id"]
    meta = {"name": name, "mimeType": "application/vnd.google-apps.folder", "parents": [parent_id]}
    created = service.files().create(body=meta, fields="id").execute()
    return created["id"]

def upload_text(service, parent_id: str, filename: str, content: str) -> str:
    media = MediaInMemoryUpload(content.encode("utf-8"), mimetype="text/plain", resumable=False)
    body = {"name": filename, "parents": [parent_id]}
    file = service.files().create(body=body, media_body=media, fields="id,webViewLink").execute()
    return file["webViewLink"]
