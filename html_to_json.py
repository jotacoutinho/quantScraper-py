import sys
import os
import time
import json
from Pair import Pair
from Period import Period
from Utils import *

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
        if (line.find('Diario') != -1):
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