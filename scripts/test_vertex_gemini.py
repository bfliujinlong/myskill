import google.auth
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import urllib.request
import json

# 刷新 token
credentials = service_account.Credentials.from_service_account_file(
    '/home/bfyalong/.hermes/credentials/gemini-sa.json',
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)
credentials.refresh(Request())
print('Token:', credentials.token[:30] + '...')

# 通过 Vertex AI 调用
url = 'https://us-central1-aiplatform.googleapis.com/v1/projects/cryptic-bivouac-471612-t0/locations/us-central1/publishers/google/models/gemini-2.0-flash:generateContent'
headers = {
    'Authorization': f'Bearer {credentials.token}',
    'Content-Type': 'application/json'
}
data = json.dumps({'contents': [{'parts': [{'text': '你好'}]}]}).encode()

req = urllib.request.Request(url, data=data, headers=headers, method='POST')
try:
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        print('✅ Vertex AI 调用成功！')
        print('回答:', result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'N/A'))
except Exception as e:
    print('❌ Vertex AI 调用失败:', str(e))
