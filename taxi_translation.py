"""
TAXI PROGRAMMING LANGUAGE
transrated by: HyuOgawa hyoga_quasar@yahoo.co.jp
LICENSE: Public Domain
"""
import math
import random
import sys
import re

#set nesw_t
D_WEST = 0
D_NORTH = 1
D_SOUTH = 2
D_EAST = 3

#set rel_dir_t
D_LEFT = 0
D_RIGHT = 1

# set buffer_type
B_FIFO = 0
B_LIFO = 1
B_RANDOM = 2

# set command_t
C_NONE = 0
C_WAITING = 1
C_GOTO = 2
C_SWITCH = 3
C_SWITCH_IF = 4
C_PICKUP = 5

class location:
    # value_list = list<taxi_value>
    __outgoing = []
    # buffer_type
    buffer_order = None
    # int
    max_passengers = 0
    # arrival_func
    arrival_function = None
    # create_outgoing_passenger_func
    create_outgoing_passenger_function = None
    # create_waiting_passenger_func
    create_waiting_passenger_function = None
    # bool
    passengers_pay = False
    # double
    gas_price = 0.0

    def __init__(self):
        self.buffer_order = B_FIFO
        self.max_passengers = -1 # infinite
        self.arrival_function = None
        self.create_outgoing_passenger_function = None
        self.create_waiting_passenger_function = None
        self.passengers_pay = True
        self.gas_price = 0.0
    
    # void add_outgoing_passenger(const taxi_value& v)
    def add_outgoing_passenger(self, v):
        assert self.max_passengers != 0 and len(self.__outgoing) != self.max_passengers,  "error: too many outgoing passengers:" + str(len(self.__outgoing)) 
        if self.buffer_order == B_FIFO:
            self.__outgoing.append(v)
        elif self.buffer_order == B_LIFO:
            self.__outgoing.insert(0, v)
        elif self.buffer_order == B_RANDOM:
            self.__outgoing.insert(random.randint(0,len(self.__outgoing)), v)
    
    # void arrival(incoming_list& incoming)
    def arrival(self, incoming):
        if debuglevel >= 2:
            print("outgoing:",end="")
            for i in range(len(self.__outgoing)):
                print(" [" + str(self.__outgoing[i]) + "]",end="")
            print("")
        
        if not self.arrival_function is None:
            self.arrival_function(incoming)
        else:
            while (not incoming.empty()) and (self.max_passengers == -1 or len(self.__outgoing) < self.max_passengers):
                add_outgoing_passenger(incoming.next())
    
    # int outgoing_passengers()
    def outgoing_passengers(self):
        return len(self.__outgoing)

    # taxi_value get_outgoing_passenger()
    def get_outgoing_passenger(self):
        assert self.max_passengers != 0,  "error: no outgoing passengers allowed at this location." 
        if self.outgoing_passengers() == 0 and (not create_outgoing_passenger_function is None):
            create_outgoing_passenger_function(self)
        assert self.outgoing_passengers() != 0,  "error: no outgoing passengers found" 
        #taxi_value
        r = self.__outgoing[0]
        del self.__outgoing[0]
        return r

    # void waiting(const char* input)
    def waiting(self, input):
        assert self.max_passengers != 0,  "no outgoing passengers allowed at this location" 
        assert not self.create_waiting_passenger_function is None,  "passengers cannot be made to wait here" 
        assert self.max_passengers == -1 or self.outgoing_passengers() > self.max_passengers,  "too many passengers already waiting here" 
        create_waiting_passenger_function(input)


class taxi:
    # passenger_list
    passengers = []
    # nesw_t
    direction = -1
    # node*
    current_node = None
    # location
    current_location = None
    # node*
    next_node = None
    prev_node = None
    # const double
    pixels_per_mile = 0.0
    max_gas = 0.0
    # double
    gas = 0.0
    gas_usage = 0.0
    credits = 0.0
    fare = 0.0
    miles_driven = 0.0

    # init(location* start_from, double ppm, double max_gax_, double gas_, double gas_usage_, double credits_, double fare_)
    def __init__(self, start_from, ppm, max_gas_, gas_, gas_usage_, credits_, fare_):
        self.direction = D_NORTH
        self.current_node = start_from
        self.current_location = start_from
        self.next_node = None
        self.prev_node = None
        self.pixels_per_mile = ppm
        self.max_gas = max_gas_
        self.gas = gas_
        self.gas_usage = gas_usage_
        self.credits = credits_
        self.fare = fare_
        self.miles_driven = 0.0
    
    # void pickup_passenger(location* whereto)
    def pickup_passenger(self, whereto):
        assert not self.current_location is None,  "error: not at a location where passengers can even be picked up from" 
        assert len(self.passengers)<3,  "error: too many passengers in the taxi" 
        self.passengers.append(passenger_t(self.current_location.get_outgoing_passenger(), whereto))
        
    #void passenger_pays(passenger_t& p)
    def passenger_pays(self, p):
        if not p.dest.passenger_pays is None:
            self.credits += p.distance_traveled * self.fare
    
    # void set_direction(nesw_t dir)
    def set_direction(self, dir):
        self.direction = dir
        self.next_node = current_node.get(self.direction)
    
    # void take_xth_turn(int num, rel_dir_t dir)
    def take_xth_turn(self, num, dir):
        # node*
        t = None
        while num>0:
            while True:
                self.__drive()
                t = self.current_node.can_turn(dir.prev_node)
                if t is None:
                    break
        self.next_node = t
        self.turn(dir)

    
    # void drive_to(node* to)
    def drive_to(self, to):
        n = to
        while self.current_node != n:
            self.drive()
        self.current_location = to
        il = incoming_list(self, self.current_location)
        self.current_location.arrival(il)
        il.update_taxi()
        if not self.current_location.gas_price is None:
            # double
            gallons = min(self.max_gas - self.gas, self.credits / self.current_location.gas_price)
            self.gas += gallons
            self.credits -= gallons * self.current_location.gas_price
            if debuglevel >= 1:
                print("You now have " + str(self.gas) + " gas and " + str(self.credits) + " credits.")
    
    # private void drive()
    def __drive(self):
        assert self.next_node is None,  "error: cannot drive in that direction" 
        # node*
        t = self.next_node.get_straight_path(self.current_node)
        self.prev_node = self.current_node
        self.next_node = t
        self.current_location = None

        # accounting...
        # double
        dist = self.prev_node.dist_to(self.current_node) / self.pixels_per_mile
        self.miles_driven += dist
        self.gas -= dist / self.gas_usage
        assert self.gas >= 0.0,  "error: out of gas" 

        for i in range(self.passengers):
            self.passengers.distance_traveled += dist
        
    # void turn(rel_dir_t dir)
    def __turn(self,dir):
        if self.direction==D_WEST:
            self.direction=D_SOUTH if dir==D_LEFT else D_NORTH
        elif self.direction==D_EAST:
            self.direction=D_NORTH if dir==D_LEFT else D_SOUTH
        elif self.direction==D_NORTH:
            self.direction=D_WEST if dir==D_LEFT else D_EAST
        elif self.direction==D_SOUTH:
            self.direction=D_EAST if dir==D_LEFT else D_WEST
        else:
            assert False,  "error: wrong direction\t" + str(self.direction) + "," + str(dir) 

class node:
    x = None
    y = None
    #neibor_list=list<node*,node*>
    neighbors = []

    def __init__(self, x_=0, y_=0):
        self.x = x_
        self.y = y_

    def position(self, x_, y_):
        self.x = x_
        self.y = y_

    @classmethod
    # static void street
    def street(cls, num_nodes, *args):
        if num_node < 2:
            return
        # node*
        p = None
        while num_nodes > 0:
            num_nodes -= 1
            # pair<node*,node*>
            e = [None, None]
            n = args[num_nodes]
            if p is None:
                e = [None, None]
            else:
                p.neighbors[-1][1] = n
                e = [p, None]
            if not e is None:
                n.neighbors.append(e)
            p = n

    # bool is_intersection
    def is_intersection(self):
        return len(self.neighbors) > 1
    
    # node* get_straight_path(node* from)
    def get_straight_path(self, f):
        for i in range(len(self.neighbors)):
            if self.neighbors[i][0] == f:
                return self.neighbors[i][1]
            elif self.neighbors[i][1] == f:
                return self.neighbors[i][0]
        return None

    # node* get(nesw_t dir, node* prev=null)
    def get(self, dir, prev=None):
        for i in range(len(self.neighbors)):
            if (prev is None) or (not prev in self.neighbors[i]):
                for j in range(2):
                    # node*
                    n = self.neighbors[i][j]
                    if n is None:
                        continue
                    b = False
                    if dir == D_NORTH:
                        b = n.y < self.y
                    elif dir == D_SOUTH:
                        b = n.y > self.y
                    elif dir == D_EAST:
                        b = n.x > self.x
                    elif dir == D_WEST:
                        b = n.x < self.x
                    if b:
                        return n
        return None

    # double dist_to(node* n)
    def dist_to(self, n):
        a = abs(self.x - n.x)
        b = abs(self.y - n.y)
        return math.sqrt(a * a + b * b)

    # node* can_turn(rel_dir_t dir, node* prev)
    def can_turn(self, dir, prev):
        for i in range(len(self.neighbors)):
            if not prev in self.neighbors[i]:
                for j in range(2):
                    n = self.neighbors[i][j]
                    if n is None:
                        continue
                    #gets outer product
                    r = ((self.x - prev.x) * (n.y - prev.y) + (self.y - prev.y) * (n.x - prev.x))**0.5
                    if dir == D_LEFT and r < 0:
                        return n
                    elif dir == D_RIGHT and r > 0:
                        return n
        return None
        
class passenger_t:
    dest = location()
    distance_traveled = None
    value = None

    def __init__(self, v = 0, d = None):
        dest = location(d)
        distance_traveled = 0.0
        value = v


class incoming_list:
    # taxi&
    __car=None
    # passenger_list
    __incoming=[]

    #constructor(taxi&c, location*dest)
    def __init__(self, c, dest):
        self.__car=c
        i=0
        while i<len(self.__car.passengers):
            if self.__car.passengers[i].dest==dest:
                self.__incoming.append(self.__car.passengers[i])
                del self.__car.passengers[i]
            else:
                i+=1
    
    # int size()
    def size(self):
        return len(self.__incoming)
    # bool empty()
    def empty(self):
        return len(self.__incoming)==0
    # taxi_value next()
    def next(self):
        assert (not self.empty()),  "error: cannot read incoming list" 

        #taxi value
        r=self.__incoming[0].value
        self.__car.passenger_pays(self.__incoming[0])
        del self.__incoming[0]
        return r
    # void update_taxi()
    def update_taxi(self):
        self.__car+=self.__incoming
        del self.__incoming


# void taxi_garage(location& here, incoming_list& incoming)
def taxi_garage(here, incoming):
    print("\nThe taxi is back in the garage. Program complete.")
    sys.exit(0)

# void post_office_arrive(location& here, incoming_list& incoming)
def post_office_arrive(here, incoming):
    while not incoming.empty():
        # taxi_value
        v = incoming.next()
        assert isinstance(v, str),  "error: post office cannot handle non-string values" 
        print(v)

# void post_office_create(location& here)
def post_office_create(here):
    if debuglevel >= 1:
        print("Waiting for input:")
    # string
    line=input()
    here.add_outgoing_passenger(line)

# void heisenbergs(location& here)
def heisenbergs(here):
    # double
    r = random.randrange(1<<32)
    here.add_outgoing_passenger(r)

# void starchild_numerology(location& here, const char* input)
def starchild_numerology(here, val):
    if debuglevel >= 1:
        print(val + " is waiting at Starchild Numerology")
    here.add_outgoing_passenger(int(val))

# void writers_depot(location& here, const char* input)
def writers_depot(here, val):
    # string
    ret = ""
    # bool
    slash = False
    for i in val:
        if i == "\\" and (not slash):
            slash = True
        elif slash:
            slash = False # ensure escaped characters in the middle of a string work properly
            if i == "\\":
                ret.append("\\")
            elif i == "n":
                ret.append("\n")
            elif i == "r":
                ret.append("\r")
            elif i == "t":
                ret.append("\t")
        else:
            ret.append(i)
    if debuglevel >= 1:
        print("\"" + ret + "\" is waiting at the Writer's Depot")
    here.add_outgoing_passenger(ret)

# void the_babelfishery(location& here, incoming_list& incoming)
def the_babelfishery(here, incoming):
    while not incoming.empty():
        # taxi_value
        v = incoming.next()
        if isinstance(v, str):
            here.add_outgoing_passenger(int(v))
        elif isinstance(v, int):
            here.add_outgoing_passenger(str(v))
        else:
            assert False,  "error: unknown type cannot be translated" 

# void charboil_grill(location& here, incoming_list& incoming)
def charboil_grill(here, incoming):
    while not incoming.empty():
        # taxi value
        v = incoming.next()
        assert (not isinstance(v, str)) or len(v) <= 1,  "error: charboil grill can only handle strings of length 1" 
        if isinstance(v, str):
            here.add_outgoing_passenger(ord(v))
        elif isinstance(v, int):
            here.add_outgoing_passenger(chr(v))
        else:
            assert False,  "error: unknown data type" 

# void addition_alley(location& here, incoming_list& incoming)
def addition_alley(here, incoming):
    if not incoming.empty():
        # double
        ret = 0
        while not incoming.empty():
            # taxi_value
            v = incoming.next()
            assert isinstance(v, int),  "error: requires a numerial value" 
            ret += v
        here.add_outgoing_passenger(ret)

# void multiplication_station(location& here, incoming_list& incoming)
def multiplication_station(here, incoming):
    if not incoming.empty():
        # double
        ret = 1
        while not incoming.empty():
            # taxi_value
            v = incoming.next()
            assert isinstance(v, int),  "error: requires a numerical value" 
            ret *= v
        here.add_outgoing_passenger(ret)

# void divide_and_conquer(location& here, incoming_list& incoming)
def divide_and_conquer(here, incoming):
    if not incoming.empty():
        # taxi_value
        v = incoming.next()
        assert isinstance(v, int),  "error: requires a numerical value" 
        # double
        ret = v
        while not incoming.empty():
            v = incoming.next()
            assert isinstance(v, int),  "error: requires a numerical value" 
            assert v != 0,  "error: divide by zero" 
            ret /= v
        here.add_outgoing_passenger(ret)

# void whats_the_difference(location& here, incoming_list& incoming)
def whats_the_difference(here, incoming):
    if not incoming.empty():
        # taxi_value
        v = incoming.next()
        assert isinstance(v, int),  "error: requires a numerical value" 
        # double
        ret = v
        while not incoming.empty():
            # taxi_value
            v = incoming.next()
            assert isinstance(v, int),  "error: requires a numerical value" 
            ret -= v
    here.add_outgoing_passenger(ret)

# void konkats(location& here, incoming_list& incoming)
def konkats(here, incoming):
    if not incoming.empty():
        # string
        ret = ""
        while not incoming.empty():
            # string
            v = incoming.next()
            assert isinstance(v, str),  "error: requires a string value" 
            ret += v
        here.add_outgoing_passenger(ret)

# void magic_eight(location& here, incoming_list& incoming)
def magic_eight(here, incoming):
    assert incoming.size() >= 2,  "error: requires two passengers" 
    #taxi_value
    v1 = incoming.next()
    v2 = incoming.next()
    assert isinstance(v1, int) and isinstance(v2, int),  "error: requires numerical number" 
    if v1 < v2:
        here.add_outgoing_passenger(v1)

# void collator_express(location& here, incoming_list incoming)
def collator_express(here, incoming):
    assert incoming.size() >= 2,  "error: requires two passengers" 
    #taxi_value
    v1=incoming.next()
    v2=incoming.next()
    assert isinstance(v1, str) and isinstance(v2, str),  "error: requires string values" 
    if v1 < v2:
        here.add_outgoing_passenger(v1)

# void the_underground(location& here, incoming_list incoming)
def the_underground(here, incoming):
    if not incoming.empty():
        # taxi_value
        v1 = incoming.next()
        assert isinstance(v1, int),  "error: requires a numerical number" 
        val = v1 - 1
        if val > 0:
            here.add_outgoing_passenger(val)

# void riverview_bridge(location& here, incoming_list& incoming)
def riverview_bridge(here, incoming):
    # this trashes values from existence. sleep with the fishies!
    while not incoming.empty():
        incoming.next()

# void auctioneer_school(location& here, incoming_list& imcoming)
def auctioneer_school(here, incoming):
    while not incoming.empty():
        # taxi_value
        v = incoming.next()
        assert isinstance(v, str),  "error: requires a string value" 
        here.add_outgoing_passenger(v.upper())

# void little_league_field(location& here, incoming_list& incoming)
def little_league_field(here, incoming):
    while not incoming.empty():
        # taxi_value
        v=incoming.next()
        assert isinstance(v, str),  "error: requires a string value" 
        here.add_outgoing_passenger(v.lower())

# void tomes_trims(location& here, incoming_list& incoming)
def tomes_trims(here, incoming):
    while not incoming.empty():
        # taxi_value
        v = incoming.next()
        assert isinstance(v, str),  "error: requires a string value" 
        here.add_outgoing_passenger(v.strip())

# void trunkers(location& here, incoming_list& incoming)
def trunkers(here, incoming):
    while not incoming.empty():
        # taxi_value
        v = incoming.next()
        assert isinstance(v, int),  "error: requires a numerical value" 
        here.add_outgoing_passenger(int(v))

# void rounders_pub(location& here, incoming_list& incoming)
def rounders_pub(here, incoming):
    while not incoming.empty():
        # taxi_value
        v=incoming.next()
        assert isinstance(v, int),  "error: requires a numerical value" 
        here.add_outgoing_passenger(round(v))

# void knots_leading(location& here, incoming_list& incoming)
def knots_leading(here, incoming):
    while not incoming.empty():
        # taxi_value
        v=incoming.next()
        assert isinstance(v, int),  "error: requires a numerical value" 
        here.add_outgoing_passenger(1 if v == 0 else 0)

# void cyclone(location& here, incoming_list& incoming)
def cyclone(here, incoming):
    while not incoming.empty():
        # taxi_value
        v = incoming.next()
        here.add_outgoing_passenger(v)
        here.add_outgoing_passenger(v)

# void chop_suey(location& here, incoming_list& incoming)
def chop_suey(here, incoming):
    while not incoming.empty():
        # taxi_value
        v = incoming.next()
        assert isinstance(v, str),  "error: requires a string value" 
        for i in range(len(v)):
            here.add_outgoing_passenger(v[i])

# void crime_lab(location& here, incoming_list& incoming)
def crime_lab(here, incoming):
    assert incoming.size() >= 2,  "error: requires at least 2 passengers" 
    # taxi_value
    v = incoming.next()
    assert isinstance(v, str),  "error: requires a string value" 
    while not incoming.empty():
        tmp = incoming.next()
        assert isinstance(tmp, str),  "error: requires a string value" 
        if v != tmp:
            return
    here.add_outgoing_passenger(v)

# void equals_corner(location& here, incoming_list& incoming)
def equals_corner(here, incoming):
    assert incoming.size() >= 2,  "error: requires at least 2 passengers" 
    # taxi_value
    v = incoming.next()
    assert isinstance(v, int),  "error: requires a numerical value" 
    while not incoming.empty():
        tmp = incoming.next()
        assert isinstance(tmp, int),  "error: requires a numerical value" 
        if v != tmp:
            return
    here.add_outgoing_passenger(v)

class road_map:
    __dest = {}
    __inter = {}
    __corner = {}

    def __init__(self):
        # setup the intersections
        self.__inter[1] = node(424, 145)
        self.__inter[2] = node(596, 138)
        self.__inter[3] = node(1120, 115)
        self.__inter[4] = node(1285, 112)
        self.__inter[5] = node(1370, 108)
        self.__inter[6] = node(1295, 84)
        self.__inter[7] = node(1094, 78)
        self.__inter[8] = node(355, 222)
        self.__inter[9] = node(215, 376)
        self.__inter[10] = node(482, 468)
        self.__inter[11] = node(379, 638)
        self.__inter[12] = node(246, 529)
        self.__inter[13] = node(291, 783)
        self.__inter[14] = node(209, 916)
        self.__inter[15] = node(501, 910)
        self.__inter[16] = node(50, 639)
        self.__inter[17] = node(739, 557)
        self.__inter[18] = node(702, 374)
        self.__inter[19] = node(875, 740)
        self.__inter[20] = node(991, 559)
        self.__inter[21] = node(1003, 825)
        self.__inter[22] = node(1241, 963)
        self.__inter[23] = node(1155, 709)
        self.__inter[24] = node(1382, 716)
        self.__inter[25] = node(1118, 683)
        self.__inter[26] = node(1132, 634)
        self.__inter[27] = node(1437, 617)
        self.__inter[28] = node(1171, 503)
        self.__inter[29] = node(1061, 407)
        self.__inter[30] = node(1061, 445)
        self.__inter[31] = node(1197, 414)
        self.__inter[32] = node(1227, 313)
        self.__inter[33] = node(1372, 314)
        self.__inter[34] = node(1160, 920)

        # setup the corners
        self.__corner[1] = node(510, 52)
        self.__corner[2] = node(108, 492)
        self.__corner[3] = node(682, 442)
        self.__corner[4] = node(818, 710)
        self.__corner[5] = node(1106, 724)
        self.__corner[6] = node(1181, 847)

        # configure destinations
        self.__dest["Taxi Garage"] = location()
        self.__dest["Taxi Garage"].arrival_function = taxi_garage
        self.__dest["Taxi Garage"].position(1246, 639)

        self.__dest["Post Office"] = location()
        self.__dest["Post Office"].arrival_function = post_office_arrive
        self.__dest["Post Office"].create_outgoing_passenger_function = post_office_create
        self.__dest["Post Office"].position(910, 695)

        self.__dest["heisenberg's"] = location()
        self.__dest["Heisenberg's"].create_outgoing_passenger_function = heisenbergs
        self.__dest["Heisenberg's"].position(1372, 237)

        self.__dest["Starchild Numerology"] = location()
        self.__dest["Starchild Numerology"].create_waiting_passenger_function = starchild_numerology
        self.__dest["Starchild Numerology"].position(278, 917)

        self.__dest["Writer's Depot"] = location()
        self.__dest["Writer's Depot"].create_waiting_passenger_function = writers_depot
        self.__dest["Writer's Depot"].position(164, 433)

        self.__dest["The Babelfishery"] = location()
        self.__dest["The Babelfishery"].arrival_function = the_babelfishery
        self.__dest["The Babelrishery"].position(949, 879)

        self.__dest["Charboil Grill"] = locaiton()
        self.__dest["Charboil Grill"].arrival_function = charboil_grill
        self.__dest["Charboil Grill"].position(152, 702)

        self.__dest["Addition Alley"] = location()
        self.__dest["Addition Alley"].arrival_function = addition_alley
        self.__dest["Addition Alley"].position(652, 211)

        self.__dest["Multiplication Station"] = location()
        self.__dest["Multiplication Station"].arrival_function = multiplication_station
        self.__dest["Multiplication Station"].position(1286, 888)

        self.__dest["Divide and Conquer"] = location()
        self.__dest["Divide and Conquer"].arrival_function = divide_and_conquier
        self.__dest["Divide and Conquer"].position(1117, 311)

        self.__dest["What's The Difference"] = location()
        self.__dest["What's The Difference"].arrival_function = whats_the_difference
        self.__dest["What's The Difference"].position(176, 153)

        self.__dest["KonKat's"] = location()
        self.__dest["KonKat's"].arrival_function = konkats
        self.__dest["KonKat's"].position(1262, 195)

        self.__dest["Magic Eight"] = location()
        self.__dest["Magic Eight"].arrival_function = magic_eight
        self.__dest["Magic Eight"].position(797, 666)

        self.__dest["Riverview Bridge"] = location()
        self.__dest["Riverview Bridge"].arrival_function = riverview_bridge
        self.__dest["Riverview Bridge"].passengers_pay = False
        self.__dest["Riverview Bridge"].position(888, 127)

        self.__dest["Sunny SKies Park"] = location()
        self.__dest["Sunny Skies Park"].buffer_order = B_FIFO
        self.__dest["Sunny Skies Park"].position(456, 412)

        self.__dest["Joyless Park"] = location()
        self.__dest["Joyless Park"].buffer_order = B_FIFO
        self.__dest["Joyless Park"].position(1361, 424)

        self.__dest["Narrow Path Park"] = location()
        self.__dest["Narrow Path Park"].buffer_order = B_LIFO
        self.__dest["Narrow Path Park"].position(1162, 78)

        self.__dest["Auctioneer School"] = location()
        self.__dest["Auctioneer School"].arrival_function = auctioneer_school
        self.__dest["Auctioneer School"].position(246, 856)

        self.__dest["Little League Field"] = location()
        self.__dest["Little League Field"].arrival_function = little_league_field
        self.__dest["Little League Field"].position(951, 711)

        self.__dest["Tom's Trims"] = location()
        self.__dest["Tom's Trims"].arrival_function = tomes_trims
        self.__dest["Tom's Trims"].position(951, 648)

        self.__dest["Trunkers"] = location()
        self.__dest["Trunkers"].arrival_function - trunkers
        self.__dest["Trunkers"].position(692, 543)

        self.__dest["Rounders Pub"] = location()
        self.__dest["Rounders Pub"].arrival_function = rounders_pub
        self.__dest["Rounders Pub"].position(1063, 482)

        self.__dest["Fueler Up"] = location()
        self.__dest["Fueler Up"].gas_price = 1.92
        self.__dest["Fueler Up"].max_passengers = 0
        self.__dest["Fueler Up"].position(1155, 557)

        self.__dest["Go More"] = location()
        self.__dest["Go More"].gas_price = 1.75
        self.__dest["Go More"].max_passengers = 0
        self.__dest["Go More"].position(258, 764)

        self.__dest["Zoom Zoom"] = location()
        self.__dest["Zoom Zoom"].gas_price = 1.45
        self.__dest["Zoom Zoom"].max_passengers = 0
        self.__dest["Zoom Zoom"].position(546, 52)

        self.__dest["Knots Landing"] = location()
        self.__dest["Knots Landing"].arrival_function = knots_leading
        self.__dest["Knots Landing"].position(1426, 314)

        self.__dest["Bird's Bench"] = location()
        self.__dest["Bird's Bench"].max_passengers = 1
        self.__dest["Bird's Bench"].position(197, 653)

        self.__dest["Rob's Rest"] = location()
        self.__dest["Rob's Rest"].max_passengers = 1
        self.__dest["Rob's Rest"].position(323, 473)

        self.__dest["Firemouth Grill"] = location()
        self.__dest["Firemouth Grill"].buffer_order = B_RANDOM
        self.__dest["Firemouth Grill"].position(770, 440)

        self.__dest["Cyclone"] = location()
        self.__dest["Cyclone"].arrival_function = cyclone
        self.__dest["Cyclone"].position(272, 314)
        
        self.__dest["Chop Suey"] = location()
        self.__dest["Chop Suey"].arrival_function =chop_suey
        self.__dest["Chop Suey"].locaiton(1374, 169)

        self.__dest["The Underground"] = location()
        self.__dest["The Underground"].arrival_function = the_underground
        self.__dest["The Underground"].position(1182, 462)

        self.__dest["Collator Express"] = location()
        self.__dest["Collator Express"].arrival_function = collator_express
        self.__dest["Collator Express"].position(424, 351)

        self.__dest["Crime Lab"] = location()
        self.__dest["Crime Lab"].arrival_function = crime_lab
        self.__dest["Crime Lab"].position(1031, 796)
        
        self.__dest["Equal's Corner"] = location()
        self.__dest["Equal's Corner"].arrival_function = equals_corner
        self.__dest["Equal's Corner"].position(210, 976)

        # link the nodes together forming the map
        node.street(9, self.__dest["Zoom Zoom"], self.__corner[1], self.__inter[1], self.__inter[8], self.__dest["Cyclone"], self.__inter[9], self.__dest["Writer's Depot"], self.__corner[2], self.__inter[16])
        node.street(7, self.__dest["What's The Difference"], self.__inter[1], self.__inter[2], self.__dest["Riverview Bridge"], self.__inter[3], self.__inter[4], self.__inter[5])
        node.street(2, self.__inter[7], self.__inter[3])
        node.street(3, self.__inter[7], self.__dest["Narrow Path Park"], self.__inter[6])
        node.street(2, self.__inter[2], self.__dest["Addition Alley"])
        node.street(4, self.__inter[9], self.__inter[10], self.__dest["Trunkers"], self.__inter[17])
        node.street(3, self.__dest["Rob's Rest"], self.__inter[12], self.__dest["Bird's Bench"])
        node.street(2, self.__inter[12], self.__inter[11])
        node.street(5, self.__inter[16], self.__dest["Charboil Grill"], self.__dest["Go More"], self.__inter[13], self.__inter[15])
        node.street(9, self.__inter[8], self.__dest["Collator Express"], self.__dest["Sunny Skies Park"], self.__inter[10], self.__inter[11], self.__inter[13], self.__dest["Auctioneer School"], self.__inter[14], self.__dest["Equal's Corner"])
        node.street(3, self.__inter[14], self.__dest["Starchild Numerology"], self.__inter[15])
        node.street(3, self.__inter[29], self.__inter[30], self.__dest["Rounders Pub"])
        node.street(3, self.__inter[29], self.__dest[31], self.__dest["Joyless Park"])
        node.street(2, self.__inter[28], self.__inter[27])
        node.street(4, self.__inter[27], self.__inter[24], self.__dest["Multiplicatoin Station"], self.__inter[22])
        node.street(3, self.__inter[23], self.__dest["Little League Field"], self.__inter[24])
        node.street(2, self.__inter[26], self.__dest["Taxi Garage"])
        node.street(4, self.__dest["Divide and Conquer"], self.__inter[32], self.__inter[33], self.__dest["Knots Landing"])
        node.street(9, self.__inter[18], self.__corner[3], self.__inter[17], self.__dest["Magic Eight"], self.__corner[4], self.__inter[19], self.__inter[21],  self.__inter[34], self.__inter[22])
        node.street(3, self.__inter[23], self.__corner[6], self.__inter[34])
        node.street(5, self.__inter[18], self.__dest["Firemouth Grill"], self.__inter[20], self.__inter[25], self.__inter[23])
        node.street(4, self.__inter[20], self.__dest["Tom's Trims"], self.__dest["Post Office"], self.__inter[19])
        node.street(14, self.__dest["The Babelfishery"], self.__inter[21], self.__dest["Crime Lab"], self.__corner[5], self.__inter[25], self.__inter[26], self.__dest["Fueler Up"], self.__inter[28], self.__dest["The Underground"], self.__inter[31], self.__inter[32], self.__dest["KonKat's"], self.__inter[4], self.__inter[6])
        node.street(4, self.__inter[5], self.__dest["Chop Suey"], self.__dest["Heisenberg's"], self.__inter[33])


    # location* get_location(const string& name)
    def get_location(self,name):
        if not name in self.__dest:
            return None
        return dest[name]

class code_t_:
    cmd = C_NONE
    loc = ""
    data = ""
    def __init__(self, c=None):
        if c is None:
            self.cmd = C_NONE
        else:
            self.cmd = c.cmd
            self.loc = c.loc
            self.data = c.data

class Program:
    __code_t = code_t_()
    __script = []
    __labels = {}
    def __init__(self, filename):
        with open(filename, "r") as file:
            s = ""
            for line in file:
                s += line
            self.parse(s)
    
    # void parse(string& in)
    def parse(self, s):
        # vector<string>
        tokens = []
        while len(s) > 0:
            print(len(s))
            # skip spaces
            s=s.strip()
            # check for labels
            # or check for narmol statements (which end in a period)
            if s[0]=="[":
                p=s.find("]")
                assert p != -1,  "parse error: incomplete label" 
                self.__labels[s[1:p]] = len(self.__script)
                t = s[p + 1:]
                s = t
            else:
                # bool
                was_quoted = False
                # string
                tok, s = self.get_token(s, was_quoted)
                if len(tok)==0:
                    break
                elif tok == "." and (not was_quoted):
                    self.compile(tokens)
                    assert len(tokens) == 0, "please insert clear."
                else:
                    tokens.append(tok)
        assert len(token) == 0,  "parse error: likely incomplete statement" 
    
    # void compile(vector<string>& in)
    def compile(self, i):
        # code_t
        c = C_NONE
        # is waiting at ...
        if len(i) >= 5 and i[1] == "is" and i[2] == "waiting" and i[3] == "at":
            c.cmd = C_WAITING
            c.data = i[0]
            # size_t
            s = 5 if i[4] == "the" else 4
            for j in range(len(i) - s):
                if j > 0:
                    c.loc += " "
                c.loc += i[j+s]
        elif len(i) >= 5 and i[0] == "Go" and i[1] == "to":
            c.cmd = C_GOTO
            # size_t
            s = 3 if i[2] == "the" else 2
            p = 0
            while p + s < len(i) and i[p + s] != ":":
                if p > 0:
                    c.loc += " "
                c.loc += i[p + s]
                p += 1
            p += 1 # skip the colon
            while p + s < len(i):
                # string
                string = i[p + s]
                # int
                n = re.search(r"^\d+$", string)
                if n:
                    c.data += str(n) + ":"
                elif len(string) > 0:
                    c.data += string.upper()[0]
        elif len(i) >= 6 and i[0] == "Pickup" and (i[1] == "a" or i[1] == "another") and i[2] == "passenger" and i[3] == "going" and i[4] == "to":
            c.cmd = C_PICKUP
            # size_t
            s = 6 if i [5] == "the" else 5
            for p in range(len(i) - s):
                if p > 0:
                    c.loc += " "
                c.loc += i[p + s]
        elif len(i) >= 4 and i[0] == "Switch" and i[1] == "to" and i[2] == "plan":
            c.cmd = C_SWITCH_IF if len(i) > 4 else C_SWITCH
            c.data = i[3]
        else:
            err = "parse error near:"
            for p in range(len(i)):
                err += " "
                err += i[p]
            assert False,  err 
        
        if debuglevel >= 2:
            print("debug:" + str(c.cmd) + " \"" + str(c.data) + "\" " + str(c.loc))
        self.__script.append(c)
        i.clear()
    
    # string get_token(string& in, bool& was_quoted)
    def get_token(self, i, was_quoted):
        # string
        r = ""
        # string::size_type
        p = 0
        was_quoted = False
        if len(i) > 0:
            # char
            c = i[0]
            if (c == "\"" or c == "'") and i[1:].find(c) != -1:
                p = i[1:].find(c)
                r = i[1:p]
                i = i[p + 2:]
                was_quoted = True
            elif c == "." or c == ":":
                r = c
                i = i[1:]
            else:
                r = i[:i.find(" \r\n\t:.")]
                i = i[len(r):]
        return r, i

    # void run(road_map& the_map)
    def run(self, the_map):
        # 1 mile: 264 pixels
        # Max gallons of gas: 20
        # Starting gallons: 20
        # miles per gallon: 18
        # starting credits: 0
        # fare in credits per mile: 0.07
        car = taxi(the_map.get_location("Taxi Garage"), 264, 20.0, 20.0, 18.0, 0.0, 0.07)

        # now let's do it!
        for i in range(len(self.__script)):
            # code_t*
            c = self.__script[i]
            # location*
            loc = the_map.get_location(c.loc)

            if debuglevel >= 2:
                print("debug2:" + str(c.cmd) + " \"" + str(c.data) + "\" " + str(c.loc) + " gas: " + str(self.car.gas) + " credits: " + str(self.car.credits) + " miles: " + str(self.car.miles_driven))
            
            if c.cmd == C_WAITING:
                assert not loc is None,  "error: missing location for waiting statement" 
                loc.waiting(str(c.data))
            elif c.cmd == C_PICKUP:
                assert not loc is None,  "error: missing destination in pickup statemet" 
                self.car.pickup_passenger(loc)
            elif c.cmd == C_GOTO:
                assert not loc is None,  "error: missing destination in go to statement" 
                assert len(c.data) > 0,  "error: invalid directions in go t0 statement" 
                # string
                path = c.data
                if path[0] == "N":
                    self.car.set_direction(D_NORTH)
                elif path[0] == "E":
                    self.car.set_direction(D_EAST)
                elif path[0] == "S":
                    self.car.set_direction(D_SOUTH)
                elif path[0] == "W":
                    self.car.set_direction(D_WEST)
                else:
                    assert False,  "error: invalid cardinal direction" 
                
                del path[0]
                while len(path) > 0:
                    # int
                    turns = int(path)
                    if turns < 1:
                        break
                    # string::size_type
                    p = path.find(":")
                    if p == -1 or p + 1 == len(path):
                        break
                    path = path[0:p]
                    # rel_dir_t
                    d = D_LEFT if path[0] == 'L' else D_RIGHT
                    del path[0]
                    self.car.take_xth_turn(turns, d)
                assert len(path) == 0,  "error: invarid directions in go to statement" 
                if debuglevel >= 1:
                    print("Driving to " + c.loc)
                self.car.drive_to(c.loc)
            elif c.cmd == C_SWITCH:
                assert len(c.data) > 0,  "error: missing label in switch command" 
                assert self.__labels.count(c.data) > 0,  "error: no such label" 
                j = self.__labels[c.data] - 1
                if debuglevel >= 1:
                    print("Switching to plan [" + str(c.data) + "]")
            elif c.cmd == C_SWITCH_IF:
                assert len(c.data) > 0,  "error missing label in switch_if command" 
                assert self.__labels.count(c.data) > 0,  "no such label" 
                assert not self.car.current_location is None,  "cannot switch, not at all passenger destination" 
                if not self.car.current_location.outgoing_passengers() is None:
                    j = self.__labels[c.data] - 1
                    if debuglevel >= 1:
                        print("Switching to plan [" + str(c.data) + "] since nobody is waiting")
                else:
                    if debuglevel >= 1:
                        print("Not switching to plan [" + str(c.data) + "] because someone is waiting")

if __name__ == "__main__":
    args = sys.argv
    assert len(args) > 1,  "usage: " + str(args[0]) + " script.txt [debuglevel]\n" 
    print("Welcome to Taxi")
    print("Let the journey begin...\n")

    # road_map
    the_map = None
    if len(args) == 3:
        debuglevel = int(args[2])
    
    f = args[1]
    pgm = Program(f)
    pgm.run(the_map)
