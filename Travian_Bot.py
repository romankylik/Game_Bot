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
            return title

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
        self.check_login()
        timer = self.time_to_complete_building()

        if not timer:
            builds = {}
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
                        all_builds = self.driver.find_elements(By.CSS_SELECTOR, selector_str)
                        # Якщо рівень будівлі нижчий за вказаний користувачем добавляємо в лист будівництва
                        for i in all_builds:
                            if i.text != '':
                                if int(i.text) < one_object[0]:
                                    builds[i.get_attribute('href')] = [one_object[0], i.text, i.get_attribute("class")]
                            else:
                                builds[i.get_attribute('href')] = [one_object[0], i.text, i.get_attribute("class")]
                    except:
                        print(village_id + ":Вказане помилкове id")
                else:

                    if 'dorf2' not in self.driver.current_url:
                        self.driver.get(f'{self.domen_URL}/dorf2.php')
                        time.sleep(2)
                    # Якщо задана будівля "Стіна" тоді обновляємо її атрибути href
                    if one_object[1] == 33:
                        el = self.driver.find_element(By.CSS_SELECTOR, 'div.g33').find_element(By.TAG_NAME, 'a')
                        url_el = 'https://ts30.x3.asia.travian.com/build.php?id=40&gid=33'
                        self.driver.execute_script('arguments[0].setAttribute("href", arguments[1])', el, url_el)

                    all_builds = self.driver.find_element(By.CSS_SELECTOR, f'div.g{one_object[1]}')
                    # Якщо рівень будівлі нижчий за вказаний користувачем добавляємо в лист будівництва
                    if int() < one_object[0]:
                        el_b = all_builds.find_element(By.TAG_NAME, 'a')
                        builds[el_b.get_attribute('href')] = [one_object[0], el_b.text, el_b.get_attribute("class")]


            # Перевірка чи завершені будівн. усіх будівель
            if len(builds) == 0:
                print(village_id + ": Усе будівництво завершено!")
                return False

            # Відсортуємо словник по рівню будівлі та зберігаємо списком
            list_el = [k for k, v in sorted(builds.items(), key=lambda item: item[1][1])]




            # Будування по списку ссилок builds
            for object_tag in list_el:
                if "good" in builds[object_tag][2]:
                    # Починаємо будівництво
                    title = self.start_building(object_tag, village_id)
                    if title:
                        time.sleep(3)
                        print(f'{village_id}:"{title[:-9]}" побуловано до {int(title[-2:]) + 1} рівня')
                        # Якщо побудовано до рівня вказаного користувачем тоді видаляємо зі елемент зі словника
                        if int(title[-2:]) + 1 == builds[object_tag][0]:
                            builds.pop(object_tag)
                        break

            # Після проходж. списку будівництві, все ще не виконується будівн. значить невистачає ресурсів
            if not self.time_to_complete_building():
                print(village_id + ': Немає ресурсів на будівництво жодної будівлі зі списку, очікуємо')
                return 900
        else:
            print(f'{village_id}: До завершення будівництва {timer} секунд')
            return int(timer)



if __name__ == '__main__':
    asia = TravianBot('https://ts30.x3.asia.travian.com', get_driver('Firefox_Profile2'))
    asia.building({'1': [[10, 20], [15, 33], [20, 15]],
                   '2': [[5, 5], [5, 6], [10, 33]],
                   '3': [[12, 10], [12, 11], [8, 1], [8, 2]],
                   })
    asia.driver.quit()