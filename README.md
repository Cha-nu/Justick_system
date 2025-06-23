# Justick_system

# 농산물 가격 예측 플랫폼 딱대

**작물별 시계열 특성과 단기 추세, 계절성까지 반영하는 지능형 농산물 예측 시스템입니다.**

- **웹페이지 주소**: [http://justick.iptime.org/](http://justick.iptime.org/)

---

## 🔍 시스템 개요

이 플랫폼은 농산물 가격과 물량의 **시간적 변동**을 효과적으로 분석하고 예측하기 위해 설계되었습니다.  
**단기 추세, 계절성, 급격한 변화량**을 반영하여, 더 신뢰도 높은 가격 예측을 제공합니다.

---

## 🧠 사용된 모델

### 1. LSTM (Long Short-Term Memory)

- 시계열 데이터를 처리하기 위한 **순환 신경망(RNN)**의 확장 모델입니다.
- 가격, 물량, 전일 대비 격차 등의 **시간 순서적 변화**를 모델링하는 데 특화되어 있습니다.

### 2. EWC (Elastic Weight Consolidation)

- 기존 학습된 정보를 보존하면서 새로운 데이터를 학습하는 데 효과적인 기법입니다.
- **점진적 학습(continual learning)** 환경에서 발생하는 catastrophic forgetting 문제를 완화합니다.
- 새로운 날짜의 데이터가 추가될 때, 기존 모델의 중요한 파라미터를 보존하며 업데이트합니다.

> 참고:  
> Kirkpatrick et al., "Overcoming catastrophic forgetting in neural networks", PNAS 2017  
> arXiv: [1612.00796](https://arxiv.org/abs/1612.00796)

---

## 🧾 사용된 데이터와 주요 Feature 

작물: 양파, 배추, 감자, 고구마, 무, 토마토 (특, 상 등급)
  
date           # 날짜
avg_price      # 당일 가격 평균
prev_price     # 이전 날짜 가격
price_diff     # 전일 대비 가격 차이
rolling_mean   # 3일 이동 평균
rolling_std    # 3일 이동 표준편차
log_price      # 로그 변환된 평균 가격

## 사용법

### apt의 firefox가 설치되어 있어야합니다.
sudo add-apt-repository ppa:mozillateam/ppa  
sudo apt update  
sudo apt install firefox  

### geck driver를 설치합니다.
GECKO_VERSION=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep tag_name | cut -d '"' -f 4)  
wget "https://github.com/mozilla/geckodriver/releases/download/$GECKO_VERSION/geckodriver-$GECKO_VERSION-linux-aarch64.tar.gz"  
tar -xzf geckodriver-*.tar.gz  
sudo mv geckodriver /usr/local/bin/  

### selenium을 설치합니다.
pip3 install selenium==4.5.0

### 다른 의존성 패키지
pip3 install numpy pandas torch playsound
