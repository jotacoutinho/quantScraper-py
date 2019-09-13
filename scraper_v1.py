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
server = Server('C:/Users/jotap/AppData//Local/Programs/Python/Python37/Lib/site-packages/browsermobproxy/browsermob-proxy-2.1.4/bin/browsermob-proxy')
server.start()
proxy = server.create_proxy()
profile = webdriver.FirefoxProfile()
profile.set_proxy(proxy.selenium_proxy())
profile.accept_untrusted_certs = True
profile.assume_untrusted_cert_issuer = False
#co = webdriver.ChromeOptions()
#co.add_argument('--proxy-server={host}:{port}'.format(host='localhost', port=proxy.port))

#driver = webdriver.Chrome(executable_path = "~/chromedriver", chrome_options=co)
#browser = webdriver.Chrome(executable_path='C:/Users/jotap/AppData/Local/Programs/Python/Python37/Scripts/chromedriver_win32/chromedriver.exe', options=co) #replace with .Firefox(), or with the browser of your choice
browser = webdriver.Firefox(firefox_profile=profile, executable_path='C:/Users/jotap/AppData/Local/Programs/Python/Python37/Scripts/geckodriver_v0.24.0/geckodriver.exe')

url = "https://portal.quantgo.com.br"
browser.get(url)
browser.maximize_window()

# Step 2: login
username = browser.find_element_by_name("email")
password = browser.find_element_by_name("password")

username.send_keys("matheusbaumbachnascimento@gmail.com")
password.send_keys("*********")

keyboard.press(Key.enter)
keyboard.release(Key.enter)

# Step 3: manual filter configuration
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
    for element in browser.find_elements_by_class_name("material-icons"):
        if ((index > 10) and (numOfPairs < elementsCounter - 12)):
            if(stopGettingPairs == False):
                element.click()
                numOfPairs = numOfPairs + 1
                time.sleep(2)
                #FIXME: remove this to get info from all pairs
                stopGettingPairs = True
        index = index + 1

innerHTML = browser.execute_script("return document.body.innerHTML")
output = open("rawOutput.txt", "w")
output.write(innerHTML)
output.close()

# Step 5a: scrape data for further analysis

pairIndex = 0
numOfParams = 9
numOfPeriods = 0
data = []
lineCount = 0
currentPair = ""
currentPeriods = []
pairs = []
currentPreferedPeriod = 0

# decision variables
maxBetaDelta = 2

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
                #jumpLines(myFile, 1)
                line = myFile.readline()
                # getting green line
                if (line.find('rgb(') != -1):
                    currentPreferedPeriod = periodCount
                
                # period
                while (readingCount < numOfParams):
                    line = myFile.readline()
                    data.append(line[::-1].split('p')[1][2::].split('>')[0][::-1])
                    readingCount = readingCount + 1

                    if(readingCount == 3):
                        jumpLines(myFile, 3)
                    if(readingCount == 7):
                        jumpLines(myFile, 2)

                # saving period info
                currentPeriods.append(Period(periodCount, data[0], data[1], float(data[2][:-1].replace(',', '.')), float(data[3].replace(',', '.')), data[4], float(data[5][:-1].replace(',', '.')), data[6], data[7], data[8]))
                periodCount = periodCount + 1
                data = []
                jumpLines(myFile, 12)

            # saving pair info
            #for period in periodCount
            pairs.append(Pair(str(pairIndex), currentPair, currentPeriods))
            pairIndex = pairIndex + 1
            currentPeriods = []

# Step 5b: get chart data for further analysis
            # Decision making: only analysing pairs with low beta variation
            sortedByBeta = sorted(pairs[pairIndex - 1].periods, key=lambda x: (x["beta"]), reverse=True)
            if ((sortedByBeta[0].beta - sortedByBeta[periodCount - 1].beta) < maxBetaDelta):

                try:
                    input("Press enter to extract data from a chart")
                except SyntaxError:
                    pass

                proxy.new_har("charts", options={'captureHeaders':True, 'captureContent':True, 'captureBinaryContent':True})
                
                #sorting perios by adf and fisher min
                rankedPeriods = sorted(pairs[pairIndex - 1].periods, key=lambda x: (x["adf"], x["fisherMin"]), reverse=True)

                #click to open chart for prefered period
                elements = 0
                for element in browser.find_elements_by_class_name("material-icons"):
                    if (elements == 11 + 2 * (1 + currentPreferedPeriod)):
                        element.click()
                    elements = elements + 1

                time.sleep(5)

                for ent in proxy.har['log']['entries']:
                    _url = ent['request']['url']
                    if(_url == "https://portal.quantgo.com.br/api/operations/residue_graph?"):
                        _response = ent['response']
                        _content = _response['content']
                        #print(_content)
                        _chartInfo = _content['text']
                        #print(_chartInfo)

                decodedInfo = base64.b64decode(_chartInfo)
                chartData = brotli.decompress(decodedInfo)
                chartJson = json.loads(chartData)
                #print(chartJson["average"])
                #result = json.dumps(proxy.har, ensure_ascii=False)

                #time.sleep(10)
                
                output = open("chart.har", "w") #--> this works for getting chart data
                output.write(str(proxy.har))
                output.close()

                server.stop() 

                # if prefered fails
                #for period in rankedPeriods.count:
                    #extract chart data for pairs[pairIndex - 1].periods[perdiod["periodId"]]

output = open("output.txt", "w")
for pair in pairs:
    #Pair.print(pair)
    #output.write(" ".join(str(x) for x in data))
    output.write(pair.toJSON())
output.close()

server.stop()

#print(chartData)

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

# Analysis Stage
# 
# Variables 
# 
# Stage I)
# betaDelta -> check if |betaMax - betaMin| < betaDelta
#   irPairFavorite -> true if the period row is green
# 
# Stage II)
# residueAvgCount -> check if the residue hits the average this much
# residueStat -> true if the residue regression is stationary (i.e. if resideuAvgCount >= count from chart)
#   chartsMatch -> true if sign(firstChart[N] - firstChart[N-1]) != sign(secondChart[N] - secondChart[N-1])
# betaRotationDelta -> check if |betaMax - betaMin| < betaRotationDelta for volatilities
# residueDelta -> check if |residueMax - residueMin| < residueDelta for volatilities

