from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time
import os
import shutil
import pandas as pd
from pathlib import Path

try:
	# 현재 경로 기준 다운로드 디렉토리
	BASE_DIR = os.path.dirname(os.path.abspath(__file__))
	DOWNLOAD_DIR = BASE_DIR

	# Firefox 옵션 설정
	options = Options()
	options.headless = True  # 개발 중엔 끄고 테스트

	options.set_preference("browser.download.folderList", 2)
	options.set_preference("browser.download.dir", DOWNLOAD_DIR)
	options.set_preference("browser.download.useDownloadDir", True)
	options.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv,application/vnd.ms-excel")
	options.set_preference("browser.download.manager.showWhenStarting", False)
	options.set_preference("pdfjs.disabled", True)

	print("Price start")
	driver = webdriver.Firefox(options=options)
	wait = WebDriverWait(driver, 20)

	# 접속
	url = "https://www.nongnet.or.kr/qlik/sso/single/?appid=21f27d83-cf68-4f03-afe4-aed6907fbe78&sheet=c262cbfc-2e3c-414b-91a0-a0c9351dfa35&theme=theme_at_24&opt=ctxmenu,currsel&select=$::%ED%92%88%EB%AA%A9%EB%AA%85_%EC%84%A0%ED%83%9D,%EC%96%91%ED%8C%8C&select=$::%EB%8C%80%EC%83%81%EC%9D%BC%EC%9E%90_%EC%84%A0%ED%83%9D,45777,45778,45779,45780,45781,45782,45783,45784,45785,45786,45787,45788,45789,45790"
	driver.get(url)
	print("connect")
	time.sleep(15)

	# 시작일: 어제
	date = datetime.now() - timedelta(days=1)
	year = f"{date.year}년"
	month = f"{date.month:02d}월"
	day = f"{date.day:02d}일"


	def select_dropdown(index, value):
	    dropdowns = driver.find_elements(By.CLASS_NAME, "qui-select")
	    select = Select(dropdowns[index])
	    select.select_by_visible_text(value)

	# 인코딩 보정 + 변환
	def convert_xlsx_to_utf8_csv(xlsx_path, csv_path):
	    df = pd.read_excel(xlsx_path, engine='openpyxl')
	    df.columns = [str(col) for col in df.columns]
	    for col in df.columns:
	    	if df[col].dtype == object:
	    		df[col] = df[col].apply(lambda x: try_decode(x))
	    df.to_csv(csv_path, index=False, encoding='utf-8')
	    print(f"변환 완료 → {csv_path}")

	def try_decode(val):
	    if isinstance(val, str):
	    	try:
	    		return val.encode("latin1").decode("euc-kr")
	    	except:
	    		return val
	    return val

	wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "qv-ui-blocker")))

	# 시작일 선택
	select_dropdown(0, year)
	select_dropdown(1, month)
	select_dropdown(2, day)

	# 종료일 선택
	select_dropdown(3, year)
	select_dropdown(4, month)
	select_dropdown(5, day)

	wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "qv-ui-blocker")))
	# 버튼 클릭
	confirm_button = wait.until(EC.element_to_be_clickable((
	    By.XPATH, "//button[.//span[text()='확인']]"
	)))
	confirm_button.click()
	time.sleep(6)

	# 품목 리스트
	items = {
	    "양파": "onionPrice",
	    "배추": "cabbagePrice",
	    "고구마": "sweetPotatoPrice",
	    "감자": "potatoPrice",
	    "토마토": "tomatoPrice",
	    "무": "radishPrice"
	}

	# 품목별 다운로드
	for item_name, filename in items.items():
	    try:
	    	print(f"{item_name} 처리 중...")
	    	
	    	# ▶ Select2 드롭다운 열기
	    	dropdown_trigger = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "select2-selection")))
	    	dropdown_trigger.click()
	    	
	    	# ▶ 드롭다운 항목 중 해당 품목 클릭
	    	option_xpath = f"//li[contains(@class, 'select2-results__option') and text()='{item_name}']"
	    	search_option = wait.until(EC.presence_of_element_located((By.XPATH, option_xpath)))
	    	search_option.click()
	    	time.sleep(3)
	    	
	    	# ▶ radio 버튼 체크
	    	try:
	    		radio = driver.find_element(By.XPATH, "//input[@type='radio' and @class='stateO' and @dval='3']")
	    		radio.click()
	    		time.sleep(3)
	    	except:
	    		print("radio 버튼 없음 또는 클릭 불가 → 스킵")
	    	
	    	# ▶ 데이터 다운로드 버튼 클릭
	    	driver.find_element(By.ID, "exportBtn").click()
	    	print(f"{item_name} 다운로드 중...")
	    	time.sleep(6)  # 다운로드 여유시간
	    	
	    	# 최신 파일 찾기
	    	latest_file = max(Path(DOWNLOAD_DIR).glob("*.xlsx"), key=os.path.getctime)
	    	csv_target = os.path.join(DOWNLOAD_DIR, f"{filename}.csv")
	    	
	    	convert_xlsx_to_utf8_csv(str(latest_file), csv_target)
	    	os.remove(latest_file)
	    	print(f"{item_name} 저장 완료 → {filename}.csv")
	    
	    except Exception as e:
	    	print(f"{item_name} 실패: {e}")

	driver.quit()
	print("가격 완료")

	# 경로 설정
	BASE_DIR = os.path.dirname(os.path.abspath(__file__))
	DOWNLOAD_DIR = BASE_DIR

	# Firefox 옵션
	options = Options()
	options.headless = True  # 필요 시 활성화

	options.set_preference("browser.download.folderList", 2)
	options.set_preference("browser.download.dir", DOWNLOAD_DIR)
	options.set_preference("browser.download.useDownloadDir", True)
	options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,text/csv")
	options.set_preference("browser.download.manager.showWhenStarting", False)
	options.set_preference("pdfjs.disabled", True)

	print("Intake start")
	driver = webdriver.Firefox(options=options)
	wait = WebDriverWait(driver, 20)

	# ▶ 반입량 대시보드 URL
	url = "https://www.nongnet.or.kr/qlik/sso/single/?appid=bf720c79-68d3-45e8-81de-d066e82d4477&sheet=4f558828-3a48-48d7-8813-fd578ec357b4&theme=theme_at_24&opt=ctxmenu,currsel"
	driver.get(url)
	print("connect")
	time.sleep(15)

	wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "qv-ui-blocker")))

	# 시작일 선택
	select_dropdown(0, year)
	select_dropdown(1, month)
	select_dropdown(2, day)

	# 종료일 선택
	select_dropdown(3, year)
	select_dropdown(4, month)
	select_dropdown(5, day)

	wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "qv-ui-blocker")))
	# 버튼 클릭
	confirm_button = wait.until(EC.element_to_be_clickable((
	    By.XPATH, "//button[.//span[text()='확인']]"
	)))
	confirm_button.click()
	time.sleep(6)


	# ▶ 반입량 파일명 설정
	items = {
	    "양파": "onionIntake",
	    "배추": "cabbageIntake",
	    "고구마": "sweetPotatoIntake",
	    "감자": "potatoIntake",
	    "토마토": "tomatoIntake",
	    "무": "radishIntake"
	}

	for item_name, filename in items.items():
		try:
			print(f"{item_name} 처리 중...")
		
			# ▶ blocker가 사라질 때까지 대기
			wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "qv-ui-blocker")))
			# ▶ Select2 드롭다운 열기
			dropdown_trigger = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "select2-selection")))
			dropdown_trigger.click()
		
			# ▶ 항목 리스트 뜰 때까지 대기
			option_xpath = f"//li[contains(@class, 'select2-results__option') and text()='{item_name}']"
			search_option = wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
			search_option.click()
			time.sleep(3)
		
			# radio 버튼 선택
			try:
				radio = driver.find_element(By.XPATH, "//input[@type='radio' and @class='stateO' and @dval='3']")
				radio.click()
				time.sleep(3)
			except:
				print("radio 버튼 없음 또는 클릭 불가 → 스킵")

			# 다운로드 버튼 클릭
			driver.find_element(By.ID, "exportBtn").click()
			print(f"{item_name} 다운로드 중...")
			time.sleep(6)

			# 최신 파일 찾기
			latest_file = max(Path(DOWNLOAD_DIR).glob("*.xlsx"), key=os.path.getctime)
			csv_target = os.path.join(DOWNLOAD_DIR, f"{filename}.csv")

			convert_xlsx_to_utf8_csv(str(latest_file), csv_target)
			os.remove(latest_file)
			print(f"{item_name} 저장 완료 → {filename}.csv")
		except Exception as e:
			print(f"{item_name} 실패: {e}")

	driver.quit()
	print("반입량 완료")
	
	BASE_DIR = os.path.dirname(os.path.abspath(__file__))
	DOWNLOAD_DIR = BASE_DIR
	
	# Firefox 옵션
	options = Options()
	# options.headless = True  # 필요 시 사용
	options.set_preference("browser.download.folderList", 2)
	options.set_preference("browser.download.dir", DOWNLOAD_DIR)
	options.set_preference("browser.download.useDownloadDir", True)
	options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,text/csv")
	options.set_preference("browser.download.manager.showWhenStarting", False)
	options.set_preference("pdfjs.disabled", True)
	
	print("Retail start")
	driver = webdriver.Firefox(options=options)
	wait = WebDriverWait(driver, 20)
	
	# ▶ 소매 데이터 URL
	url = "https://www.nongnet.or.kr/qlik/sso/single/?appid=075d5cd6-c045-45fa-8640-07873c49c4bb&sheet=edf72f21-8148-4fd7-aa8d-e3e61c560a0b&theme=theme_at_24&opt=ctxmenu,currsel&select=$::%ED%92%88%EB%AA%A9%EB%AA%85_%EC%84%A0%ED%83%9D,%EB%B0%B0%EC%B6%94&select=$::%EB%8C%80%EC%83%81%EC%9D%BC%EC%9E%90_%EC%84%A0%ED%83%9D,45779,45780,45781,45782,45783,45784,45785,45786,45787,45788,45789,45790,45791,45792"
	driver.get(url)
	print("connect")
	time.sleep(15)
	
	wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "qv-ui-blocker")))
	
	# 시작일 선택
	select_dropdown(0, year)
	select_dropdown(1, month)
	select_dropdown(2, day)

	# 종료일 선택
	select_dropdown(3, year)
	select_dropdown(4, month)
	select_dropdown(5, day)
	
	wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "qv-ui-blocker")))
	# 버튼 클릭
	confirm_button = wait.until(EC.element_to_be_clickable((
	    By.XPATH, "//button[.//span[text()='확인']]"
	)))
	confirm_button.click()
	time.sleep(6)
	
	# 품목 리스트
	items = {
    		"배추": "cabbageRetail",
    		"양파": "onionRetail",
    		"고구마": "sweetPotatoRetail",
    		"감자": "potatoRetail",
    		"토마토": "tomatoRetail",
    		"무": "radishRetail"
    		}
	for item_name, filename in items.items():
    		try:
    			print(f"{item_name} 처리 중...")
    			
    			# ▶ blocker가 사라질 때까지 대기
    			wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "qv-ui-blocker")))
    			
    			# ▶ Select2 드롭다운 열기
    			dropdown_trigger = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "select2-selection")))
    			dropdown_trigger.click()
    			
    			# ▶ 항목 리스트 뜰 때까지 대기
    			option_xpath = f"//li[contains(@class, 'select2-results__option') and text()='{item_name}']"
    			search_option = wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
    			search_option.click()
    			time.sleep(3)
    			
    			# radio 버튼 선택
    			try:
    				radio = driver.find_element(By.XPATH, "//input[@type='radio' and @class='stateO' and @dval='3']")
    				radio.click()
    				time.sleep(3)
    			except:
    				print("radio 버튼 없음 또는 클릭 불가 → 스킵")
    				
    			# 다운로드 버튼 클릭
    			driver.find_element(By.ID, "exportBtn").click()
    			print(f"{item_name} 다운로드 중...")
    			time.sleep(6)
    			
    			# 최신 파일 찾기
    			latest_file = max(Path(DOWNLOAD_DIR).glob("*.xlsx"), key=os.path.getctime)
    			csv_target = os.path.join(DOWNLOAD_DIR, f"{filename}.csv")
    			
    			convert_xlsx_to_utf8_csv(str(latest_file), csv_target)
    			os.remove(latest_file)
    			print(f"{item_name} 저장 완료 → {filename}.csv")
    		except Exception as e:
    			print(f"{item_name} 실패: {e}")
    	
	driver.quit()
	print("소매 완료")
	
except IndexError as ie:
    print("IndexError 발생:", ie)
    traceback.print_exc()
    sys.exit(1)

except WebDriverException as we:
    print("Selenium 관련 예외 발생:", we)
    traceback.print_exc()
    sys.exit(1)

except Exception as e:
    print("기타 예외 발생:", e)
    traceback.print_exc()
    sys.exit(1)

finally:
    try:
        driver.quit()
        print("드라이버 정상 종료됨")
    except:
        print("드라이버 종료 실패")
