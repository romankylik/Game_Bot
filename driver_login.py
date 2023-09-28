import time
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException

#domen_URL = 'https://sow.x3.europe.travian.com'
domen_URL = 'https://ts30.x3.asia.travian.com'

def get_driver():
    URL = domen_URL+'/dorf1.php'
    options = Options()
    # Задаємо опцію власного профіля для драйвера
    options.add_argument('-profile')
    # Додаткова опція не відкривати графічне вікно браузера(робота у фоновому режимі, за бажанням)
    ##options.add_argument('-headless')
    # Вказуємо шлях до профілю браузера( в цьому випадку він в папці проекту)
    options.add_argument('.\\Firefox_Profile2')
    #-Відкрийте веб-браузер Firefox.
    #-Введіть ' about:profiles ' у адресному рядку браузера Firefox.
    #-Копієюмо папку профілю браузера Firefox в папку проекту, по бажанню можна перейменувати папку
    #-Наприклад, шлях може виглядати схоже на '...\user\AppData\Roaming\Mozilla\Firefox\Profiles\xxxxxxxx.default-release'
    #-Де 'xxxxxxxx.default-release' яку потрібно скопіювати"""
    return webdriver.Firefox(options=options)

def login_in(driver, URL):

    # Відкриваємо веб-сторінку для авторизації
    counter = 0
    while counter < 4:
        try:
            driver.get(URL)
            # Чекаємо, поки елемент з ім'ям 'name' не буде видимим
            time.sleep(2)
            # Знаходимо поля для введення логіну та паролю
            username_field = driver.find_element(By.NAME, 'name')
            password_field = driver.find_element(By.NAME, "password")
            break
        except:
            driver.get(domen_URL)
            time.sleep(3)
            counter += 1

    # Введення логіну та паролю
    username_field.send_keys("gada94")
    password_field.send_keys("gada11291994")
    time.sleep(2)
    # Відправлення форми авторизації
    username_field.submit()
    time.sleep(1)
    return driver
