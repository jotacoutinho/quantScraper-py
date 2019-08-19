from selenium import webdriver
from browsermobproxy import Server
from pynput.keyboard import Key, Controller
import sys
import os
import time
import json
import base64
import struct
import codecs
import re
import brotli
from Pair import Pair
from Period import Period
from Utils import *

keyboard = Controller()

# Step 1: open Chrome at QuantGO.com.br

# Step 8: generating HAR to get chart info (response)
server = Server('C:/Users/jotap/AppData//Local/Programs/Python/Python37/Lib/site-packages/browsermobproxy/browsermob-proxy-2.1.4/bin/browsermob-proxy')
server.start()
proxy = server.create_proxy()
profile = webdriver.FirefoxProfile()
profile.set_proxy(proxy.selenium_proxy())

#browser = webdriver.Chrome(executable_path='C:/Users/jotap/AppData/Local/Programs/Python/Python37/Scripts/chromedriver_win32/chromedriver.exe') #replace with .Firefox(), or with the browser of your choice
browser = webdriver.Firefox(firefox_profile=profile, executable_path='C:/Users/jotap/AppData/Local/Programs/Python/Python37/Scripts/geckodriver_v0.24.0/geckodriver.exe')

url = "https://portal.quantgo.com.br"
#

browser.get(url)
browser.maximize_window()

# Step 2: login
username = browser.find_element_by_name("email")
password = browser.find_element_by_name("password")

username.send_keys("matheusbaumbachnascimento@gmail.com")
password.send_keys("senha123")

keyboard.press(Key.enter)
keyboard.release(Key.enter)

# Step 3: manual filter configuration
#filterUrl = "https://portal.quantgo.com.br/long-short/cointegration"
#browser.get(filterUrl)

proxy.new_har("charts", options={'captureHeaders':True, 'captureContent':True, 'captureBinaryContent':True})

try:
    input("Press enter to continue after selecting a filter and loading the list of pairs ")
except SyntaxError:
    pass

# Step 4: fetch information
elementsCounter = 0
numOfPairs = 0
index = 0

stopGettingPairs = False

if browser.find_elements_by_css_selector("material-icons").count != 0:
    for element in browser.find_elements_by_class_name("material-icons"):
        elementsCounter = elementsCounter + 1
    print(elementsCounter)
    for element in browser.find_elements_by_class_name("material-icons"):
        if ((index > 10) and (numOfPairs < elementsCounter - 12)):
            if(stopGettingPairs == False):
                element.click()
                numOfPairs = numOfPairs + 1
                time.sleep(4)
                stopGettingPairs = True
        index = index + 1

innerHTML = browser.execute_script("return document.body.innerHTML")
output = open("rawOutput.txt", "w")
output.write(innerHTML)
output.close()


# chart

try:
    input("Press enter to extract data from a chart")
except SyntaxError:
    pass


elements = 0
for element in browser.find_elements_by_class_name("material-icons"):
    if (elements == 13):
        element.click()
    elements = elements + 1

print('elements: ', elements)

#browser.get("https://portal.quantgo.com.br/api/operations/residue_graph?")
#print(proxy.har)

for ent in proxy.har['log']['entries']:
    _url = ent['request']['url']
    if(_url == "https://portal.quantgo.com.br/api/operations/residue_graph?"):
        _response = ent['response']
        _content = _response['content']
        _chartInfo = _content['text']
        #print(_url)
        #print(_response)
        #print(_content)
        print(_chartInfo)
        #print('\n')

#altchars=b'+/'
#_chartInfo = re.sub(rb'[^a-zA-Z0-9%s]+' % altchars, b'', _chartInfo)
#decodedInfo = base64.b64decode(_chartInfo)
#b_string = codecs.encode(decodedInfo, 'hex')
#print(b_string.decode('utf-8').upper())
#print(decodedInfo)

print(brotli.decompress(_chartInfo))
result = json.dumps(proxy.har, ensure_ascii=False)

output = open("chart.har", "w")
output.write(str(result))
output.close()

#cleaned_data = []
#struct_format = ">ff"
#for i in range(len(decodedInfo) // 8):
#   cleaned_data.append(struct.unpack_from(struct_format, decodedInfo, 8*i))

#print(cleaned_data)

#chartJson = json.loads(decodedInfo)
#print(chartJson)

server.stop()
# Step 5: scrape data for further analysis

pairIndex = 0
numOfParams = 9
numOfPeriods = 0
data = []
lineCount = 0
currentPair = ""
currentPeriods = []
pairs = []

with open('rawOutput.txt', 'r') as myFile:
    line = myFile.readline()
    while line:
        line = myFile.readline()
        if (line.find('Diário') != -1):
            jumpLines(myFile, 1)

            # this line has the numOfPeriods
            line = myFile.readline() 
            numOfPeriods = int(line[::-1].split('p')[1][2::].split('>')[0][::-1])

            jumpLines(myFile, 6)

            # getting pair name
            line = myFile.readline()
            currentPair = line[::-1].split('p')[1][2::].split('>')[0][::-1] + " vs. "
            line = myFile.readline()
            currentPair = currentPair + line[::-1].split('p')[1][2::].split('>')[0][::-1]

        elif (line.find('<!----><tbody _ngcontent-c5="">') != -1):
            periodCount = 0
            # list of periods
            while (periodCount < numOfPeriods):
                readingCount = 0
                jumpLines(myFile, 1)
                
                # period
                while (readingCount < numOfParams):
                    line = myFile.readline()
                    data.append(line[::-1].split('p')[1][2::].split('>')[0][::-1])
                    readingCount = readingCount + 1

                    if(readingCount == 7):
                        jumpLines(myFile, 2)

                # saving period info
                currentPeriods.append(Period(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8]))
                periodCount = periodCount + 1
                data = []
                jumpLines(myFile, 12)

            # saving pair info
            #for period in periodCount
            pairs.append(Pair(str(pairIndex), currentPair, currentPeriods))
            pairIndex = pairIndex + 1
            currentPeriods = []

output = open("output.txt", "w")
for pair in pairs:
    #Pair.print(pair)
    #output.write(" ".join(str(x) for x in data))
    output.write(pair.toJSON())
output.close()

# Step 6: write data
# output = open("output.txt", "w")
# output.write(" ".join(str(x) for x in data))
# output.close()

# Step 7: first analysis -> get potential periods and perform click to see each chart
# summary: track pair index, period index and compare to number of material-icons apearances
# e.g.: get chart info from bestPeriod = pair[2].period[3]
# get HTML line for bestPeriod
# count number of material-icons and track index of bestPeriod line
# index = 0
# for element in browser.find_elements_by_class_name("material-icons"):
#   if index == bestPeriodIndex
#       element.click()
#   index = index + 1

# Step 8: generating HAR to get chart info (response)
#server = Server('C:/Users/jotap/AppData/Local/Programs/Python/Python37/Lib/site-packages/browsermobproxy')
#server.start()
#proxy = server.create_proxy()

#profile = webdriver.FirefoxProfile()
#profile.set_proxy(proxy.selenium_proxy())

#try:
#    input("Press enter to extract data from a chart after pressing the detail button")
#except SyntaxError:
#    pass

#server.stop()

#print("Finished!\nNumber of cointegrated pairs = ", numOfPairs)
