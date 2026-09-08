import os
import requests

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def run_bot():
    # 1. '상태'가 '요청'인 데이터 필터링
    query_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {
        "filter": {
            "property": "상태", # 노션 속성 이름과 일치해야 함
            "status": {
                "equals": "요청"
            }
        }
    }
    
    res = requests.post(query_url, headers=headers, json=payload)
    results = res.json().get("results", [])

    if not results:
        print("새로운 요청이 없습니다.")
        return

    # 2. 슬랙 전송
    for page in results:
        title_prop = page["properties"].get("이름", {}).get("title", [])
        title = title_prop[0]["text"]["content"] if title_prop else "제목 없음"
        page_url = page["url"]

        slack_payload = {
            "text": f"🔔 *[새로운 요청]*\n*아젠다:* {title}\n*링크:* {page_url}"
        }
        requests.post(SLACK_WEBHOOK_URL, json=slack_payload)
        print(f"전송 완료: {title}")

if __name__ == "__main__":
    run_bot()
