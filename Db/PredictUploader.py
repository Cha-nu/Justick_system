import pandas as pd
import requests
import os
from datetime import datetime, timedelta

class PredictDataUploader:
    def __init__(self, base_dir='Data', base_url='http://localhost:2022/api'):
        self.base_dir = base_dir
        self.base_url = base_url
        self.vegetables = ['cabbage', 'onion', 'radish', 'potato', 'sweetPotato', 'tomato']
        self.rate = ['HIGH', 'SPECIAL']

    def upload_all(self):
        for veg in self.vegetables:
            self.upload_predict(veg)

    def upload_predict(self, veg):
        file_path = os.path.join(self.base_dir, f'{veg}_predict.csv')
        url = f'{self.base_url}/{veg}-predict'

        if not os.path.exists(file_path):
            print(f"🔍 파일 없음: {file_path}")
            return

        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            print(f"⚠️ CSV 읽기 오류 ({file_path}): {e}")
            return

        if 'rate' not in df.columns:
            print(f"❌ rate 컬럼 없음: {file_path}")
            return

        for rate_value in self.rate:
            filtered = df[df['rate'] == rate_value].tail(1)
            if filtered.empty:
                print(f"{veg}/{rate_value}: 마지막 예측값 데이터 없음")
                continue

            for _, row in filtered.iterrows():
                payload = {
                    "year": int(row['year']),
                    "month": int(row['month']),
                    "day": int(row['day']),
                    "grade": rate_value,
                    "averagePrice": int(row['avg_price'])
                }

                try:
                    response = requests.post(url, json=payload)
                    if response.status_code == 200:
                        print(f"✅ {veg}/{rate_value}: 성공 - {payload}")
                    else:
                        print(f"❌ {veg}/{rate_value}: 실패 - {payload}, 코드: {response.status_code}, 내용: {response.text}")
                except Exception as e:
                    print(f"🚨 {veg}/{rate_value}: 요청 오류 - {e}")



# 실행 예시
if __name__ == '__main__':
    uploader = PredictDataUploader()
    uploader.upload_all()
