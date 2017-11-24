import sys
check = "1\n"
def set_problem_xor(loclist):
    loclist["Post Office"].outgoing = [1, 0]

testphase = 0
check_test = ["0\n", "0\n", "1\n"]
def set_test_add(loclist, i):
    if i == 0:
        loclist["Post Office"].outgoing = [1, 1]
    elif i == 1:
        loclist["Post Office"].outgoing = [0, 0]
    elif i == 2:
        loclist["Post Office"].outgoing = [0, 1]