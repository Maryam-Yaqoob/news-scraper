FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y python3 python3-pip wget curl unzip gnupg ca-certificates fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 libatk1.0-0 libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 libx11-xcb1 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 xdg-utils --no-install-recommends && rm -rf /var/lib/apt/lists/*
RUN wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && apt-get update && apt-get install -y /tmp/chrome.deb && rm /tmp/chrome.deb && rm -rf /var/lib/apt/lists/*
RUN CHROME_VER=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+') && wget -q -O /tmp/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VER}/linux64/chromedriver-linux64.zip" && unzip /tmp/chromedriver.zip -d /tmp/chromedriver_dir && find /tmp/chromedriver_dir -name "chromedriver" -exec mv {} /usr/bin/chromedriver \; && chmod +x /usr/bin/chromedriver && rm -rf /tmp/chromedriver.zip /tmp/chromedriver_dir
RUN pip3 install --no-cache-dir flask==3.0.3 selenium==4.21.0 requests==2.32.3
WORKDIR /app
COPY app.py .
EXPOSE 7000
CMD ["python3", "app.py"]
