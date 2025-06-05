from Crawler.crawler import Crawler
from Preprocess.DBProcessor import PreprocessingDB
from Db.DailyUploader import DailyUploader
from Db.RetailDataUploader import RetailDataUploader
from Db.PredictUploader import PredictDataUploader
from Model.PredictorManager import PredictionManager
import playsound

if __name__ == "__main__":
    try:
        Crawler().run()
        PreprocessingDB().process()
        PreprocessingDB().preprocess_retail_data()
        DailyUploader().run_all()
        RetailDataUploader().upload_all()

        # continuous 학습 후 db에 올림
        PredictionManager().continuous()
        PredictDataUploader().upload_all()

    # 사운드 재생
        try:
            playsound.playsound("/media/chan/LCW/Automation/Sound/KirbyVictoryDance.mp3")
        except Exception as e:
            print(f"사운드 재생 실패: {e}")
    except Exception as e:
        print(f"로직 실패: {e}")
        try:
            playsound.playsound("/media/chan/LCW/Automation/Sound/missionfailed.mp3")
        except Exception as e:
            print(f"사운드 재생 실패: {e}")
