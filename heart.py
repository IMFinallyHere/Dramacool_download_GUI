import math
import threading
import time

from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup as bs4
import requests as rq
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


# noinspection PyMethodMayBeStatic,PyBroadException
class Heart:
    def __init__(self):
        self.website_url = 'https://dramacool.cr'
        self.browser_exe_path = 'C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe'

    def search(self, name: str):
        user_looking_for = name.replace(' ', '+')
        response = rq.get(f'{self.website_url}/search?type=movies&keyword={user_looking_for}')
        soup = bs4(response.text, 'html.parser')
        names = [i.string for i in soup.select('ul li a h3')]
        img_url = [i.get('data-original') for i in soup.select('ul li a img')[1:]]
        urls = [self.website_url + ((i.get('onclick')).replace('window.location = \'', '')).replace('\'', '') for i in
                soup.select('ul li a h3')]
        result = [{'name': names[i], 'img': img_url[i], 'url': urls[i]} for i in range(len(names))]

        return result

    def home_pg(self):
        chrome_driver_path = '.\\chromedriver.exe'
        options = Options()
        # browser exe file
        options.binary_location = self.browser_exe_path

        options.add_argument('headless')
        driver = webdriver.Chrome(options=options, service=Service(chrome_driver_path))
        driver.get(self.website_url)
        a = driver.find_elements(By.CSS_SELECTOR, '.views1 ul li')
        b = [{'name': i.find_element(By.CSS_SELECTOR, 'a').get_attribute('title'),
              'url': i.find_element(By.CSS_SELECTOR, 'a').get_attribute('href'),
              'img': i.find_element(By.CSS_SELECTOR, 'a div').get_attribute('style')[23:-3]} for i in a]
        return b

    def get_all_ep_pg(self, media_page: str):
        response = rq.get(media_page)
        soup = bs4(response.text, 'html.parser')
        some_useless_data = soup.select('.all-episode li a h3')
        ep_pg = [self.website_url + ((ep.get('onclick')).replace('window.location = \'', '').replace('\'', '')) for ep
                 in some_useless_data]
        ep_pg.reverse()
        return ep_pg

    def get_ep_download_links(self, ep_to_download):
        ep_download = []
        for ep in ep_to_download:
            response = rq.get(ep)
            soup = bs4(response.text, 'html.parser')
            some_useless_data = soup.select('.download a')
            for i in some_useless_data:
                ep_download.append("https://" + str(i).split('\n')[0][11:-18])
        return ep_download

    # noinspection PyShadowingNames,PyBroadException
    def downloading(self, ep):
        chrome_driver_path = '.\\chromedriver.exe'
        options = Options()
        options.binary_location = self.browser_exe_path
        # fdm
        options.add_extension('.\\fdm.crx')
        # buster
        options.add_extension('.\\buster.crx')
        options.add_experimental_option('detach', True)

        driver = webdriver.Chrome(options=options, service=Service(chrome_driver_path))
        driver.minimize_window()
        driver.get(ep)
        if self.check_captcha(driver):
            driver.maximize_window()

            WebDriverWait(driver, 100).until(EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, "iframe[name^='a-'][src^='https://www.google.com/recaptcha/api2/anchor?']")))
            WebDriverWait(driver, 100).until(
                EC.element_to_be_clickable((By.XPATH, "//span[@id='recaptcha-anchor']"))).click()
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//span[@id='recaptcha-anchor' and @aria-checked='true']")))
            except TimeoutException:
                self.solve_captcha(driver)

            driver.switch_to.default_content()
            driver.find_element(By.ID, 'btn-submit').click()
            driver.minimize_window()
            time.sleep(5)

        for i in range(4, 0, -1):
            try:
                btn = driver.find_element(By.XPATH, f'/html/body/section/div/div[2]/div/div[4]/div[1]/div[{i}]')
            except Exception:
                pass
            else:
                btn.click()
                driver.minimize_window()
                break

        time.sleep(1)
        driver.quit()
        return

    # noinspection PyBroadException
    def solve_captcha(self, driver):
        driver.switch_to.default_content()
        WebDriverWait(driver, 50).until(EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, "iframe[name^='c-'][src^='https://www.google.com/recaptcha/api2/bframe?']")))

        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.help-button-holder'))).click()
        time.sleep(3)

        driver.switch_to.default_content()
        try:
            WebDriverWait(driver, 5).until(EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, "iframe[name^='a-'][src^='https://www.google.com/recaptcha/api2/anchor?']")))
            WebDriverWait(driver, 4).until(EC.presence_of_element_located(
                (By.XPATH, "//span[@id='recaptcha-anchor' and @aria-checked='true']")))
            return
        except Exception:
            driver.switch_to.default_content()
            WebDriverWait(driver, 50).until(EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, "iframe[name^='c-'][src^='https://www.google.com/recaptcha/api2/bframe?']")))
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '.image-button-holder'))).click()
            time.sleep(2)
            self.solve_captcha(driver)

    def check_captcha(self, driver):
        """Returns true if captcha found on page"""
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "captcha-v2"))
            )
        except Exception:
            return False
        else:
            return True


def partition(ls: list):
    x = math.ceil(len(ls) / 6) if 6 < len(ls) else 1
    n = 0
    ls_for_challenge = []
    for i in range(x):
        if n + 6 > len(ls):
            ls_for_challenge.append(ls[n:len(ls)])
        else:
            ls_for_challenge.append(ls[n:n + 6])
            n += 6

    return ls_for_challenge


def handle_download(download_links: list, func):
    thread_list, ls = [], []
    for a in partition(download_links):
        for link in a:
            t = threading.Thread(target=func, kwargs={'ep': link})
            t.start()
            time.sleep(1)
            thread_list.append(t)
        # Wait for all threads to complete
        for thread in thread_list:
            thread.join()
    return
