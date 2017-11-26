import sys

check = "0"

def set_problem(loclist):
    global testphase
    loclist["Post Office"].outgoing = [3]
    testphase = 0

testphase = 0
check_test = ["0", "0", "0"]

def set_test(loclist, i):
    if i == 0:
        loclist["Post Office"].outgoing = [8]
    elif i == 1:
        loclist["Post Office"].outgoing = [5]
    elif i == 2:
        loclist["Post Office"].outgoing = [475025373]
