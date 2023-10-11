import pickle
import re
import threading
import time
from multiprocessing import Process

from selenium.webdriver.common.by import By
import requests
from driver_login import *





driver = get_driver()
def check_login(URL):
    try:
        driver.get(URL)
        driver.find_element(By.ID, 'outOfGame')
    except NoSuchElementException:
        return login_in(driver, URL)



def building_one_object(name_villag: str, max_level: int, build_id: int, build_gid: int):
    check_login(domen_URL + '/dorf1.php')
    # Список існуючих поселень
    villages = check_villages(driver)
    # Перевірка чи правильно вказана назва поселення користувачем
    while name_villag not in villages:
        name_villag = input(f"Поселення {name_villag} не знайдено,введіть заново: ")
    while True:
        try:
            if time_to_complete_building(driver, domen_URL+'/dorf2.php' + '?newdid='+villages[name_villag]+'&'):
                time.sleep(1)
                build_URL = f'{domen_URL}/build.php?id={build_id}&gid={build_gid}'

                # Починаємо будівництво/ Якщо функція start_building повертає 'max' значить будівля побудована до рівня max_level
                if start_building(driver, build_URL, max_level) == 'max':
                    break
                time.sleep(1)
        except:
            time.sleep(50)
            check_login(domen_URL+"/dorf2.php")

    print(f'Будування до рівня {max_level} успішно завершено!')

def building_all_object(name_villagе: str, max_level: int, type_object=None):
    check_login(domen_URL+'/dorf1.php')
    time.sleep(1)
    # Список існуючих поселень
    villages = check_villages(driver)
    resources = {
        "Дерево": 'gid1',
        "Глина": 'gid2',
        "Залізо": 'gid3',
        "Зерно": 'gid4',
    }
    # Перевірка чи правильно вказана назва поселення користувачем
    while name_villagе not in villages:
        name_villagе = input(f"Поселення {name_villagе} не знайдено,введіть заново: ")

    while True:
        try:
            if time_to_complete_building(driver, domen_URL+'/dorf1.php' + '?newdid='+villages[name_villagе]+'&'):
                time.sleep(1)
                container = driver.find_element(By.ID, 'resourceFieldContainer')
                # ЯКщо не вказано тип ресурсу то будуємо всі
                if type_object not in resources:
                    print("Вказаний тип ресурсів не знайдено, будуємо всі")
                    all_object = container.find_elements(By.CSS_SELECTOR, 'a.colorLayer')
                else:
                    print(f"Будуємо всі поля типу {type_object}")
                    all_object = container.find_elements(By.CSS_SELECTOR, 'a.' + resources[type_object])
                # Отримаємо список рівнів всіх ресурсних полів одного типу
                levels_object = [int(a_tag.text) if a_tag.text != '' else 0 for a_tag in all_object]
                if min(levels_object) == max_level:
                    break
                for one_bild in all_object:
                    if one_bild.text == str(min(levels_object)) or one_bild.text == '':
                        # Починаємо будівництво
                        start_building(driver, one_bild.get_attribute('href'))
                        time.sleep(3)
                        break
        except NoSuchElementException:
            time.sleep(60)
            check_login(domen_URL+"/dorf1.php")

    print(f'Будування до рівня {max_level} успішно завершено!')

def check_villages(driver):
    villages = {}
    for div in driver.find_elements(By.CSS_SELECTOR, 'div.listEntry'):
        villages[div.find_element(By.CSS_SELECTOR, 'span.name').text] = div.get_attribute('data-did')
    return villages




def time_to_complete_building(driver, URL):
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



def start_building(driver , URL, lvl=100):
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
        if int(re.search(r'\d+', clic_bild.text).group()) > lvl:
            print("Будівля побудована до вказаного вами рівня")
            return 'max'
        title = driver.find_element(By.CSS_SELECTOR, '.titleInHeader').text
        clic_bild.click()
        print(f'Будівлю "{title}" побуловано успішно')
    except:
        if check_login(URL):
            return print("Вхід виконано під час будування")
        else:
            print('Не вистачає ресурсів на будівництво, очікуємо')
            time.sleep(900)

# Вдосконалення "Баллиста" в академії (Важливо яка мова інтерфейсу гри)
def up_in_academy(driver: webdriver ):

    try:
        # Вдосконаленні в академії
        driver.get(domen_URL+'/build.php?id=28&gid=22')
        time.sleep(3)
        # Пошук "Баллиста"
        academy_buttons = driver.find_elements(By.CLASS_NAME, 'information')
        time.sleep(3)
        for element in academy_buttons:
            if "Баллиста" in element.text:
                cta_element = element.find_element(By.CLASS_NAME, 'cta')
                button_element = cta_element.find_element(By.TAG_NAME, 'button')
                button_element.click()
                print("ВИКОНАНО ДОСЛІДЖЕННЯ В АКАДЕМІЇ")
                driver.get(domen_URL+'/dorf2.php')
        time.sleep(3)

    except:
        print('Дослідження в академії не виконано')




def requests_do():
    # Створіть сеанс Requests
    session = requests.Session()
    cookies_data = driver.get_cookies()
    user_agent = {'User-Agent': driver.execute_script("return navigator.userAgent;")}
    #driver.quit()

    for cookie in cookies_data:
        session.cookies.set(cookie['name'], cookie['value'])

    page = session.get(domen_URL+'/dorf1.php?newdid=16042&', headers=user_agent).text

    # зберігаю html код у файл
    with open('page_dorf1.txt', 'wb') as page_dorf1:
        pickle.dump(page, page_dorf1)
    page_dorf1.close()

    return page

def first():
    building_one_object('1', 16, 20, 10)  # Склад
    building_one_object('1', 12, 23, 17)  # Склад
def second():
    building_all_object('2', 2)
    building_all_object('2', 3)
    building_one_object('2', 7, 21, 11)
    building_one_object('2', 16, 20, 10)


if __name__ == '__main__':
    ...
    #building_all_object('2', 8, "Дерево")
    #building_all_object('2', 8, "Глина")
    #building_all_object('2', 8, "Залізо")
    #building_all_object('2', 8, "Зерно")


    building_all_object('3', 8)

    #building_one_object('1', 10, 26, 15)
    #building_one_object('1', 12, 22, 11)  # Комора
    #building_one_object('1', 12, 26, 15)  # Головна будівля
    #building_one_object('1', 10, 19, 25)  # Склад
      # Якщо некорекний або взагалі немає типу ресурсного поля то будує всі поля


    driver.quit()



