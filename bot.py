import argparse
import json
import os
import sys
import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

class SendMessage:
    def __init__(self, user, text):
        self.user = user
        self.text = text
        self.delay = 2
        
        self.chrome_options = Options()
        self.chrome_options.add_argument('--disable-notifications')
        #chrome_options.add_argument('--headless') 

        #User Data
        self.user_data_dir = os.path.join(os.getcwd(), 'User_Data') 
        self.chrome_options.add_argument('--user-data-dir=' + self.user_data_dir)
        if os.path.isdir(self.user_data_dir):
            print(f"User data {self.user_data_dir}")
        else:
            os.makedirs(self.user_data_dir)  
        prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': os.getcwd()}
        self.chrome_options.add_experimental_option('prefs', prefs)
        #//

        webdriver_path = ChromeDriverManager().install()
        expect_binary_name = 'chromedriver'
        if os.name == 'nt':
            expect_binary_name += '.exe'
        actual_binary_name = os.path.basename(webdriver_path)
        if actual_binary_name != expect_binary_name:
            webdriver_dir_path = os.path.dirname(webdriver_path)
            webdriver_path = os.path.join(webdriver_dir_path, expect_binary_name)

        self.chrome_service = Service(executable_path=webdriver_path)
        self.driver = webdriver.Chrome(service=self.chrome_service, options=self.chrome_options)
        self.driver.maximize_window() 
        self.driver.get('https://web.telegram.org/a/')
        self.action = ActionChains(self.driver)

    def local_storage_save(self):
        local_storage = self.driver.execute_script("return window.localStorage")
        print('Saving to local_storage.json...')
        with open(self.json_path, 'w') as f:
            json.dump(local_storage, f)

    def search_input(self):
        while self.driver.current_url == 'https://web.telegram.org/a/':
            try:
                search = WebDriverWait(self.driver, self.delay * 2).until(EC.presence_of_element_located((By.ID, 'telegram-search-input')))
                #search = self.driver.find_element(By.ID, 'telegram-search-input')
                self.action.click(search).perform()
                search.clear()
                time.sleep(self.delay) 
                search.send_keys(self.user) 
                print(f"Введено значение: {self.user}")
                break
            except Exception as e:
                time.sleep(self.delay)
                print(e)
                print("Повторный поиск search_input")

    def picker(self):
        picker = WebDriverWait(self.driver, self.delay * 2).until(EC.presence_of_element_located((By.CLASS_NAME, 'ChatInfo')))
        time.sleep(self.delay)
        self.action.move_to_element(picker).click().perform()

    def text_area(self):
        text_area = WebDriverWait(self.driver, self.delay * 2).until(EC.presence_of_element_located((By.ID, 'editable-message-text')))
        text_area.click()  
        text_area.clear()
        text_area.send_keys(self.text)

    def send_message(self):
        button = WebDriverWait(self.driver, self.delay * 2).until(EC.presence_of_element_located((By.XPATH, '//button[@title="Send Message"]')))
        self.action.click(button).perform()
    
    def run(self):
        while True:
            try:
                while self.driver.current_url == 'https://web.telegram.org/a/':
                    self.search_input()
                    time.sleep(self.delay)
                    # self.local_storage_save()
                    # time.sleep(self.delay)
                    self.picker()
                    time.sleep(self.delay)
                    self.text_area()
                    time.sleep(self.delay)
                    self.send_message()
                    time.sleep(self.delay)
                    self.driver.quit()
                    sys.exit()
            except Exception as e:
                print(f"Ошибка: {e}. Повторная попытка...")
                time.sleep(self.delay)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Отправка сообщения')
    parser.add_argument('user', type=str, help='@Ник')
    parser.add_argument('text', type=str, help='Текст')
    
    args = parser.parse_args()
    
    bot = SendMessage(args.user, args.text)
    bot.run()