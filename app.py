from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

app = Flask(__name__)

REGISTRATION = "FA23-BAI-025"
NEWS_SOURCE = "Associated Press"
NEWS_URL = "https://apnews.com"

def get_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def simple_summarize(text, max_sentences=5):
    text = re.sub(r'\s+', ' ', text).strip()
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 40]
    summary = ' '.join(sentences[:max_sentences])
    return summary if summary else text[:800]

def scrape_ap_news(keyword):
    driver = get_chrome_driver()
    article_url = ""
    summary = ""
    try:
        search_url = f"https://apnews.com/search?q={keyword.replace(' ', '+')}"
        driver.get(search_url)
        time.sleep(4)
        article_link = None
        all_links = driver.find_elements(By.TAG_NAME, "a")
        for a in all_links:
            href = a.get_attribute("href") or ""
            if "apnews.com/article/" in href:
                article_link = href
                break
        if not article_link:
            return "", "No article found for the given keyword."
        article_url = article_link
        driver.get(article_url)
        time.sleep(4)
        text_blocks = []
        for selector in ["div.RichTextStoryBody p", ".Article p", "article p", "main p"]:
            paragraphs = driver.find_elements(By.CSS_SELECTOR, selector)
            if paragraphs:
                text_blocks = [p.text.strip() for p in paragraphs if p.text.strip()]
                break
        if not text_blocks:
            all_p = driver.find_elements(By.TAG_NAME, "p")
            text_blocks = [p.text.strip() for p in all_p if len(p.text.strip()) > 50]
        full_text = ' '.join(text_blocks)
        summary = simple_summarize(full_text)
        if not summary:
            summary = "Could not extract article content."
    except Exception as e:
        summary = f"Scraping error: {str(e)}"
    finally:
        driver.quit()
    return article_url, summary

@app.route('/get', methods=['GET'])
def get_news():
    keyword = request.args.get('keyword', '').strip()
    if not keyword:
        return jsonify({"registration": REGISTRATION, "newssource": NEWS_SOURCE, "keyword": keyword, "url": "", "summary": "Please provide a keyword parameter."}), 400
    url, summary = scrape_ap_news(keyword)
    return jsonify({"registration": REGISTRATION, "newssource": NEWS_SOURCE, "keyword": keyword, "url": url, "summary": summary})

@app.route('/', methods=['GET'])
def index():
    return jsonify({"registration": REGISTRATION, "newssource": NEWS_SOURCE, "message": "News Scraper API running. Use /get?keyword=<your_keyword>"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=False)
