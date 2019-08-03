from selenium import webdriver
from pynput.keyboard import Key, Controller
import sys
import os
import time
import json

keyboard = Controller()

# Step 1: open Chrome at QuantGO.com.br
browser = webdriver.Chrome(executable_path='C:/Users/jotap/AppData/Local/Programs/Python/Python37/Scripts/chromedriver_win32/chromedriver.exe') #replace with .Firefox(), or with the browser of your choice
url = "https://portal.quantgo.com.br"
browser.get(url)
browser.maximize_window()


# Step 2: login
username = browser.find_element_by_name("email")
password = browser.find_element_by_name("password")

username.send_keys("jotapedrocoutinho@hotmail.com")
password.send_keys("senha123")

keyboard.press(Key.enter)
keyboard.release(Key.enter)

# Step 3: manual filter configuration
#filterUrl = "https://portal.quantgo.com.br/long-short/cointegration"
#browser.get(filterUrl)

try:
    input("Press enter to continue after selecting a filter and loading the list of pairs ")
except SyntaxError:
    pass

# Step 4: fetch information
elementsCounter = 0
counter = 0
index = 0

if browser.find_elements_by_css_selector("material-icons").count != 0:
    for element in browser.find_elements_by_class_name("material-icons"):
        elementsCounter = elementsCounter + 1

    for element in browser.find_elements_by_class_name("material-icons"):
        if ((index > 9) and (counter < elementsCounter - 11)):
            element.click()
            counter = counter + 1
            time.sleep(2)
        index = index + 1

innerHTML = browser.execute_script("return document.body.innerHTML")

# Step 5: write HTML into JSON for further analysis
jsonHTML = json.dumps(innerHTML)
output = open("output.txt", "w")
output.write(jsonHTML)
output.close()

print("Finished!\nNumber of cointegrated pairs = ", counter)
