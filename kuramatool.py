# coding:utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome import service as fs
from selenium.webdriver.common.by import By
from configparser import ConfigParser
import pprint
import re
import csv

config = config = ConfigParser()
config.read('config.ini')

user_id=config.get("user", 'user_id')
user_pass=config.get("user", 'user_pass')

def get_bill_data(driver,kubun):
  result: list = []
#  item=driver.find_element(By.XPATH,'//*[@id="nplist"]/div[2]/ul/li[1]')
  items=driver.find_elements(By.XPATH,'//*[@id="'+kubun+'"]/div[2]/ul/li')
  i = 0
  for item in items:
    date = item.find_element(By.XPATH,'div/div/div[1]/span').get_attribute('innerHTML')
    data_type = item.find_element(By.XPATH,'div/div/div[3]').get_attribute('innerHTML') 
    id = ""
    stripe_tesuryo=""
    kaikei_kingaku=""
    tesuryo=""
    bikou = ""

    if data_type.startswith('Stripe振込手数料（税込）'):
      bikou = "Stripe振込手数料（税込）"
      stripe_tesuryo = item.find_element(By.XPATH,'div/div/div[4]/h2').get_attribute('innerHTML') 
    elif data_type.startswith('複数カテゴリの追加分（税抜）'):
      id = ""
      bikou = "複数カテゴリの追加分（税抜）"
      tesuryo = ""
      kaikei_kingaku = item.find_element(By.XPATH,'div[2]/div/div/div/div[2]').get_attribute('innerHTML')
    elif data_type.startswith('店舗の当日キャンセル'):
      id = re.search('.*? :(.*?)（税抜）',data_type)[1]
      bikou = "店舗の当日キャンセル"
      tesuryo = item.find_element(By.XPATH,'div/div/div[4]/h2').get_attribute('innerHTML')
      kaikei_kingaku = item.find_element(By.XPATH,'div[2]/div/div/div/div[2]').get_attribute('innerHTML')
    else:
      if data_type.startswith('リピーターからの受注（税抜）'):
        bikou = 'リピーターからの受注（税抜）'
      id = item.find_element(By.XPATH,'div/div/div[2]/a').get_attribute('innerHTML')
      kaikei_kingaku = item.find_element(By.XPATH,'div/div/div/div/div[2]').get_attribute('innerHTML') 
      tesuryo = item.find_element(By.XPATH,'div/div/div[4]/h2').get_attribute('innerHTML') 
    result.append([kubun,date,id,kaikei_kingaku,tesuryo,stripe_tesuryo,bikou])

  return result
  
# できあがってる部分
def get_bill_id(lines):
  lines_array=lines.split("\n")
  result = []
  for line in lines_array:
    #match = re.search('value="\/shop\/bill\/\?(bill_id=.*&amp;month=[0-9]{4}-[0-9]{2})" \>.*',line)
    match = re.search('value="/shop/bill/\?(bill_id=.*?&amp;month=[0-9]{4}-[0-9]{2})',line)
    if match is not None:
      result.append(match[1])
  return result
 
# ここから開始
# ブラウザを開く
chrome_service = fs.Service(executable_path='/usr/local/bin/chromedriver')
driver = webdriver.Chrome(service=chrome_service)
#ログインする
driver.get("https://curama.jp/shop/bill/")
login_form_id = driver.find_element(By.XPATH,'//*[@id="shopUser"]/div[1]/div/div/div[1]/form/div[1]/table/tbody/tr[1]/td/input')
login_form_id.send_keys(user_id)
login_form_password = driver.find_element(By.XPATH,'//*[@id="password-input"]')
login_form_password.send_keys(user_pass)
login_button = driver.find_element(By.XPATH,'//*[@id="shopUser"]/div[1]/div/div/div[1]/form/div[2]/button')
login_button.click()

#請求明細の画面のドロップダウン
bill_dropdown = driver.find_elements(By.XPATH,'//*[@id="npBill"]')
#各月のURLを取得する
url_list = get_bill_id(bill_dropdown[0].get_attribute('innerHTML'))
result: list = [["区分","日付","id","会計金額","手数料","Stripe手数料","備考"]]
for opt in url_list:
  print(opt)
  month = re.search('bill_id=.*?month=([0-9]{4}-[0-9]{2})',opt)
  if month is not None:
    bill_month = month[1]
  else:
    bill_month = "-"

  driver.get("https://curama.jp/shop/bill/?"+opt)
  month_data = get_bill_data(driver,"nplist")
  for line in month_data:
    if line is not None:
      data = list(line)
      data.insert(0,bill_month) 
      result.append(data)
  month_data = get_bill_data(driver,"stripelist")
  for line in month_data:
    if line is not None:
      data = list(line)
      data.insert(0,bill_month) 
      result.append(data)
f = open('output.tsv', 'w')
writer = csv.writer(f, delimiter='\t')
writer.writerows(result)
f.close()




pprint.pprint(result)
driver.close()
