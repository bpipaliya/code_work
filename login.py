
import time
from fy_lib import *
from fyers_api import accessToken
from selenium.webdriver.support.ui import WebDriverWait

app_id = fyers_api2_id_BBP
app_secret = fyers_api2_secret_BBP
user_id = fyers_user_id_BBP
password = fyers_pwd_BBP
two_fa = fyers_two_fa_BBP
redirect_url = fyers_redirect_url
digit = digit


def get_token():
    session = accessToken.SessionModel(
        client_id=app_id,
        secret_key=app_secret,
        redirect_uri=redirect_url,
        response_type="code",
        grant_type="authorization_code",
        state="abcdef",
    )

    app_ID, app_type = app_id.split("-")

    payload = {
        "app_id": app_ID,
        "appType": app_type,
        "code_challenge": "",
        "create_cookie": False,
        "fyers_id": user_id,
        "nonce": "",
        "password": password,
        "redirect_uri": redirect_url,
        "response_type": "code",
        "scope": "",
        "state": "abcdef",
    }

    generate_auth_code_url = session.generate_authcode()

    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.by import By

    s = Service(ChromeDriverManager().install())

    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=s, options=options)

    driver.get(generate_auth_code_url)

    login_id = WebDriverWait(driver, 10).until(
        lambda x: x.find_element(By.XPATH, '//*[@id="fy_client_id"]')
    )

    login_id.send_keys(user_id)
    submit = WebDriverWait(driver, 300).until(
        lambda x: x.find_element(By.XPATH, '//*[@id="clientIdSubmit"]')
    )
    submit.click()
    wait = WebDriverWait(driver, 10)
    from selenium.webdriver.support import expected_conditions as EC
    fy_client_pwd = wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="fy_client_pwd"]')))
    fy_client_pwd.send_keys(password)
    driver.implicitly_wait(20)
    submit = WebDriverWait(driver, 20).until(
        lambda x: x.find_element(By.XPATH, '//*[@id="loginSubmit"]')
    )
    submit.click()
    from selenium.webdriver.common.by import By
    digit_1 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/section[8]/div[3]/div[3]/form/div[2]/input[1]")))
    digit_2 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/section[8]/div[3]/div[3]/form/div[2]/input[2]")))
    digit_3 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/section[8]/div[3]/div[3]/form/div[2]/input[3]")))
    digit_4 = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/section[8]/div[3]/div[3]/form/div[2]/input[4]")))

    digit_1.send_keys(digit[0])
    digit_2.send_keys(digit[1])
    digit_3.send_keys(digit[2])
    digit_4.send_keys(digit[3])

    driver.implicitly_wait(20)
    submit = WebDriverWait(driver, 20).until(
        lambda x: x.find_element(By.XPATH, '//*[@id="verifyPinSubmit"]')
    )

    submit.click()
    time.sleep(2)

    result_url = driver.current_url
    auth_code = result_url.split("auth_code=")[1]
    auth_code = auth_code.split("&")[0]
    session.set_token(auth_code)
    response = session.generate_token()
    return response["access_token"]


if __name__ == '__main__':
    access_token = get_token()
    with open('access_token2_BBP.txt', "w") as at:
        at.write(access_token)
    print(access_token)
