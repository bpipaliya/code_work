import urllib.parse as urlparse
from time import sleep
import fy_lib
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.chrome.service import Service
from fyers_api import fyersModel, accessToken
app_id = fy_lib.fyers_api2_id_BBP
app_secret = fy_lib.fyers_api2_secret_BBP
user_id = fy_lib.fyers_user_id_BBP
password = fy_lib.fyers_pwd_BBP
two_fa = fy_lib.fyers_two_fa_BBP

redirect_url = fy_lib.fyers_redirect_url
now = pd.Timestamp.now(tz='Asia/Kolkata')
start_time = now.replace(hour=9, minute=0, second=0, microsecond=0)


def get_token():
    session = accessToken.SessionModel(client_id=app_id,
                                       secret_key=app_secret,
                                       redirect_uri=redirect_url,
                                       response_type="code",
                                       grant_type="authorization_code")
    url = session.generate_authcode()
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s)
    # s = Service(executable_path='G:/My Drive/Trading_Stratery/Fyers/chromedriver.exe')
    # driver = webdriver.Chrome(service=s, options=options)

    driver.get(url)
    WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.XPATH, '//div[@class="container login-main-start"]')))
    driver.find_element(By.XPATH, "//input[@id='fyers_id']").send_keys(user_id)
    driver.find_element(
        By.XPATH, "//input[@id='password']").send_keys(password)
    driver.find_element(By.XPATH, "//input[@id='pancard']").send_keys(two_fa)
    driver.find_element(By.XPATH, "//button[@id='btn_id']").click()
    sleep(2)
    current_url = driver.current_url
    driver.close()

    parsed = urlparse.urlparse(current_url)
    auth_code = urlparse.parse_qs(parsed.query)['auth_code'][0]
    session.set_token(auth_code)
    response = session.generate_token()
    return response["access_token"]


if __name__ == '__main__':
    access_token = get_token()
    with open('access_token2_BBP.txt', "w") as at:
        at.write(access_token)
    print(access_token)
    fyers = fyersModel.FyersModel(
        client_id=app_id, token=access_token, log_path="D:\\bhave\\Desktop")
