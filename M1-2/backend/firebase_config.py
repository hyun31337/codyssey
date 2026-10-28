import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

if not firebase_admin._apps:
    # 1. Render 환경 변수(FIREBASE_CREDENTIALS)에 JSON 문자열이 통째로 들어있는지 확인
    firebase_json_str = os.getenv("FIREBASE_CREDENTIALS")
    
    if firebase_json_str:
        # 2. Render 환경 변수의 JSON 문자열을 딕셔너리로 파싱하여 인증
        cred_dict = json.loads(firebase_json_str)
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    else:
        # 3. 로컬 개발 환경: 기존처럼 파일 경로(service_account.json)를 사용
        cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "service_account.json")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

db = firestore.client()