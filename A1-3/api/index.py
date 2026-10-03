from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
            try:
                # api/ 폴더의 상위 디렉토리에 있는 index.html 파일 경로 찾기
                current_dir = os.path.dirname(os.path.abspath(__file__))
                index_path = os.path.join(current_dir, '..', 'index.html')

                if os.path.exists(index_path):
                    with open(index_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(html_content.encode('utf-8'))
                else:
                    self.send_response(404)
                    self.send_header('Content-Type', 'text/plain; charset=utf-8')
                    self.end_headers()
                    self.wfile.write("index.html 파일을 찾을 수 없습니다.".encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(f"서버 오류 발생: {str(e)}".encode('utf-8'))

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))

            date = data.get('date', '')
            location = data.get('location', '전국')
            interest = data.get('interest', '일반 여행')

            openai_api_key = os.environ.get("OPENAI_API_KEY")
            openai_base_url = os.environ.get("OPENAI_BASE_URL", "https://copa.codyssey.kr/v1")
            naver_client_id = os.environ.get("NAVER_CLIENT_ID")
            naver_client_secret = os.environ.get("NAVER_CLIENT_SECRET")

            if not openai_api_key:
                self.send_error_response(500, "서버 설정 오류: OpenAI API 키가 설정되지 않았습니다.")
                return

            # 네이버 검색 API 연동
            search_query = f"{date} {location} {interest} 축제"
            enc_text = urllib.parse.quote(search_query)
            naver_url = f"https://openapi.naver.com/v1/search/blog.json?query={enc_text}&display=3"

            naver_results_text = "관련 검색 정보를 불러오지 못했습니다."
            if naver_client_id and naver_client_secret:
                try:
                    naver_req = urllib.request.Request(naver_url)
                    naver_req.add_header("X-Naver-Client-Id", naver_client_id)
                    naver_req.add_header("X-Naver-Client-Secret", naver_client_secret)
                    
                    with urllib.request.urlopen(naver_req) as naver_res:
                        if naver_res.getcode() == 200:
                            naver_data = json.loads(naver_res.read().decode('utf-8'))
                            items = naver_data.get('items', [])
                            summaries = []
                            for item in items:
                                clean_title = item['title'].replace('<b>', '').replace('</b>', '')
                                clean_desc = item['description'].replace('<b>', '').replace('</b>', '')
                                summaries.append(f"- {clean_title}: {clean_desc}")
                            if summaries:
                                naver_results_text = "\n".join(summaries)
                except Exception as ne:
                    print(f"Naver Search API Error: {ne}")

            # OpenAI 프롬프트 구성
            prompt = (
                f"사용자가 선택한 날짜({date}), 지역({location}), 관심사({interest})를 바탕으로 "
                f"해당 주간에 열리는 대한민국 지역 축제 2가지를 추천해줘.\n\n"
                f"[참고할 만한 실시간 웹/블로그 검색 데이터]\n{naver_results_text}\n\n"
                "위 정보를 참고하여 각 축제의 이름, 추천 이유, 대략적인 일정을 친절하고 깔끔한 텍스트 형태로 작성해줘."
            )

            req_url = f"{openai_base_url.rstrip('/')}/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai_api_key}"
            }
            payload = {
                "model": "gpt-5-mini",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }

            req = urllib.request.Request(
                req_url, 
                data=json.dumps(payload).encode('utf-8'), 
                headers=headers, 
                method="POST"
            )

            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                ai_message = res_data['choices'][0]['message']['content']

            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            response_body = json.dumps({"recommendation": ai_message}, ensure_ascii=False)
            self.wfile.write(response_body.encode('utf-8'))

        except Exception as e:
            self.send_error_response(500, f"처리 중 오류가 발생했습니다: {str(e)}")

    def send_error_response(self, status_code, message):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        error_body = json.dumps({"recommendation": message}, ensure_ascii=False)
        self.wfile.write(error_body.encode('utf-8'))