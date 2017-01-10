from sys import platform as _platform
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json, os, time


email = 'AAAA'
password = 'AAAA'

kijiji_urls = {
    'new_base': 'https://www.kijiji.ca/p-select-category.html',
    'login': 'https://www.kijiji.ca/t-login.html',
    'profile': 'https://www.kijiji.ca/m-my-ads.html',
}

current_folder = os.path.dirname(os.path.abspath(__file__))
source_data = os.path.join(current_folder, 'data.txt')
chrome_path = ''
data = ''
driver = ''


def set_chrome():
    global chrome_path
    global driver

    if _platform == "linux" or _platform == "linux2":
        chrome_path = os.path.join(current_folder, 'chromedriver_linux64')
    elif _platform == "darwin":
        chrome_path = os.path.join(current_folder, 'chromedriver_mac64')
    elif _platform == "win32":
        chrome_path = os.path.join(current_folder, 'chromedriver_win32')
    driver = webdriver.Chrome(chrome_path)


def read_data():
    global data

    with open(source_data) as data_file:
        data = json.loads(data_file.read())
    return 1


def login():
    global driver

    driver.get(kijiji_urls['login'])

    while driver.execute_script('return document.readyState;') != 'complete':
        pass

    username_element = driver.find_element_by_id("LoginEmailOrNickname")
    username_element.send_keys(email)
    password_element = driver.find_element_by_id("login-password")
    password_element.send_keys(password)
    password_element.submit()

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "LocUpdate")))
    driver.find_element_by_xpath("//*[contains(text(), 'Ontario (M - Z)')]").click()
    time.sleep(0.5)
    driver.find_element_by_xpath("//*[contains(text(), 'Toronto (GTA)')]").click()
    time.sleep(0.5)
    driver.find_element_by_xpath("//*[contains(text(), 'City of Toronto')]").click()
    time.sleep(0.5)
    driver.find_element_by_id('LocUpdate').click()

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "SearchSubmit")))

    return 1


def post_all():
    for info in data:
        post(info)


def post(info):
    global driver

    driver.get(kijiji_urls['new_base'])
    while driver.execute_script('return document.readyState;') != 'complete':
        pass

    for category in info['category']:
        driver.find_element_by_partial_link_text(category).click()
        while driver.execute_script('return document.readyState;') != 'complete':
            pass

    while driver.execute_script('return document.readyState;') != 'complete':
        pass

    if info['ad_type'] == 'offer':
        driver.find_element_by_id('adType1').click()
    else:
        driver.find_element_by_id('adType2').click()

    if info['price'] == 'free':
        driver.find_element_by_id('priceType2').click()
    elif info['price'] == 'contact':
        driver.find_element_by_id('priceType3').click()
    elif info['price'] == 'trade':
        driver.find_element_by_id('priceType4').click()
    else:
        driver.find_element_by_id('priceType1').click()
        driver.find_element_by_id('priceAmount').send_keys(info['price'])

    if info['sale_by'] == 'owner':
        driver.find_element_by_css_selector("input[value='ownr']").click()
    else:
        driver.find_element_by_css_selector("input[value='delr']").click()

    driver.find_element_by_id('postad-title').send_keys(info['title'])
    driver.find_element_by_id('pstad-descrptn').send_keys(info['description'])

    location_dropdown = driver.find_element_by_id('locationLevel0')
    for option in location_dropdown.find_elements_by_tag_name('option'):
        if info['location'].upper() in option.text.upper():
            option.click()
            break

    driver.find_element_by_id('PostalCode').send_keys(info['postal_code'])
    driver.find_element_by_id('pstad-map-address').send_keys(info['address'])

    for ind, image in enumerate(info['images']):
        driver.find_element_by_xpath("//input[@type='file']").send_keys(os.getcwd() + image)
    time.sleep(30)

    driver.find_element_by_xpath('//*[@id="MainForm"]/div[7]/button[1]').click()
    time.sleep(10)
    return 1


def delete_all():
    global driver

    driver.get(kijiji_urls['profile'])
    while driver.execute_script('return document.readyState;') != 'complete':
        pass
    time.sleep(5)

    elements = driver.find_elements_by_css_selector("a[id*='delete-ad']")
    elements_count = len(elements)
    
    print("Deleting %s items." % str(elements_count))

    for ind in range(0, elements_count):
        print ("Deleting item number %s." % str(ind + 1))
        success = False
        while not success:
            try:
                elements = driver.find_elements_by_css_selector("a[id*='delete-ad']")
                elements[0].click()
                time.sleep(2)
                driver.find_element_by_id("DeleteSurveyOK").click()
                time.sleep(10)
            except:
                pass
            finally:
                success = True

    return 1


def repost():
    set_chrome()
    read_data()
    login()
    delete_all()
    post_all()


repost()
