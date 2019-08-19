import sys
import os

def jumpLines(file, numOfLines):
    for count in range(numOfLines):
        file.readline()