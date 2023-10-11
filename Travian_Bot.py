from selenium.webdriver.common.by import By
import time
import os
from dotenv import load_dotenv
from selenium.common import NoSuchElementException
from random import randint
import threading
from multiprocessing import Process

from selenium import webdriver
from selenium.webdriver.firefox.options import Options


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

    def check_login(self):
        try:
            self.driver.find_element(By.ID, 'outOfGame')
        except NoSuchElementException:
            return self.login_in()

    def check_villages(self):
        if 'listEntry' not in self.driver.page_source:
            self.check_login()
            time.sleep(2)
        for div in self.driver.find_elements(By.CSS_SELECTOR, 'div.listEntry'):
            self.villages[div.find_element(By.CSS_SELECTOR, 'span.name').text] = div.get_attribute('data-did')

    def time_to_complete_building(self):
        try:
            # Отримуємо час до завершення поточного будівництва
            if 'dorf' not in self.driver.current_url:
                self.driver.get(f'{self.domen_URL}/dorf1.php')
                time.sleep(1)
            tag_bild = self.driver.find_element(By.CLASS_NAME, 'buildDuration').find_element(By.TAG_NAME, 'span')
            time.sleep(1)
            time_bild = tag_bild.get_attribute('value')
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
            print(f'{village_id}: Будівлю "{title[:-9]}" побуловано успішно до {int(title[-2:])+1} рівня')

        except:
            if self.check_login():
                print("Вхід виконано під час будування")
                self.start_building(url, village_id)


    def building(self, objects: dict[str: list[[int, int],]]): # {"name_village":[[max_level: int, build_gid: int],  ])
        self.driver.get(f'{self.domen_URL}/dorf1.php')
        # Отримуємо список поселень
        self.check_villages()
        # Перевіряємо чи правильно вказанні назви поселень
        for name in objects.keys():
            if name not in self.villages:
                print(f"{self.villages}\n В списку вище не знайдено {name}.")
        # Список потоків

        # Запускаємо будування в кожному поселенні циклом
        times = {}
        for name_village in objects:
            x = self.one_village(name_village, objects[name_village])
            if x:
                times[name_village] = x
        while True:
            if len(times) == 0:
                break
            min_key = min(times, key=times.get)
            min_time = times.pop(min_key)
            time.sleep(min_time + randint(3, 20))
            for i in times:
                times[i] = times[i] - min_time
            y = self.one_village(min_key, objects[min_key])
            if x:
                times[min_key] = y





    def one_village(self, name_villag: str, list_build: list[int, int, int]):
        # Відсортуємо список list_build, щоб спочатку йшли ресурсні поля а потім з центру
        list_build = sorted(list_build, key=lambda x: x[1])
        village_id = self.villages[name_villag]
        main_page = f'{self.domen_URL}/dorf1.php'
        self.driver.get(f'{main_page}?newdid={village_id}&')
        try:
            builds = []
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
                        # Відкриваємо сторінку ресурсів тільки у випадку якщо поточній сторінці немає 'dorf1'
                        if 'dorf1' not in self.driver.current_url:
                            self.driver.get(main_page)
                            time.sleep(2)
                        builds = self.driver.find_elements(By.CSS_SELECTOR, selector_str)
                        #Відсортуємо список по рівню будівлі
                        build_level = sorted(builds, key=lambda x: x.find_element(By.CLASS_NAME, 'labelLayer').text)
                        # Якщо рівень будівлі нижчий за вказаний користувачем добавляємо в лист будівництва
                        for i in build_level:
                            if i.text != '':
                                if int(i.text) < one_object[0]:
                                    build_url_list.append(i.get_attribute('href'))
                            else:
                                build_url_list.append(i.get_attribute('href'))
                    except:
                        print(village_id + ":Вказане помилкове id")
                else:
                    try:

                        if 'dorf2' not in self.driver.current_url:
                            self.driver.get(f'{self.domen_URL}/dorf2.php')
                            time.sleep(2)
                        build_level = self.driver.find_element(By.CSS_SELECTOR, f'div.g{one_object[1]}')
                        # Якщо рівень будівлі нижчий за вказаний користувачем добавляємо в лист будівництва
                        if int(build_level.text) < one_object[0]:
                            if one_object[1] == 33:
                                build_url_list.append('https://ts30.x3.asia.travian.com/build.php?id=40&gid=33')
                            else:
                                build_url_list.append(build_level.find_element(By.TAG_NAME, 'a').get_attribute('href'))
                    except:
                        print(village_id + ":Вказане помилкове id")

            print(build_url_list)
            # Перевірка чи завершені будівн. усіх будівель
            if len(build_url_list) == 0:
                print(village_id + ": Усе будівництво завершено!")
                return False
            # Будування по списку ссилок build_url_list
            for object_url in build_url_list:
                timer = self.time_to_complete_building()
                if not timer:
                    time.sleep(1)
                    # Починаємо будівництво
                    self.start_building(object_url, village_id)
                    time.sleep(1)
                else:
                    print(f'{village_id}: До завершення будівництва {timer} секунд')
                    return int(timer)
            time.sleep(2)
            # Після проходж. списку будівництві, все ще не виконується будівн. значить невистачає ресурсів
            if not self.time_to_complete_building():
                print(village_id + ': Немає ресурсів на будівництво жодної будівлі зі списку, очікуємо')
                return 900
        except:
            print(village_id + ': Щось пішло не так')
            self.check_login()
            return 15



if __name__ == '__main__':
    asia = TravianBot('https://ts30.x3.asia.travian.com', get_driver('Firefox_Profile2'))
    asia.building({'1': [[10, 20], [15, 33], [20, 15]],
                   '2': [[5, 5], [5, 6]],
                   '3': [[12, 10], [12, 11], [8, 1], [8, 2]],
                   })
    asia.driver.quit()