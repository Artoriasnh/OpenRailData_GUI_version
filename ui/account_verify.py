from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

def verify_credentials_selenium(email, password):
    options = Options()
    # 开启浏览器窗口调试，建议调试阶段不要用 headless
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=options)

    try:
        driver.get("https://datafeeds.networkrail.co.uk/ntrod/welcome")

        wait = WebDriverWait(driver, 15)

        # 使用 placeholder 定位输入框
        email_input = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//input[@placeholder="Enter your email address"]')))
        password_input = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//input[@placeholder="Enter your password"]')))
        sign_in_button = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//button[.//text()[contains(., "Sign in")]]')))

        email_input.send_keys(email)
        password_input.send_keys(password)
        sign_in_button.click()

        time.sleep(3)  # 等待跳转或验证

        # 登录成功后通常跳转到 dashboard 或 welcome 页面
        current_url = driver.current_url.lower()
        if "profile" in current_url:
            return True
        else:
            return False

    except Exception as e:
        print("验证过程中出错：", e)
        return False

    finally:
        driver.quit()
