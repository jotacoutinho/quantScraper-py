import sys
import os
import time
import json

numOfParams = 9
data = [] 
numOfPeriods = 0
lineCount = 0
hasPrinted = False

with open('exampleOutput.txt', 'r') as myfile:
    line = myfile.readline()
    while line:
        line = myfile.readline()
        if (line.find('Diário') != -1):
            line = myfile.readline()
            # FIXME read number properly
            line = myfile.readline() # this line has the numOfPeriods
            numOfPeriods = 1
            #numOfPeriods = myfile.readline()
        elif (line.find('<!----><tbody _ngcontent-c5="">') != -1):
            periodCount = 0
            # list of periods
            while (periodCount < numOfPeriods):
                readingCount = 0
                # jumps first line (useless)
                line = myfile.readline()
                # period
                while (readingCount < numOfParams):
                    line = myfile.readline()
                    data.append(line)
                    readingCount = readingCount + 1
                    # jumping empty lines
                    if(readingCount == 6):
                        line = myfile.readline()
                        line = myfile.readline()
                periodCount = periodCount + 1
                if(hasPrinted == False):
                    print(data)
                    hasPrinted = True
                # jumping empty lines
                myfile.readline()
                myfile.readline()
                myfile.readline()
                myfile.readline()
                myfile.readline()
                myfile.readline()
                myfile.readline()
                myfile.readline()
                myfile.readline()
                myfile.readline()
                myfile.readline()
                myfile.readline()
                myfile.readline()



#jsonHTML = json.dumps(data)
#output = open("output.txt", "w")
#output.write(jsonHTML)
#output.close()