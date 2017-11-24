import sys
sys.path.append("..")
from driver import *

def setEasy(w, h):
    loclist = {}
    the_map = [[None for i in range(h)]for j in range(w)]

    # make the map
    loclist["Taxi Garage"] = location(300, 100, "Taxi Garage")
    loclist["Taxi Garage"].description = "Start and Goal. If you arrive here, the program will end."
    loclist["Taxi Garage"].arrival_function = taxi_garage
    the_map[300][100] = loclist["Taxi Garage"]
    the_map[299][100] = location(299, 100, "Wall")
    the_map[300][99] = location(300, 99, "Wall")

    loclist["Post Office"] = location(700, 500, "Post Office")
    loclist["Post Office"].description = "Pickup Input and discharge Output."
    loclist["Post Office"].arrival_function = post_office_arrive
    loclist["Post Office"].create_outgoing_passenger_function = post_office_create
    the_map[700][500] = loclist["Post Office"]
    the_map[700][501] = location(700, 501, "Wall")
    the_map[701][500] = location(701, 500, "Wall")

    loclist["What's the Difference"] = location(500, 300, "What's the Difference")
    loclist["What's the Difference"].description = "You can pickup the value '1st (- 2nd - 3rd)'."
    loclist["What's the Difference"].create_waiting_passenger_function = whats_the_difference
    the_map[500][300] = loclist["What's the Difference"]

    loclist["Addition Alley"] = location(500, 500, "Addition Alley")
    loclist["Addition Alley"].description = "You can pickup the value '1st (+ 2nd + 3rd)'."
    loclist["Addition Alley"].arrival_function = addition_alley
    the_map[500][500] = loclist["Addition Alley"]
    the_map[500][501] = location(500, 501, "Wall")

    loclist["Multiplication Station"] = location(700, 300, "Multiplication Station")
    loclist["Multiplication Station"].description = "You can pickup the value '1st (* 2nd * 3rd)'."
    loclist["Multiplication Station"].arrival_function = multiplication_station
    the_map[700][300] = loclist["Multiplication Station"]
    the_map[701][300] = location(701, 300, "Wall")

    loclist["Divide and Conquer"] = location(700, 100, "Divide and Conquer")
    loclist["Divide and Conquer"].description = "You can pickup the value '1st (/ 2nd / 3rd)'."
    loclist["Divide and Conquer"].arrival_function = divide_and_conquer
    the_map[700][100] = loclist["Divide and Conquer"]
    the_map[700][99] = location(700, 99, "Wall")
    the_map[701][100] = location(701, 100, "Wall")

    loclist["Cyclone"] = location(500, 100, "Cyclone")
    loclist["Cyclone"].description = "You can make copy of passengers."
    loclist["Cyclone"].arrival_function = cyclone
    the_map[500][100] = loclist["Cyclone"]
    the_map[500][99]=location(500,99,"Wall")

    loclist["Fueler Up"] = location(300, 500, "Fueler Up")
    loclist["Fueler Up"].description = "Gallon Station. You cannot pass through. 1.92dollar/gallon."
    loclist["Fueler Up"].gas_price = 1.92
    loclist["Fueler Up"].max_passengers = 0
    the_map[300][500] = loclist["Fueler Up"]
    the_map[299][500] = location(299, 500, "Wall")
    the_map[300][501] = location(300, 501, "Wall")

    loclist["Riverview Bridge"] = location(300, 300, "Riverview Bridge")
    loclist["Riverview Bridge"].description = "Discharged passengers will disappear and you'll get no money."
    loclist["Riverview Bridge"].arrival_function = riverview_bridge
    loclist["Riverview Bridge"].passengers_pay = False
    the_map[300][300] = loclist["Riverview Bridge"]
    the_map[299][300] = location(299, 300, "Wall")

    road = [    [[300,100],[300,300]],
                [[300,300],[300,500]],
                [[500,300],[500,500]],
                [[300,300],[500,300]],
                [[300,500],[500,500]],
                [[500,500],[700,500]],
                [[500,300],[700,300]],
                [[700,100],[700,300]],
                [[700,300],[700,500]],
                [[300,100],[500,100]],
                [[500,100],[700,100]],
                [[500,100],[500,300]]   ]

    # 1 mile: 16.5 pixels
    # Max gallons of gas: 20
    # Starting gallons: 20
    # miles per gallon: 18
    # starting credits: 0
    # fare in credits per mile: 0.07
    car = taxi(loclist["Taxi Garage"], 16.5, 20.0, 20.0, 18.0, 0.0, 0.07)

    return [car, the_map, loclist, road]
