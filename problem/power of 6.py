import sys

check = "64"

def set_problem(loclist):
    loclist["Post Office"].outgoing = [2]

testphase = 0
check_test = ["729", "15625", "117649"]


def set_test(loclist, i):
    if i == 0:
        loclist["Post Office"].outgoing = [3]
    elif i == 1:
        loclist["Post Office"].outgoing = [5]
    elif i == 2:
        loclist["Post Office"].outgoing = [7]
