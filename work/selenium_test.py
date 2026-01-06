# coding:utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome import service as fs
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

selenium_url = "http://selenium:4444/wd/hub"
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Remote(command_executor=selenium_url, options=chrome_options)

driver.get("https://www.google.com/")
time.sleep(20)
driver.get("https://www.yahoo.co.jp/")
time.sleep(5)

driver.quit()