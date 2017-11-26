import sys
check = "1"


def set_problem(loclist):
    global testphase
    loclist["Post Office"].outgoing = [1, 0]
    testphase = 0

testphase = 0
check_test = ["0", "0", "1"]


def set_test(loclist, i):
    if i == 0:
        loclist["Post Office"].outgoing = [1, 1]
    elif i == 1:
        loclist["Post Office"].outgoing = [0, 0]
    elif i == 2:
        loclist["Post Office"].outgoing = [0, 1]
