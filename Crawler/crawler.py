from selenium.webdriver.firefox.service import Service
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from datetime import datetime, timedelta
import time
import os
import pandas as pd
from pathlib import Path
import traceback
import sys
import playsound

class Crawler:
    def __init__(self):
        self.DOWNLOAD_DIR = "/media/chan/LCW/Automation/Data"
        self.options = Options()
        # self.options.headless = True
        self.options.set_preference("browser.download.folderList", 2)
        self.options.set_preference("browser.download.dir", self.DOWNLOAD_DIR)
        self.options.set_preference("browser.download.useDownloadDir", True)
        self.options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,text/csv")
        self.options.set_preference("browser.download.manager.showWhenStarting", False)
        self.options.set_preference("pdfjs.disabled", True)

    def select_dropdown(self, driver, index, value):
        WebDriverWait(driver, 20).until(
        EC.invisibility_of_element_located((By.CLASS_NAME, "qv-ui-blocker"))
    )
        dropdowns = driver.find_elements(By.CLASS_NAME, "qui-select")
        select = Select(dropdowns[index])
        select.select_by_visible_text(value)

    def try_decode(self, val):
        if isinstance(val, str):
            try:
                return val.encode("latin1").decode("euc-kr")
            except:
                return val
        return val

    def convert_xlsx_to_utf8_csv(self, xlsx_path, csv_path):
        df = pd.read_excel(xlsx_path, engine='openpyxl')
        df.columns = [str(col) for col in df.columns]
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].apply(lambda x: self.try_decode(x))
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"변환 완료 → {csv_path}")

    def run(self):
        try:
            sections = [
                ("가격", "https://www.nongnet.or.kr/qlik/sso/single/?appid=21f27d83-cf68-4f03-afe4-aed6907fbe78&sheet=c262cbfc-2e3c-414b-91a0-a0c9351dfa35&theme=theme_at_24&opt=ctxmenu,currsel&select=$::%ED%92%88%EB%AA%A9%EB%AA%85_%EC%84%A0%ED%83%9D,%EC%96%91%ED%8C%8C&select=$::%EB%8C%80%EC%83%81%EC%9D%BC%EC%9E%90_%EC%84%A0%ED%83%9D,45777,45778,45779,45780,45781,45782,45783,45784,45785,45786,45787,45788,45789,45790",
                 {
                    "양파": "onionPrice", "배추": "cabbagePrice", "고구마": "sweetPotatoPrice",
                    "감자": "potatoPrice", "토마토": "tomatoPrice", "무": "radishPrice"
                }),
                ("반입량", "https://www.nongnet.or.kr/qlik/sso/single/?appid=bf720c79-68d3-45e8-81de-d066e82d4477&sheet=4f558828-3a48-48d7-8813-fd578ec357b4&theme=theme_at_24&opt=ctxmenu,currsel",
                 {
                    "양파": "onionIntake", "배추": "cabbageIntake", "고구마": "sweetPotatoIntake",
                    "감자": "potatoIntake", "토마토": "tomatoIntake", "무": "radishIntake"
                }),
                ("소매", "https://www.nongnet.or.kr/qlik/sso/single/?appid=075d5cd6-c045-45fa-8640-07873c49c4bb&sheet=edf72f21-8148-4fd7-aa8d-e3e61c560a0b&theme=theme_at_24&opt=ctxmenu,currsel&select=$::%ED%92%88%EB%AA%A9%EB%AA%85_%EC%84%A0%ED%83%9D,%EB%B0%B0%EC%B6%94&select=$::%EB%8C%80%EC%83%81%EC%9D%BC%EC%9E%90_%EC%84%A0%ED%83%9D,45779,45780,45781,45782,45783,45784,45785,45786,45787,45788,45789,45790,45791,45792",
                 {
                    "배추": "cabbageRetail", "양파": "onionRetail", "고구마": "sweetPotatoRetail",
                    "감자": "potatoRetail", "토마토": "tomatoRetail", "무": "radishRetail"
                })
            ]

            for label, url, items in sections:
                print(f"{label} 시작")
                service = Service(executable_path="/usr/local/bin/geckodriver")
                driver = webdriver.Firefox(service=service, options=self.options)

                wait = WebDriverWait(driver, 20)
                driver.get(url)
                time.sleep(15)
                wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "qv-ui-blocker")))

                date = datetime.now() - timedelta(days=1)
                y, m, d = f"{date.year}년", f"{date.month:02d}월", f"{date.day:02d}일"
                for i, val in enumerate([y, m, d, y, m, d]):
                    self.select_dropdown(driver, i, val)

                wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "qv-ui-blocker")))
                confirm_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='확인']]")))
                confirm_button.click()
                time.sleep(6)

                for item_name, filename in items.items():
                    try:
                        print(f"{item_name} 처리 중...")
                        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "qv-ui-blocker")))
                        dropdown_trigger = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "select2-selection")))
                        dropdown_trigger.click()
                        option_xpath = f"//li[contains(@class, 'select2-results__option') and text()='{item_name}']"
                        search_option = wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
                        search_option.click()
                        time.sleep(2)
                        try:
                            radio = driver.find_element(By.XPATH, "//input[@type='radio' and @class='stateO' and @dval='3']")
                            radio.click()
                            time.sleep(2)
                        except:
                            print("radio 버튼 없음 또는 클릭 불가 → 스킵")
                        driver.find_element(By.ID, "exportBtn").click()
                        print(f"{item_name} 다운로드 중...")
                        time.sleep(6)
                        latest_file = max(Path(self.DOWNLOAD_DIR).glob("*.xlsx"), key=os.path.getctime)
                        csv_path = os.path.join(self.DOWNLOAD_DIR, f"{filename}.csv")
                        self.convert_xlsx_to_utf8_csv(str(latest_file), csv_path)
                        os.remove(latest_file)
                        print(f"{item_name} 저장 완료 → {filename}.csv")
                    except Exception as e:
                        print(f"{item_name} 실패: {e}")

                driver.quit()
                print(f"{label} 완료")

        except IndexError as ie:
            print("IndexError 발생:", ie)
            traceback.print_exc()
            playsound.playsound("/media/chan/LCW/Automation/Sound/missionfailed.mp3")
            sys.exit(1)

        except WebDriverException as we:
            print("Selenium 관련 예외 발생:", we)
            traceback.print_exc()
            playsound.playsound("/media/chan/LCW/Automation/Sound/missionfailed.mp3")
            sys.exit(1)

        except Exception as e:
            print("기타 예외 발생:", e)
            traceback.print_exc()
            playsound.playsound("/media/chan/LCW/Automation/Sound/missionfailed.mp3")
            sys.exit(1)

        finally:
            try:
                driver.quit()
                print("드라이버 정상 종료됨")
            except:
                print("드라이버 종료 실패")
