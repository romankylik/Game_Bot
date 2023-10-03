import pickle
import threading
import time
from multiprocessing import Process
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import requests
#from driver_login import *
from selenium import webdriver
from selenium.common import NoSuchElementException
class TR_bot():
    def __init__(self, domen_Url, browser_profile):
        self.domen_URL = domen_Url
        self.profile_dir = browser_profile
        self.options = Options()
        self.driver = self.get_driver()


    def get_driver(self):
        URL = self.domen_URL + '/dorf1.php'

        # Задаємо опцію власного профіля для драйвера
        self.options.add_argument('-profile')
        # Додаткова опція не відкривати графічне вікно браузера(робота у фоновому режимі, за бажанням)
        ##options.add_argument('-headless')
        # Вказуємо шлях до профілю браузера( в цьому випадку він в папці проекту)
        self.options.add_argument(f'.\\{self.profile_dir}')
        # -Відкрийте веб-браузер Firefox.
        # -Введіть ' about:profiles ' у адресному рядку браузера Firefox.
        # -Копієюмо папку профілю браузера Firefox в папку проекту, по бажанню можна перейменувати папку
        # -Наприклад, шлях може виглядати схоже на '...\user\AppData\Roaming\Mozilla\Firefox\Profiles\xxxxxxxx.default-release'
        # -Де 'xxxxxxxx.default-release' яку потрібно скопіювати"""
        return webdriver.Firefox(options=self.options)

    def login_in(self, driver, URL):

        # Відкриваємо веб-сторінку для авторизації
        self.counter = 0
        while self.counter < 4:
            try:
                driver.get(URL)
                # Чекаємо, поки елемент з ім'ям 'name' не буде видимим
                time.sleep(2)
                # Знаходимо поля для введення логіну та паролю
                self.username_field = driver.find_element(By.NAME, 'name')
                self.password_field = driver.find_element(By.NAME, "password")
                break
            except:
                driver.get(self.domen_URL)
                time.sleep(3)
                self.counter += 1

        # Введення логіну та паролю
        self.username_field.send_keys("gada94")
        self.password_field.send_keys("gada11291994")
        time.sleep(2)
        # Відправлення форми авторизації
        self.username_field.submit()
        time.sleep(1)
        return driver




    def check_login(self,URL):
        try:
            self.driver.get(URL)
            self.driver.find_element(By.ID, 'outOfGame')
        except NoSuchElementException:
            return self.login_in(self.driver, URL)



    def building_one_object(self, name_villag: str, max_level: int, build_id: int, build_gid: int):
        self.check_login(self.domen_URL + '/dorf1.php')
        # Список існуючих поселень
        self.villages = self.check_villages(self.driver)
        # Перевірка чи правильно вказана назва поселення користувачем
        while name_villag not in self.villages:
            name_villag = input(f"Поселення {name_villag} не знайдено,введіть заново: ")
        while True:
            try:
                if self.time_to_complete_building(self.driver, self.domen_URL+'/dorf2.php' + '?newdid='+self.villages[name_villag]+'&'):
                    time.sleep(1)
                    build_URL = f'{self.domen_URL}/build.php?id={build_id}&gid={build_gid}'

                    # Починаємо будівництво/ Якщо функція start_building повертає 'max' значить будівля побудована до рівня max_level
                    if self.start_building(self.driver, build_URL, max_level) == 'max':
                        break
                    time.sleep(1)
            except:
                time.sleep(50)
                self.check_login(self.domen_URL+"/dorf2.php")

        print(f'Будування до рівня {max_level} успішно завершено!')



    def check_villages(self, driver):
        self.villages = {}
        for div in driver.find_elements(By.CSS_SELECTOR, 'div.listEntry'):
            self.villages[div.find_element(By.CSS_SELECTOR, 'span.name').text] = div.get_attribute('data-did')
        return self.villages




    def time_to_complete_building(self, driver, URL):
        try:
            # Отримуємо час до завершення поточного будівництва
            driver.get(URL)
            time.sleep(1)
            tag_bild = driver.find_element(By.CLASS_NAME, 'buildDuration').find_element(By.TAG_NAME, 'span')
            time.sleep(1)
            time_bild = tag_bild.get_attribute('value')
            print('До завершення поточного будівництва ' + time_bild + " секунд")
            time.sleep(int(time_bild) + 10)
        except:
            return True



    def start_building(self, driver , URL, lvl=100):
        try:
            # Відкриваємо сторінку конкретної будівлі
            driver.get(URL)
            time.sleep(1)

            # Перевірка чи сторінка будівництва має різні вкладки
            if 'scrollingContainer' in driver.page_source:
                driver.find_element(By.CSS_SELECTOR, 'div.favorKey0').click()
                time.sleep(1)
            # Знаходимо кнопку "Побудувати" та клікаємо
            clic_1 = driver.find_element(By.CLASS_NAME, 'section1')
            clic_bild = clic_1.find_element(By.CSS_SELECTOR, '.textButtonV1.green.build')
            time.sleep(2)
            # Перевірка чи будівля не побудована до вказаного рівня
            if int(clic_bild.text[-1]) > lvl:
                print("Будівля побудована до вказаного вами рівня")
                return 'max'
            title = driver.find_element(By.CSS_SELECTOR, '.titleInHeader').text
            clic_bild.click()
            print(f'Будівлю "{title}" побуловано успішно')
        except:
            if self.check_login(URL):
                return print("Вхід виконано під час будування")
            else:
                print('Не вистачає ресурсів на будівництво, очікуємо')
                time.sleep(900)

# Вдосконалення "Баллиста" в академії (Важливо яка мова інтерфейсу гри)


def first():
    x = TR_bot('https://ts30.x3.asia.travian.com', 'Firefox_Profile2')
    x.options.add_argument("--headless")
    x.building_one_object('1', 16, 20, 10)  # Склад
    x.building_one_object('1', 12, 23, 17)
    x.driver.quit()

def second():
    y = TR_bot('https://ts30.x3.asia.travian.com', 'Firefox_Profile1')
    y.options.add_argument("--headless")
    y.building_one_object('2', 10, 21, 11)
    y.building_one_object('2', 10, 20, 10)
    y.building_one_object('2', 10, 26, 15)
    y.building_one_object('2', 10, 38, 17)

    y.driver.quit()


if __name__ == '__main__':
    ...



    #building_all_object('1', 5, "Дерево") #Якщо некорекний або взагалі немає типу ресурсного поля то будує всі поля
    #building_all_object('1', 5, "Глина")
    #building_all_object('Third villl', 10, "Зерно")

    ##building_one_object('1', 7, 1, 1)
    #building_one_object('1', 3, 22, 11)

    process1 = Process(target=first)
    process2 = Process(target=second)

    process1.start()
    process2.start()

    process1.join()
    process2.join()






