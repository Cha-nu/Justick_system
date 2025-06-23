# Justick_system

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
