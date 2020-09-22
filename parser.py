import json

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType


input_email = 'dtest-1984@gmail.com'
input_password = 'Test!234'

# Not working right now
myProxy = ''
proxyF = Proxy({
    'proxyType': ProxyType.MANUAL,
    'httpProxy': myProxy,
    'ftpProxy': myProxy,
    'sslProxy': myProxy,
    'noProxy': '' # set this value as desired
})


def await_element(driver,selector):
    try:
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        WebDriverWait(driver, 180).until(element_present)
    except TimeoutException:
        raise

# Overwrite Selenium headers
profile = webdriver.FirefoxProfile()
profile.set_preference("general.useragent.override", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36")


break_out = False
title_cards = [] # list of items
sections = [] # list of sections for output
category = 0 # Index of current section
card = 0 # Index of current title card

#
while True:
    if break_out:
        break
    # Init drive
    driver = webdriver.Firefox(profile)
    # Go to domain page
    driver.get("https://www.disneyplus.com/")
    await_element(driver,'button[aria-label*="Log in"]')
    driver.find_element_by_css_selector('button[aria-label*="Log in"]').click()

    # Send Email
    await_element(driver,'#email')
    email = driver.find_element_by_css_selector('#email')
    email.click()
    email.send_keys(Keys.HOME)
    email.send_keys(input_email)
    await_element(driver,'button[value="submit"]')
    driver.find_element_by_css_selector('button[value="submit"]').click()


    # Send Password
    await_element(driver,'#password')
    password = driver.find_element_by_css_selector('#password')
    password.send_keys(Keys.HOME)
    password.send_keys(input_password)
    await_element(driver,'button[value="submit"]')
    WebDriverWait(driver,2)
    driver.find_element_by_css_selector('button[name="dssLoginSubmit"]').click()



    # Get needed Category
    await_element(driver,'#home-collection > div')
    home_page_sliders = driver.find_elements_by_css_selector('#home-collection > div')[2:] # drop 2 first menu



    visible_card = len(home_page_sliders[0].find_elements_by_css_selector('div.slick-active')) # just for check


    while True:


        #categoty_slider = driver.find_elements_by_css_selector('#home-collection > div')[2:][category]

        # Await all cards loaded
        cards_wait = WebDriverWait(driver, 40)
        cards_wait.until(lambda driver: len(driver.find_elements_by_css_selector('#home-collection > div')[2:][category].find_elements_by_css_selector('div.slick-slide')) != visible_card)

        # Sliks it's cads in current category
        sliks = driver.find_elements_by_css_selector('#home-collection > div')[2:][category].find_elements_by_css_selector('div.slick-slide')

        # check image load necessary for title and img url information
        try:
            img_info = sliks[card].find_element_by_css_selector('img')
        except:
            while True:
                WebDriverWait(driver, 2)

                # Press slider to right
                driver.find_elements_by_css_selector('#home-collection > div')[2:][category].find_element_by_css_selector(
                        'button.slick-next:not(.slick-disabled)').click()
                try:
                    # Check updated slider
                    img_info = driver.find_elements_by_css_selector('#home-collection > div')[2:][category].find_elements_by_css_selector('div.slick-slide')[card].find_element_by_css_selector('img')
                    break
                except:
                    continue
        # Name of item
        title = img_info.get_attribute("alt")
        img_url = img_info.get_attribute("src")

        # Press a outside the vision zone
        try:
            element = sliks[card].find_element_by_css_selector('a')
            driver.execute_script("arguments[0].click();", element)
        except:
            WebDriverWait(driver, 2)

        # Await detail page
        wait = WebDriverWait(driver, 20)
        wait.until(lambda driver: driver.current_url != "https://www.disneyplus.com/")

        # Title url
        title_url = driver.current_url
        print(title_url)
        WebDriverWait(driver, 4)
        driver.back()

        # Check back button is correct return
        try:
            wait_back = WebDriverWait(driver, 5)
            wait_back.until(lambda driver: driver.current_url != title_url)
        except:
            driver.back()

        # Write item
        title_cards.append({"name":title, "url_img":img_url,"url":title_url})

        # Again check all cards loaded
        await_element(driver, '#home-collection > div')
        cards_wait.until(lambda driver: len(driver.find_elements_by_css_selector('#home-collection > div')[2:][category].find_elements_by_css_selector('div.slick-slide')) != visible_card)

        # Update card index and
        if card!=len(driver.find_elements_by_css_selector('#home-collection > div')[2:][category].find_elements_by_css_selector('div.slick-slide'))-1:
            card += 1
        else:
            sections.append({"name":driver.find_elements_by_css_selector('#home-collection > div')[2:][category]
                            .find_element_by_css_selector('h4').text, "Items":title_cards})
            title_cards = []
            print(sections)
            category += 1
            card = 0
            if category == len(driver.find_elements_by_css_selector('#home-collection > div')[2:]):
                break_out = True
            driver.close()
            break


with open('data.json', 'w') as f:
    json.dump({"Sections":sections}, f)






