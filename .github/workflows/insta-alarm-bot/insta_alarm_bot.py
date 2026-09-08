import os
import requests
import json
from datetime import datetime, timedelta, timezone

# GitHub Secrets에서 가져올 환경 변수들
NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("DATABASE_ID")
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def check_and_send_insta_alarm():
    # 1. 한국 시간(KST) 기준으로 오늘 날짜에 10일을 더해 타겟 날짜(YYYY-MM-DD) 계산
    KST = timezone(timedelta(hours=9))
    today = datetime.now(KST)
    target_date = (today + timedelta(days=10)).strftime("%Y-%m-%d")
    
    print(f"조회 대상 날짜 (D-10): {target_date}")

    # 2. 노션 데이터베이스 필터링: 날짜가 정확히 10일 뒤(target_date)인 항목만 가져옴
    query_url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    query_payload = {
        "filter": {
            "property": "날짜",  # 🚨 노션 캘린더의 날짜 속성 이름과 똑같이 맞춰주세요!
            "date": {
                "equals": target_date
            }
        }
    }
    
    response = requests.post(query_url, headers=headers, data=json.dumps(query_payload))
    results = response.json().get("results", [])

    if not results:
        print(f"{target_date} 에 업로드 예정인 게시물이 없습니다.")
        return

    # 3. 가져온 데이터를 슬랙으로 전송
    for page in results:
        # 노션 페이지 제목 가져오기
        title_prop = page["properties"].get("이름", {}).get("title", [])
        if not title_prop:
            title_prop = page["properties"].get("Name", {}).get("title", [])
            
        agenda_title = title_prop[0]["text"]["content"] if title_prop else "제목 없음"
        page_url = page["url"]

        # 슬랙 웹훅으로 데이터 전송 (미리 만들어둔 insta_alarm 변수 활용)
        slack_payload = {
            "insta_alarm": f"🚨 *[업로드 D-10 알림]*\n10일 뒤 업로드 예정인 콘텐츠가 있습니다!\n\n*콘텐츠명:* {agenda_title}\n*예정일:* {target_date}\n*노션 링크:* {page_url}"
        }
        
        slack_res = requests.post(SLACK_WEBHOOK_URL, json=slack_payload)
        
        if slack_res.status_code == 200:
            print(f"✅ 슬랙 전송 완료: {agenda_title}")
        else:
            print(f"❌ 슬랙 전송 실패: {slack_res.text}")

if __name__ == "__main__":
    check_and_send_insta_alarm()
