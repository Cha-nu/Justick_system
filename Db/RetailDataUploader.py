import pandas as pd
import requests
import os
from datetime import datetime, timedelta

class RetailDataUploader:
    def __init__(self, base_dir='/media/chan/LCW/Automation/Data', base_url='http://localhost:2022/api'):
        self.base_dir = base_dir
        self.base_url = base_url
        self.vegetables = ['cabbage', 'onion', 'radish', 'potato', 'sweetPotato', 'tomato']
        self.target_date = datetime.now() - timedelta(days=1)

    def upload_all(self):
        for veg in self.vegetables:
            self.upload_vegetable(veg)

    def upload_vegetable(self, veg):
        file_path = os.path.join(self.base_dir, f'{veg}_retail.csv')
        url = f'{self.base_url}/{veg}-retail'

        if not os.path.exists(file_path):
            print(f"🔍 파일 없음: {file_path}")
            return

        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            print(f"⚠️ CSV 읽기 오류 ({file_path}): {e}")
            return

        # 전날 날짜 필터링
        y, m, d = self.target_date.year, self.target_date.month, self.target_date.day
        filtered = df[(df['year'] == y) & (df['month'] == m) & (df['day'] == d)]

        if filtered.empty:
            print(f"📭 {veg}: 전날({y}-{m}-{d}) 데이터 없음")
            return

        for _, row in filtered.iterrows():
            payload = {
                "year": int(row['year']),
                "month": int(row['month']),
                "day": int(row['day']),
                "averagePrice": int(row['avg_price']),
                "gap": int(row['gap'])
            }

            try:
                response = requests.post(url, json=payload)
                if response.status_code == 200:
                    print(f"✅ {veg}: 성공 - {payload}")
                else:
                    print(f"❌ {veg}: 실패 - {payload}, 코드: {response.status_code}, 내용: {response.text}")
            except Exception as e:
                print(f"🚨 {veg}: 요청 오류 - {e}")

# 실행 예시
if __name__ == '__main__':
    uploader = RetailDataUploader()
    uploader.upload_all()
