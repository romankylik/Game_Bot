from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time
import os
from dotenv import load_dotenv
from selenium.common import NoSuchElementException
from random import randint


def get_driver(browser_profile):
    options = Options()
    # Задаємо опцію власного профіля для драйвера
    options.add_argument('-profile')
    # Додаткова опція не відкривати графічне вікно браузера(робота у фоновому режимі, за бажанням)
    ##options.add_argument('-headless')
    # Вказуємо шлях до профілю браузера( в цьому випадку він в папці проекту)
    options.add_argument(f'.\\{browser_profile}')
    # -Відкрийте веб-браузер Firefox.
    # -Введіть ' about:profiles ' у адресному рядку браузера Firefox.
    # -Копієюмо папку профілю браузера Firefox в папку проекту, по бажанню можна перейменувати папку
    # -Наприклад, шлях може виглядати схоже на '...\user\AppData\Roaming\Mozilla\Firefox\Profiles\xxxxxxxx.default-release'
    # -Де 'xxxxxxxx.default-release' яку потрібно скопіювати"""
    return webdriver.Firefox(options=options)

class TravianBot:
    def __init__(self, domen_url, driver):
        self.domen_URL = domen_url
        self.driver = driver
        self.villages = {}


    def login_in(self):
        # Завантажуємо логін та пароль з файлу *.env( файл добавлений в .gitignore)
        load_dotenv()
        counter = 0
        while counter < 4:
            try:
                # Знаходимо поля для введення логіну та паролю
                username_field = self.driver.find_element(By.NAME, 'name')
                password_field = self.driver.find_element(By.NAME, "password")
                # Введення логіну та паролю з файлу *.env в форму
                username_field.send_keys(os.getenv("USERNAME"))
                password_field.send_keys(os.getenv("PASSWORD"))
                time.sleep(2)
                # Відправлення форми авторизації
                username_field.submit()
                break
            except NoSuchElementException:
                self.driver.get(self.domen_URL)
                time.sleep(3)
                counter += 1

    def check_login(self, url):
        try:
            self.driver.get(url)
            self.driver.find_element(By.ID, 'outOfGame')
        except NoSuchElementException:
            return self.login_in()

    def check_villages(self):
        for div in self.driver.find_elements(By.CSS_SELECTOR, 'div.listEntry'):
            self.villages[div.find_element(By.CSS_SELECTOR, 'span.name').text] = div.get_attribute('data-did')

    def time_to_complete_building(self):
        try:
            # Отримуємо час до завершення поточного будівництва
            if 'buildDuration' not in self.driver.page_source:
                self.driver.get(self.domen_URL + '/dorf1.php')
                time.sleep(1)
            tag_bild = self.driver.find_element(By.CLASS_NAME, 'buildDuration').find_element(By.TAG_NAME, 'span')
            time.sleep(1)
            time_bild = tag_bild.get_attribute('value')
            print('До завершення поточного будівництва ' + time_bild + " секунд")
            time.sleep(int(time_bild) + randint(3, 20))
        except NoSuchElementException:
            return True

    def start_building(self, url, lvl=100):
        try:
            # Відкриваємо сторінку конкретної будівлі
            self.driver.get(url)
            time.sleep(1)
            # Перевірка чи сторінка будівництва має різні вкладки
            if 'scrollingContainer' in self.driver.page_source:
                # Клікаємо на саму першу вкладку
                self.driver.find_element(By.CSS_SELECTOR, 'div.favorKey0').click()
                time.sleep(1)
            # Знаходимо кнопку "Побудувати" та клікаємо
            clic_1 = self.driver.find_element(By.CLASS_NAME, 'section1')
            clic_bild = clic_1.find_element(By.CSS_SELECTOR, '.textButtonV1.green.build')
            time.sleep(2)
            # Перевірка чи будівля не побудована до вказаного рівня
            if int(clic_bild.text[-1]) > lvl:
                print("Будівля побудована до вказаного вами рівня")
                return 'max'
            title = self.driver.find_element(By.CSS_SELECTOR, '.titleInHeader').text
            clic_bild.click()
            print(f'Будівлю "{title}" побуловано успішно')
        except NoSuchElementException:
            if self.check_login(url):
                return print("Вхід виконано під час будування")
            else:
                print('Не вистачає ресурсів на будівництво, очікуємо')
                time.sleep(900)


    def building(self, name_villagе: str, object: list[[int, int],]): # [max_level: int, build_gid: int)
        for
        if object[1] < 19:
            self.check_login(self.domen_URL + '/dorf1.php')
            time.sleep(1)
        else:
            self.check_login(self.domen_URL + '/dorf2.php')
            time.sleep(1)
        # Отримуємо список поселень
        self.check_villages()
        # Перевірка чи правильно вказана назва поселення користувачем
        while name_village not in self.villages:
            name_village = input(f"{self.villages}\n В списку вище не знайдено {name_village}. Повторіть введення: ")

        while True:
            try:
                if self.time_to_complete_building():
                    time.sleep(1)
                    build_URL = f'{domen_URL}/build.php?id={build_id}&gid={build_gid}'

                    # Починаємо будівництво/ Якщо функція start_building повертає 'max' значить будівля побудована до рівня max_level
                    if start_building(driver, build_URL, max_level) == 'max':
                        break
                    time.sleep(1)
            except:
                time.sleep(50)
                check_login(domen_URL + "/dorf2.php")



