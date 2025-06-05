import os
import pandas as pd

class PreprocessingDB:
    def __init__(self, base_dir='Data'):
        self.base_dir = base_dir
        self.output_dir = base_dir
        self.grade_ratio = {
            '특': ('SPECIAL', 0.05),
            '상': ('HIGH', 0.35),
        }
        self.vegetables = ['cabbage', 'onion', 'potato', 'radish', 'sweetPotato', 'tomato']
        os.makedirs(self.output_dir, exist_ok=True)
    
    def process(self):
        for veg in self.vegetables:
            try:
                price_file = os.path.join(self.base_dir, f'{veg}Price.csv')
                intake_file = os.path.join(self.base_dir, f'{veg}Intake.csv')
                output_path = os.path.join(self.output_dir, f'{veg}_separated.csv')

                if not os.path.exists(price_file) or not os.path.exists(intake_file):
                    print(f"[SKIP] 파일 없음: {veg}")
                    continue

                try:
                    price_df = pd.read_csv(price_file)
                    intake_df = pd.read_csv(intake_file)
                except Exception as e:
                    print(f"[ERROR] {veg} 파일 읽기 실패: {e}")
                    continue

                if veg == 'onion':
                    price_df = price_df[price_df['단위'] == '1키로']
                elif veg == 'tomato':
                    price_df = price_df[price_df['단위'] == '5키로상자']

                filtered = price_df[price_df['등급명'].isin(self.grade_ratio)].copy()
                filtered['avg_price'] = (
                    filtered['평균가격'].astype(str).str.replace(',', '', regex=False).astype(int)
                )
                filtered = filtered[filtered['avg_price'] != 0]
                filtered['rate'] = filtered['등급명'].map(lambda x: self.grade_ratio[x][0])
                filtered['비율'] = filtered['등급명'].map(lambda x: self.grade_ratio[x][1])

                intake_df = intake_df[['DATE', '총반입량']].copy()
                intake_df.rename(columns={'총반입량': 'total_intake'}, inplace=True)
                merged = pd.merge(filtered, intake_df, on='DATE', how='inner')

                merged['intake'] = (merged['total_intake'] * merged['비율']).round().astype(int)
                merged['DATE'] = pd.to_datetime(merged['DATE'], errors='coerce')
                merged = merged.dropna(subset=['DATE'])
                merged['year'] = merged['DATE'].dt.year
                merged['month'] = merged['DATE'].dt.month
                merged['day'] = merged['DATE'].dt.day

                merged.sort_values(['rate', 'DATE'], inplace=True)

                new_df = merged[['year', 'month', 'day', 'intake', 'avg_price','rate']]
                new_df = new_df.sort_values(['year', 'month', 'day', 'rate'])
                

                # 기존 데이터 있으면 불러와서 합치기
                if os.path.exists(output_path):
                    old_df = pd.read_csv(output_path)
                    # 기존 데이터 마지막 행 추출
                    for rate in new_df['rate'].unique():
                        last_old = old_df[old_df['rate'] == rate].sort_values(['year', 'month', 'day']).tail(1)
                        first_new = new_df[new_df['rate'] == rate].sort_values(['year', 'month', 'day']).head(1)
                        if not last_old.empty and not first_new.empty:
                            gap_val = first_new['avg_price'].values[0] - last_old['avg_price'].values[0]
                            new_df.loc[(new_df['rate'] == rate) & (new_df['year'] == first_new['year'].values[0]) &
                                    (new_df['month'] == first_new['month'].values[0]) &
                                    (new_df['day'] == first_new['day'].values[0]), 'gap'] = gap_val
                    # 신규 데이터 나머지는 diff()
                    for rate in new_df['rate'].unique():
                        temp = new_df[new_df['rate'] == rate].sort_values(['year', 'month', 'day'])
                        temp['gap'] = temp['avg_price'].diff().fillna(0).astype(int)
                        # 이미 gap값이 있으면 유지
                        new_df.loc[temp.index, 'gap'] = new_df.loc[temp.index, 'gap'].fillna(temp['gap'])
                    # 합치기
                    total_df = pd.concat([old_df, new_df], ignore_index=True)
                    total_df = total_df.drop_duplicates(subset=['year', 'month', 'day', 'rate'], keep='last')
                    total_df = total_df.sort_values(['rate', 'year', 'month', 'day'])
                else:
                    # 첫 데이터(혹은 전체 처음)
                    for rate in new_df['rate'].unique():
                        temp = new_df[new_df['rate'] == rate].sort_values(['year', 'month', 'day'])
                        temp['gap'] = temp['avg_price'].diff().fillna(0).astype(int)
                        new_df.loc[temp.index, 'gap'] = temp['gap']
                    total_df = new_df.sort_values(['rate', 'year', 'month', 'day'])

                total_df = total_df[['year', 'month', 'day', 'intake', 'avg_price', 'gap', 'rate']]
                total_df["gap"] = total_df["gap"].astype(int)
                total_df.to_csv(output_path, index=False)

                print(f"[DONE] {veg} 저장 완료 -> {output_path}")

                try:
                    os.remove(price_file)
                    os.remove(intake_file)
                    print(f"[DELETE] {price_file}, {intake_file} 삭제 완료")
                except Exception as e:
                    print(f"[ERROR] 파일 삭제 실패: {e}")
            except Exception as e:
                print(f"[ERROR] {veg} 처리 중 오류 발생: {e}")
                continue

    def preprocess_retail_data(self):
        for veg in self.vegetables:
            try:
                variety_filter = {
                    'cabbage': '배추(전체)',
                    'onion': '양파(전체)',
                    'potato': '감자(전체)',
                    'radish': '무(전체)',
                    'sweetPotato': '고구마(전체)',
                    'tomato': '토마토(전체)',
                }

                file_path = os.path.join(self.base_dir, f"{veg}Retail.csv")
                output_path = os.path.join(self.output_dir, f"{veg}_retail.csv")

                if not os.path.exists(file_path):
                    print(f"[SKIP] 파일 없음: {file_path}")
                    continue

                df = pd.read_csv(file_path)
                df = df[df['품종'] == variety_filter[veg]]
                df = df[df['등급'] == '상품'].copy()
                df['avg_price'] = pd.to_numeric(df['평균가격'], errors='coerce').round(-1).astype('Int64')
                df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
                df = df.dropna(subset=['DATE'])
                df['year'] = df['DATE'].dt.year
                df['month'] = df['DATE'].dt.month
                df['day'] = df['DATE'].dt.day

                new_df = df[['year', 'month', 'day', 'avg_price']].sort_values(['year', 'month', 'day'])

                if os.path.exists(output_path):
                    old_df = pd.read_csv(output_path)
                    # 기존 데이터 마지막 행, 신규 데이터 첫 행 비교
                    last_old = old_df.sort_values(['year', 'month', 'day']).tail(1)
                    first_new = new_df.sort_values(['year', 'month', 'day']).head(1)
                    if not last_old.empty and not first_new.empty:
                        gap_val = first_new['avg_price'].values[0] - last_old['avg_price'].values[0]
                        new_df.loc[(new_df['year'] == first_new['year'].values[0]) &
                                (new_df['month'] == first_new['month'].values[0]) &
                                (new_df['day'] == first_new['day'].values[0]), 'gap'] = gap_val
                    # 신규 데이터 나머지는 diff()
                    temp = new_df.sort_values(['year', 'month', 'day'])
                    temp['gap'] = temp['avg_price'].diff().fillna(0).astype(int)
                    new_df.loc[temp.index, 'gap'] = new_df.loc[temp.index, 'gap'].fillna(temp['gap'])
                    # 합치기
                    total_df = pd.concat([old_df, new_df], ignore_index=True)
                    total_df = total_df.drop_duplicates(subset=['year', 'month', 'day'], keep='last')
                    total_df = total_df.sort_values(['year', 'month', 'day'])
                else:
                    temp = new_df.sort_values(['year', 'month', 'day'])
                    temp['gap'] = temp['avg_price'].diff().fillna(0).astype(int)
                    new_df.loc[temp.index, 'gap'] = temp['gap']
                    total_df = new_df.sort_values(['year', 'month', 'day'])

                total_df = total_df[['year', 'month', 'day', 'avg_price', 'gap']]
                total_df["gap"] = total_df["gap"].astype(int)
                total_df.to_csv(output_path, index=False)
                print(f"[DONE] 전처리 및 저장 완료 -> {output_path}")

                # 원본 파일 삭제
                try:
                    os.remove(file_path)
                    print(f"[DELETE] 원본 파일 삭제 완료 -> {file_path}")
                except Exception as e:
                    print(f"[ERROR] 파일 삭제 실패: {e}")

            except Exception as e:
                print(f"[ERROR] {veg} 처리 중 오류 발생: {e}")
                continue

      

# 실행
if __name__ == '__main__':
    processor = PreprocessingDB()
    processor.process()
    processor.preprocess_retail_data()
