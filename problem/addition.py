import sys
check = "3\n"
def set_problem(loclist):
    loclist["Post Office"].outgoing = [1, 2]

testphase = 0
check_test = ["8\n", "6\n", "0\n"]
def set_test(loclist, i):
    if i == 0:
        loclist["Post Office"].outgoing = [3, 5]
    elif i == 1:
        loclist["Post Office"].outgoing = [2, 4]
    elif i == 2:
        loclist["Post Office"].outgoing = [9, -9]