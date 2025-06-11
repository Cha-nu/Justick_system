import pandas as pd
from .Predictor28 import Predictor28
from .Predictor7 import Predictor7
from .Predictor import Predictor
import datetime

class PredictionManager:
    def __init__(self, items=None, grades=None, base_dir="/media/chan/LCW/Automation/Data", model_dir="/media/chan/LCW/Automation/Model/model"):
        self.items = items or ["cabbage", "onion", "potato", "radish", "sweetPotato", "tomato"]
        self.grades = grades or ["HIGH", "SPECIAL"]
        self.base_dir = base_dir
        self.model_dir = model_dir

    def shift_dates_after_sundays(df):
        df = df.sort_values(by=["year", "month", "day"]).reset_index(drop=True)
        new_rows = []
        add_days = 0

        for i in range(len(df)):
            row = df.iloc[i].copy()
            original_date = datetime.date(int(row["year"]), int(row["month"]), int(row["day"]))
            shifted_date = original_date + datetime.timedelta(days=add_days)

            row["year"] = shifted_date.year
            row["month"] = shifted_date.month
            row["day"] = shifted_date.day

            new_rows.append(row)

            if shifted_date.weekday() == 5:  # 토요일이면 이후 날짜를 하루씩 미룸
                add_days += 1

        return pd.DataFrame(new_rows)

    def batch(self):
        cutoff_date = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        # cutoff_date = "2025-06-02"
        for item in self.items:
            df = pd.read_csv(f"{self.base_dir}/{item}_separated.csv")

            for grade in self.grades:
                print(f"Batch processing {item} with grade {grade}...")

                # Step 1: 28일 예측
                model28 = Predictor28()
                model28.fit(df, cutoff_date=cutoff_date, months=[4, 5, 6], rate=grade)
                pred_28 = pd.DataFrame(model28.post_latest())
                model28.save(grade, item, self.model_dir)

                # Step 2: 앞쪽 7일간 Predictor7 결과로 덮어쓰기
                model7 = Predictor7()
                model7.fit(df, cutoff_date=cutoff_date, months=[4, 5, 6], rate=grade)
                pred_7 = pd.DataFrame(model7.post_latest())
                pred_28.iloc[:7] = pred_7
                model7.save(grade, item, self.model_dir)

                # Step 3: 가장 앞 1일을 Predictor로 덮어쓰기
                model1 = Predictor()
                model1.fit(df, cutoff_date=cutoff_date, months=list(range(1, 13)), rate=grade)
                pred_1 = pd.Series(model1.post_latest())
                pred_28.iloc[0] = pred_1
                model1.save(grade, item, self.model_dir)

                # 저장할 path 설정
                path = f"{self.base_dir}/{item}_predict.csv"

                # 컬럼 재정렬 및 변환: price → avg_price
                pred_28["avg_price"] = pred_28["price"]
                pred_28 = pred_28[["year", "month", "day", "avg_price", "rate"]]

                # 예측 값에서 일요일 만날때마다 +1씩하고 총 28개의 데이터를 남긴다.
                pred_28 = self.filter_sunday_and_trim(pred_28)

                try:
                    existing = pd.read_csv(path)
                except FileNotFoundError:
                    existing = pd.DataFrame(columns=["year", "month", "day", "avg_price", "rate"])

                # 기존 데이터와 새 예측 결합, 중복 날짜+등급 기준으로 최신 예측으로 덮어쓰기
                combined = pd.concat([existing, pred_28], ignore_index=True)
                combined = combined.drop_duplicates(subset=["year", "month", "day", "rate"], keep="last")

                combined = combined.sort_values(by=["rate", "year", "month", "day"]).reset_index(drop=True)

                # 저장
                combined.to_csv(path, index=False)
                print(f"Saved predictions for {item} with grade {grade} to {path}")

    def continuous(self):
        for item in self.items:
            df = pd.read_csv(f"{self.base_dir}/{item}_separated.csv")

            for grade in self.grades:
                print(f"Continuous processing {item} with grade {grade}...")

                # Step 1: 28일 예측
                model28 = Predictor28()
                model28.load(grade, item, self.model_dir)
                model28.update_one_day(df, months=[4, 5, 6], rate=grade)
                pred_28 = pd.DataFrame(model28.post_latest())
                model28.save(grade, item, self.model_dir)

                # Step 2: 앞쪽 7일 Predictor7
                model7 = Predictor7()
                model7.load(grade, item, self.model_dir)
                model7.update_one_day(df, months=[4, 5, 6], rate=grade)
                pred_7 = pd.DataFrame(model7.post_latest())
                pred_28.iloc[:7] = pred_7
                model7.save(grade, item, self.model_dir)

                # Step 3: 가장 앞 1일 Predictor
                model1 = Predictor()
                model1.load(grade, item, self.model_dir)
                model1.update_one_day(df, months=list(range(1, 13)), rate=grade)
                pred_1 = pd.Series(model1.post_latest())
                pred_28.iloc[0] = pred_1
                model1.save(grade, item, self.model_dir)

                # 컬럼 재정렬 및 변환
                pred_28["avg_price"] = pred_28["price"]
                pred_28 = pred_28[["year", "month", "day", "avg_price", "rate"]]

                # 예측 값에서 일요일 만날때마다 +1씩하고 총 28개의 데이터를 남긴다. 
                red_28 = self.filter_sunday_and_trim(pred_28)

                # 기존 파일 불러오기
                path = f"{self.base_dir}/{item}_predict.csv"
                try:
                    existing = pd.read_csv(path)
                except FileNotFoundError:
                    existing = pd.DataFrame(columns=["year", "month", "day", "avg_price", "rate"])

                # 기존 + 새로운 예측 병합 (중복 날짜+등급 제거, 최신 유지)
                combined = pd.concat([existing, pred_28], ignore_index=True)
                combined = combined.drop_duplicates(subset=["year", "month", "day", "rate"], keep="last")

                combined = combined.sort_values(by=["rate", "year", "month", "day"]).reset_index(drop=True)

                # 저장
                combined.to_csv(path, index=False)
                print(f"Updated predictions for {item} with grade {grade} to {path}")


if __name__ == "__main__":
    manager = PredictionManager()
    # manager.batch()

    # 매일 아침 continuous 실행
    manager.continuous()
