import csv
import requests
import os
from datetime import datetime, timedelta

class DailyUploader:
    def __init__(self, base_dir='/media/chan/LCW/Automation/Data', base_url='http://localhost:2022/api'):
        self.base_dir = base_dir
        self.base_url = base_url
        self.vegetables = ['cabbage', 'onion', 'radish', 'potato', 'sweetPotato', 'tomato']
        self.grades = ['HIGH', 'SPECIAL']
        self.target_date = datetime.now() - timedelta(days=1)

    def run_all(self):
        for veg in self.vegetables:
            for grade in self.grades:
                self.upload_yesterday_data(veg, grade)

    def upload_yesterday_data(self, veg, grade):
        file_path = os.path.join(self.base_dir, f'{veg}_separated.csv')
        url = f"{self.base_url}/{veg}"

        if not os.path.exists(file_path):
            print(f"🔍 파일 없음: {file_path}")
            return

        try:
            with open(file_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except Exception as e:
            print(f"⚠️ CSV 읽기 실패: {file_path}, 이유: {e}")
            return

        found = False
        latest_row = None
        latest_row_date = None

        for row in rows:
            try:
                row_date = datetime(year=int(row["year"]), month=int(row["month"]), day=int(row["day"]))

                # 등급 일치하는 가장 마지막 행 저장
                if row["rate"] == grade:
                    if (latest_row_date is None) or (row_date > latest_row_date):
                        latest_row_date = row_date
                        latest_row = row

                    if row_date.date() == self.target_date.date():
                        # 전날 데이터 존재
                        payload = {
                            "year": int(row["year"]),
                            "month": int(row["month"]),
                            "day": int(row["day"]),
                            "intake": int(row["intake"]),
                            "averagePrice": int(row["avg_price"]),
                            "grade": row["rate"],
                            "gap": int(row['gap'])
                        }

                        response = requests.post(url, json=payload)
                        if response.status_code == 200:
                            print(f"✅ {veg} ({grade}): 전송 성공 - {payload}")
                        else:
                            print(f"❌ {veg} ({grade}): 전송 실패 - 코드: {response.status_code}, 내용: {response.text}")
                        found = True
                        break
            except Exception as e:
                print(f"🚨 변환/요청 실패: {row}, 에러: {e}")

        # 전날 데이터가 없을 때 → 마지막 데이터로 생성
        if not found and latest_row:
            try:
                fallback_payload = {
                    "year": self.target_date.year,
                    "month": self.target_date.month,
                    "day": self.target_date.day,
                    "intake": int(latest_row["intake"]),
                    "averagePrice": int(latest_row["avg_price"]),
                    "grade": latest_row["rate"],
                    "gap": 0
                }

                response = requests.post(url, json=fallback_payload)
                if response.status_code == 200:
                    print(f"🟡 {veg} ({grade}): 보간 전송 성공 - {fallback_payload}")
                else:
                    print(f"🟥 {veg} ({grade}): 보간 전송 실패 - 코드: {response.status_code}, 내용: {response.text}")
            except Exception as e:
                print(f"⚠️ 보간 실패: {latest_row}, 에러: {e}")
        elif not found:
            print(f"⛔ {veg} ({grade}): 전날 데이터도 없고 보간도 불가")

# 실행
if __name__ == '__main__':
    uploader = DailyUploader()
    uploader.run_all()
