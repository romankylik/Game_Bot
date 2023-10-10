import threading
from multiprocessing import Process

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
        load_dotenv(dotenv_path='personal_data.env')
        counter = 0
        while counter < 4:
            try:
                # Знаходимо поля для введення логіну та паролю
                username_field = self.driver.find_element(By.NAME, 'name')
                password_field = self.driver.find_element(By.NAME, "password")
                # Введення логіну та паролю з файлу *.env в форму
                username_field.send_keys(os.getenv("USERNAME_TR"))
                password_field.send_keys(os.getenv("PASSWORD_TR"))
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
        if 'listEntry' not in self.driver.page_source:
            self.check_login(self.domen_URL + '/dorf1.php')
            time.sleep(2)

        for div in self.driver.find_elements(By.CSS_SELECTOR, 'div.listEntry'):
            self.villages[div.find_element(By.CSS_SELECTOR, 'span.name').text] = div.get_attribute('data-did')

    def time_to_complete_building(self, village_id):
        time_bild =''
        try:
            # Отримуємо час до завершення поточного будівництва
            if 'buildDuration' not in self.driver.page_source:
                self.driver.get(f'{self.domen_URL}/dorf1.php?newdid={village_id}&')
                time.sleep(1)
            tag_bild = self.driver.find_element(By.CLASS_NAME, 'buildDuration').find_element(By.TAG_NAME, 'span')
            time.sleep(1)
            time_bild = tag_bild.get_attribute('value')
            print(f'{village_id}: До завершення будівництва {time_bild} секунд')
            return time_bild
        except NoSuchElementException:
            return False

    def start_building(self, url, village_id):
        try:
            # Відкриваємо сторінку конкретної будівлі
            self.driver.get(url)
            time.sleep(1)
            # Перевірка чи сторінка будівництва має різні вкладки
            if 'scrollingContainer' in self.driver.page_source:
                self.driver.find_element(By.CSS_SELECTOR, 'div.favorKey0').click()
                time.sleep(1)
            # Знаходимо кнопку "Побудувати" та клікаємо
            clic_1 = self.driver.find_element(By.CLASS_NAME, 'section1')
            clic_bild = clic_1.find_element(By.CSS_SELECTOR, '.textButtonV1.green.build')
            time.sleep(2)
            title = self.driver.find_element(By.CSS_SELECTOR, '.titleInHeader').text
            clic_bild.click()
            print(f'{village_id}: Будівлю "{title[:-9]}" побуловано успішно')

        except:
            if self.check_login(url):
                print("Вхід виконано під час будування")


    def building(self, objects: dict[str: list[[int, int],]]): # {"name_village":[[max_level: int, build_gid: int],  ])
        # Отримуємо список поселень
        self.check_villages()
        # Перевіряємо чи правильно вказанні назви поселень
        for name in objects.keys():
            if name not in self.villages:
                print(f"{self.villages}\n В списку вище не знайдено {name}.")
        # Список потоків
        threads = []
        # Запускаємо будування в кожному поселенні окремим потоком

        for name_village in objects:
            arg_potok = (self.driver, name_village, objects[name_village])
            thread = threading.Thread(target=self.building_in_one_villages, args=arg_potok)
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()





    def building_in_one_villages(self, driver, name_villag: str, list_build: list[int, int, int]):
        village_id = self.villages[name_villag]
        while True:
            try:
                build_url_list = []
                for one_object in list_build:
                    if one_object[1] < 5:
                        resource = True
                    else:
                        resource = False
                    # Шукаємо або ресурсне поле або в центрі будівлю
                    if resource:
                        try:
                            # Якщо вказаний третій аргумент- Id то будуємо тільки одне ресурсне поле а не всі
                            if len(one_object) == 3:
                                selector_str = f'a.buildingSlot{one_object[2]}'
                            else:
                                selector_str = f'a.gid{one_object[1]}'
                            with threading.Lock():
                                driver.get(f'{self.domen_URL}/dorf1.php?newdid={village_id}&')
                                time.sleep(2)
                                build_level = driver.find_elements(By.CSS_SELECTOR, selector_str)
                            # Якщо рівень будівлі нижчий за вказаний користувачем добавляємо в лист будівництва
                            for i in build_level:
                                if i.text != '':
                                    if int(i.text) < one_object[0]:
                                        build_url_list.append(i.get_attribute('href'))
                                else:
                                    build_url_list.append(i.get_attribute('href'))
                        except:
                            print(village_id+":Вказане помилкове id")
                    else:
                        with threading.Lock():
                            driver.get(f'{self.domen_URL}/dorf2.php?newdid={village_id}&')
                            time.sleep(2)
                            build_level = driver.find_element(By.CSS_SELECTOR, f'div.g{one_object[1]}')
                        # Якщо рівень будівлі нижчий за вказаний користувачем добавляємо в лист будівництва
                        if int(build_level.text) < one_object[0]:
                            build_url_list.append(build_level.find_element(By.TAG_NAME, 'a').get_attribute('href'))

                # Перевірка чи завершені будівн. усіх будівель
                if len(build_url_list) == 0:
                    print(village_id+": Усе будівництво завершено!")
                    break


                for object_url in build_url_list:
                    #timer = 0
                    with threading.Lock():
                        timer = self.time_to_complete_building(village_id)
                        if not timer:
                            time.sleep(1)
                            # Починаємо будівництво
                            self.start_building(object_url, village_id)
                            time.sleep(1)
                    if timer:
                        time.sleep(int(timer) + randint(3, 20))
                time.sleep(2)
                # Після проходж. списку будівництві, все ще не виконується будівн. значить невистачає ресурсів
                if not self.time_to_complete_building(village_id):
                    print(village_id+': Немає ресурсів на будівництво жодної будівлі зі списку, очікуємо')
                    time.sleep(900)
            except:
                print(village_id+': Щось пішло не так')
                time.sleep(15)
                self.check_login(self.domen_URL + "/dorf1.php")




if __name__ == '__main__':
    asia = TravianBot('https://ts30.x3.asia.travian.com', get_driver('Firefox_Profile2'))
    asia.building({'3':
        [
        [10, 1],
        [10, 10],
        [10, 15]], '1':
        [
        [5, 16]
              ]},
    )


