import requests
import os
import subprocess
from datetime import datetime, timedelta
from dotenv import load_dotenv
from shutil import which

# Load sensitive data from .env
load_dotenv()

# DefectDojo configuration
BASE_URL = os.getenv('DEFECTDOJO_URL', 'https://dojo.nktech.online/api/v2')
API_TOKEN = os.getenv('DEFECTDOJO_API_TOKEN')
PRODUCT_ID = int(os.getenv('DEFECTDOJO_PRODUCT_ID', '1'))
ENVIRONMENT = os.getenv('DEFECTDOJO_ENVIRONMENT', 'Development')
BANDIT_REPORT_PATH = 'bandit-report.json'

# Headers
HEADERS = {
    'Authorization': f'Token {API_TOKEN}',
}

def get_active_engagement(product_id):
    url = f"{BASE_URL}/engagements/?product={product_id}&active=true"
    res = requests.get(url, headers=HEADERS, timeout=10)
    res.raise_for_status()
    engagements = res.json().get('results', [])
    return engagements[0]['id'] if engagements else None

def create_engagement(product_id):
    today = datetime.today().strftime('%Y-%m-%d')
    tomorrow = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')

    payload = {
        "name": f"Auto Bandit Scan {today}",
        "product": product_id,
        "target_start": today,
        "target_end": tomorrow,
        "active": True,
        "status": "In Progress"
    }

    response = requests.post(f"{BASE_URL}/engagements/", json=payload, headers=HEADERS, timeout=10)
    response.raise_for_status()
    print("✅ Created new engagement.")
    return response.json()['id']

def get_git_commit_id():
    try:
        git_path = which("git") or "git"
        return subprocess.check_output([git_path, 'rev-parse', 'HEAD']).decode().strip()  # nosec B603
    except subprocess.CalledProcessError:
        return "unknown"

def get_jenkins_build_number():
    return os.getenv('BUILD_NUMBER', 'manual-run')

def upload_bandit_scan(engagement_id):
    if not os.path.exists(BANDIT_REPORT_PATH):
        raise FileNotFoundError("bandit-report.json not found.")

    files = {
        'file': (BANDIT_REPORT_PATH, open(BANDIT_REPORT_PATH, 'rb'), 'application/json')
    }

    data = {
        'scan_type': 'Bandit Scan',
        'minimum_severity': 'Low',
        'active': 'true',
        'verified': 'true',
        'scan_date': datetime.today().strftime('%Y-%m-%d'),
        'engagement': engagement_id,
        'environment': ENVIRONMENT,
        'branch_tag': get_git_commit_id(),
        'build_id': get_jenkins_build_number()
    }

    print(f"📤 Uploading Bandit report to engagement {engagement_id}...")
    response = requests.post(f"{BASE_URL}/import-scan/", headers=HEADERS, files=files, data=data, timeout=20)

    if response.status_code == 201:
        print("✅ Bandit report uploaded successfully.")
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(response.text)

if __name__ == '__main__':
    try:
        engagement_id = get_active_engagement(PRODUCT_ID)
        if not engagement_id:
            engagement_id = create_engagement(PRODUCT_ID)
        upload_bandit_scan(engagement_id)
    except Exception as e:
        print(f"❗ Error: {e}")
