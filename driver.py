import math
import random
import sys
import re
import time
import pygame
from pygame.locals import *

#set nesw_t
D_NONE = [0, 0]
D_WEST = [-1, 0]
D_NORTH = [0, -1]
D_EAST = [1, 0]
D_SOUTH = [0, 1]

def mul(a,k):
    return list(map(lambda x:k*x, a))


font = pygame.font.Font(None, 30)

#set rel_dir_t
def D_LEFT(d):
    return [d[1], -d[0]]
def D_RIGHT(d):
    return [-d[1], d[0]]

# change to counting str
def countingStr(n):
    if (n//10)%10==1:
        return str(n)+"th"
    if n%10 == 1:
        return str(n)+"st"
    elif n%10 == 2:
        return str(n)+"nd"
    elif n%10 == 3:
        return str(n)+"rd"
    else:
        return str(n)+"th"

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

loclist = {}
the_map = []
road = []
car = None
height = 0
width = 0
ans = ""
# コード生成系統
code = []
tmpcode = ""
usecode = ""
leftcnt = 0
rightcnt = 0
codereader = 0
codetimer = None

class location:
    x = 0
    y = 0
    name = ""
    description = ""
    outgoing = []
    buffer_order = None
    max_passengers = 0
    arrival_function = None
    create_outgoing_passenger_function = None
    create_waiting_passenger_function = None
    passengers_pay = False
    gas_price = 0.0
    is_wall = False

    def __init__(self, x_, y_, name_):
        self.x, self.y = x_, y_
        self.name = name_
        self.description = ""
        self.outgoing = []
        self.buffer_order = B_FIFO
        self.max_passengers = -1  # infinite
        self.arrival_function = None
        self.create_outgoing_passenger_function = None
        self.create_waiting_passenger_function = None
        self.passengers_pay = True
        self.gas_price = 0.0
        self.is_wall == self.name == "Wall"

# void taxi_garage(location& here, incoming_list& incoming)
def taxi_garage(car):
    global code
    print("\nThe taxi is back in the garage. Program complete.")
    if code[:len(code)//2]==code[len(code)//2:]:
        code=code[:len(code)//2]
    print(code)
    car.ingarage = True

# void post_office_arrive(location& here, incoming_list& incoming)
def post_office_arrive(here, incoming):
    global ans
    for v in incoming:
        # assert isinstance(v, str),  "error: post office cannot handle non-string values"
        ans += str(v) + "\n"
        print(v)
    del incoming

# void post_office_create(location& here)
def post_office_create(here):
    if debuglevel >= 1:
        print("Waiting for input:")
    # string
    line = input()
    here.outgoing.append(line)

# void starchild_numerology(location& here, const char* input)
def starchild_numerology(here, val):
    if debuglevel >= 1:
        print(val + " is waiting at Starchild Numerology")
    here.outgoing.append(int(val))

# void addition_alley(location& here, incoming_list& incoming)
def addition_alley(here, incoming):
    if len(incoming) > 0:
        # double
        ret = 0
        for i in incoming:
            # taxi_value
            assert isinstance(i, int),  "error: requires a numerial value"
            ret += i
        here.outgoing.append(ret)
        del incoming

# void multiplication_station(location& here, incoming_list& incoming)
def multiplication_station(here, incoming):
    if len(incoming) > 0:
        # double
        ret = 1
        for v in incoming:
            # taxi value
            assert isinstance(v, int),  "error: requires a numerical value"
            ret *= v
        here.outgoing.append(ret)
        del incoming

# void divide_and_conquer(location& here, incoming_list& incoming)
def divide_and_conquer(here, incoming):
    if len(incoming) > 0:
        # double
        ret = incoming[0]
        assert isinstance(ret, int),  "error: requires a numerical value"
        for i in range(1,len(incoming)):
            v = incoming[i]
            assert isinstance(v, int),  "error: requires a numerical value"
            if v == 0:
                # You're fired!!
                global ans
                ans = ""
                car.ingarage = True
            ret /= v
        here.outgoing.append(ret)
        del incoming

# void whats_the_difference(location& here, incoming_list& incoming)
def whats_the_difference(here, incoming):
    if len(incoming)>0:
        # double
        assert isinstance(v, int),  "error: requires a numerical value"
        ret = incoming[0]
        for i in range(1,len(incoming)):
            # taxi_value
            v = incoming[i]
            assert isinstance(v, int),  "error: requires a numerical value"
            ret -= v
        here.outgoing.append(ret)
        del incoming

# void cyclone(location& here, incoming_list& incoming)
def cyclone(here, incoming):
    for i in incoming:
        here.outgoing.append(i)
        here.outgoing.append(i)
    del incoming

# void riverview_bridge(location& here, incoming_list& incoming)
def riverview_bridge(here, incoming):
    # this trashes values from existence. sleep with the fishies!
    del incoming

class taxi:
    x, y = 0, 0
    tx, ty = 0, 0
    v = 10
    vx, vy = 0, 0
    passengers = []
    passengers_destination = []
    passengers_pay = []
    selector = []
    willpickup = False
    ingarage = False
    pixels_per_mile = 0.0
    max_gas = 0.0
    gas = 0.0
    gas_usage = 0.0
    credits = 0.0
    fare = 0.0
    miles_driven = 0.0
    image=[]
    meter_img=[]
    direction = 0

    def __init__(self, start, ppm, max_gas_, gas_, gas_usage_, credits_, fare_):
        self.x, self.y = self.tx, self.ty = start.x, start.y
        self.vx = self.vy = 0
        self.passengers = []
        self.passengers_destination = []
        self.passengers_pay = []
        self.selector = []
        self.willpickup = False
        self.ingarage = False
        self.pixels_per_mile = ppm
        self.max_gas = max_gas_
        self.gas = gas_
        self.gas_usage = gas_usage_
        self.credits = credits_
        self.fare = fare_
        self.miles_driven = 0.0
        self.image = [pygame.image.load("img/taxi_east.png"), pygame.image.load("img/taxi_south.png"), pygame.image.load("img/taxi_west.png"), pygame.image.load("img/taxi_north.png")]
        self.meter_img = [pygame.image.load("img/meter.png"), pygame.image.load("img/meter-red.png")]
        self.image[0] = pygame.transform.scale(self.image[0], (70, 40))
        self.image[1] = pygame.transform.scale(self.image[1], (45, 60))
        self.image[2] = pygame.transform.scale(self.image[2], (70, 40))
        self.image[3] = pygame.transform.scale(self.image[3], (45, 60))
        self.direction = -4
    
    def move(self, d):
        global the_map, width, height, code, tmpcode, leftcnt, rightcnt
        if self.vx != 0 or self.vy != 0:
            return
        to = [self.x + d[0], self.y + d[1]]
        if to[0]<0 or width<=to[0] or to[1]<0 or height<=to[1]:
            return
        if not the_map[to[0]][to[1]] is None and the_map[to[0]][to[1]].name == "Wall":
            return
        k = 1
        while True:
            to = [to[0] + d[0], to[1] + d[1]]
            if to[0]<0 or width<=to[0] or to[1]<0 or height<=to[1]:
                return
            if not the_map[to[0]][to[1]] is None:
                break
        self.tx, self.ty = to
        self.vx, self.vy = d
        self.selector = []
        self.willpickup = False
        if d == mul(D_EAST, self.v):
            if self.direction < 0 or self.direction == 2:
                if tmpcode != "":
                    if tmpcode[0].islower():
                        code.append("Go to "+the_map[self.x][self.y].name+": "+(tmpcode[:-1] if tmpcode[-1]=="," else tmpcode)+".")
                    else:
                        code.append(tmpcode)
                tmpcode = "east"
                leftcnt = 0
                rightcnt = 0
            elif self.direction == 0:
                if the_map[self.x][self.y+1] is None or the_map[self.x][self.y+1].name!="Wall":
                    rightcnt+=1
                if the_map[self.x][self.y-1] is None or the_map[self.x][self.y-1].name!="Wall":
                    leftcnt+=1
            elif self.direction == 1:
                tmpcode += " "+countingStr(leftcnt+1)+" left,"
                leftcnt=0
                rightcnt=0
            elif self.direction == 3:
                tmpcode += " "+countingStr(rightcnt+1)+" right,"
                leftcnt = 0
                rightcnt = 0
            self.direction = 0
        elif d == mul(D_SOUTH, self.v):
            if self.direction < 0 or self.direction == 3:
                if tmpcode != "":
                    if tmpcode[0].islower():
                        code.append("Go to "+the_map[self.x][self.y].name+": "+(tmpcode[:-1] if tmpcode[-1]=="," else tmpcode)+".")
                    else:
                        code.append(tmpcode)
                tmpcode = "south"
                leftcnt = 0
                rightcnt = 0
            elif self.direction == 1:
                if the_map[self.x+1][self.y] is None or the_map[self.x+1][self.y].name!="Wall":
                    leftcnt += 1
                if the_map[self.x-1][self.y] is None or the_map[self.x-1][self.y].name!="Wall":
                    rightcnt += 1
            elif self.direction == 0:
                tmpcode += " "+countingStr(rightcnt+1)+" right,"
                leftcnt = 0
                rightcnt = 0
            elif self.direction == 2:
                tmpcode += " "+countingStr(leftcnt+1)+" left,"
                leftcnt = 0
                rightcnt = 0
            self.direction = 1
        elif d == mul(D_WEST, self.v):
            if self.direction <= 0:
                if tmpcode != "":
                    if tmpcode[0].islower():
                        code.append(
                            "Go to " + the_map[self.x][self.y].name + ": " + (tmpcode[:-1] if tmpcode[-1] == "," else tmpcode) + ".")
                    else:
                        code.append(tmpcode)
                tmpcode = "west"
                leftcnt = 0
                rightcnt = 0
            elif self.direction == 2:
                if the_map[self.x][self.y + 1] is None or the_map[self.x][self.y + 1].name != "Wall":
                    leftcnt += 1
                if the_map[self.x][self.y - 1] is None or the_map[self.x][self.y - 1].name != "Wall":
                    rightcnt += 1
            elif self.direction == 1:
                tmpcode += " " + countingStr(rightcnt+1) + " right,"
                leftcnt = 0
                rightcnt = 0
            elif self.direction == 3:
                tmpcode += " " + countingStr(leftcnt+1) + " left,"
                leftcnt = 0
                rightcnt = 0
            self.direction = 2
        elif d == mul(D_NORTH, self.v):
            if self.direction < 0 or self.direction == 1:
                if tmpcode != "":
                    if tmpcode[0].islower():
                        code.append(
                            "Go to " + the_map[self.x][self.y].name + ": " + (tmpcode[:-1] if tmpcode[-1]=="," else tmpcode) + ".")
                    else:
                        code.append(tmpcode)
                tmpcode = "north"
                leftcnt = 0
                rightcnt = 0
            elif self.direction == 3:
                if the_map[self.x - 1][self.y] is None or the_map[self.x - 1][self.y].name != "Wall":
                    leftcnt += 1
                if the_map[self.x + 1][self.y] is None or the_map[self.x + 1][self.y].name != "Wall":
                    rightcnt += 1
            elif self.direction == 2:
                tmpcode += " " + countingStr(rightcnt+1) + " right,"
                leftcnt = 0
                rightcnt = 0
            elif self.direction == 0:
                tmpcode += " " + countingStr(leftcnt+1) + " left,"
                leftcnt = 0
                rightcnt = 0
            self.direction = 3
    
    def update(self):
        global the_map, loclist, code, tmpcode, leftcnt, rightcnt
        self.x += self.vx
        self.y += self.vy
        d = (self.vx*self.vx+self.vy*self.vy)**0.5/self.pixels_per_mile
        self.gas -= d/self.gas_usage
        self.miles_driven += d
        if self.gas < 0:
            ans = "gas is empty."
            self.ingarage = True
            return
        for i in range(len(self.passengers_pay)):
            self.passengers_pay[i] += self.fare * d

        if self.x == self.tx and self.y == self.ty and (self.vx != 0 or self.vy != 0):
            if (self.vx != 0 or self.vy != 0) and the_map[self.x][self.y] == loclist["Taxi Garage"]:
                if tmpcode != "":
                    if tmpcode[0].islower:
                        code.append("Go to Taxi Garage: "+(tmpcode[:-1] if tmpcode[-1]=="," else tmpcode)+".")
                    else:
                        code.append(tmpcode)
                    tmpcode = ""
                loclist["Taxi Garage"].arrival_function(car)
            #客を降ろす
            if not the_map[self.x][self.y] is None:
                #ガソリンスタンド
                if the_map[self.x][self.y].gas_price > 0 and car.credits > 0:
                    getgas = min(self.credits / the_map[self.x][self.y].gas_price, self.max_gas - self.gas)
                    self.credits -= getgas
                    self.gas += getgas
                    code.append("Go to "+the_map[self.x][self.y].name+": "+(tmpcode[:-1] if tmpcode[-1]=="," else tmpcode)+".")
                    tmpcode = ""
                    leftcnt = 0
                    rightcnt = 0
                    if car.direction >= 0:
                        car.direction -= 4
                else:
                    for i in range(len(self.passengers)):
                        if [self.x,self.y]==self.passengers_destination[i]:
                            self.selector.append(i)
                    if len(self.selector)>0:
                        self.getout_passenger()
            self.vx = self.vy = 0
    
    def pickup_passenger(self,x_,y_):
        global the_map, code, tmpcode, leftcnt, rightcnt
        if the_map[self.x][self.y] is None or len(the_map[self.x][self.y].outgoing) == 0:
            return
        self.passengers.append(the_map[self.x][self.y].outgoing[0])
        self.passengers_destination.append([x_,y_])
        self.passengers_pay.append(0.0)
        del the_map[self.x][self.y].outgoing[0]
        self.willpickup=False
        if tmpcode != "":
            if tmpcode[0].islower:
                code.append("Go to " + the_map[self.x][self.y].name + ": " + (
                    tmpcode[:-1] if tmpcode[-1] == "," else tmpcode) + ".")
            else:
                code.append(tmpcode)
            tmpcode = ""
            leftcnt = 0
            rightcnt = 0
        code.append("Pickup a passenger going to "+the_map[x_][y_].name+".")
        if self.direction >= 0:
            self.direction -= 4
    
    def getout_passenger(self):
        global the_map, tmpcode, code, leftcnt, rightcnt
        if len(self.selector) == 0 or the_map[self.x][self.y] is None or the_map[self.x][self.y].arrival_function is None:
            return
        send = []
        self.selector.sort()
        for i in range(len(self.selector)):
            send.append(self.passengers[self.selector[i]])
        for i in reversed(range(len(self.selector))):
            self.credits += self.passengers_pay[self.selector[i]]
            del self.passengers[self.selector[i]]
            del self.passengers_pay[self.selector[i]]
            del self.passengers_destination[self.selector[i]]
        the_map[self.x][self.y].arrival_function(the_map[self.x][self.y],send)
        self.selector = []
        # tmpcodeの最後の「,」を「.」に置換するのを忘れずに
        code.append("Go to " + the_map[self.x][self.y].name + ": " + (tmpcode[:-1] if tmpcode[-1]=="," else tmpcode) + ".")
        tmpcode = ""
        if self.direction >= 0:
            self.direction -= 4


def setup(car_, loclist_, the_map_, road_,  h_, w_, test_mode):
    global car, loclist, the_map, road, height, width, ans, code, tmpcode, leftcnt, rightcnt, codetimer, codereader
    ans = ""
    car = car_
    loclist = loclist_
    the_map = the_map_
    road = road_
    height = h_
    width = w_
    if not test_mode:
        code = []
    tmpcode = ""
    leftcnt = 0
    rightcnt = 0
    codereader = 0
    codetimer = None

def get_score():
    global code
    return len(code), car.miles_driven

def gaming(screen):
    global car, loclist, the_map, height, width, code
    if len(code)>0:
        text = font.render(code[-1],True,(0,0,0))
        screen.blit(text, [400,height-40])
    x,y = pygame.mouse.get_pos()
    for i in road:
        pygame.draw.line(screen, (200,50,0), i[0], i[1])
    for key,val in loclist.items():
        if key == "Wall" or key == "Road":
            continue
        else:
            if val.x - 20 < x < val.x + 20 and val.y - 20 < y < val.y + 20:
                pygame.draw.rect(screen, (200,0,0), Rect(val.x-10,val.y-10,20,20))
                text = font.render(key, True, (200, 0, 0))
                screen.blit(text, [val.x-text.get_width()/2,val.y+10])
                text = font.render(key + ": " + val.description, True, (0,0,0))
                screen.blit(text, [250, 20])
            else:
                pygame.draw.rect(screen, (0,80,0), Rect(val.x-10,val.y-10,20,20))
                text = font.render(key, True, (0, 80, 0))
                screen.blit(text, [val.x-text.get_width()/2,val.y+10])
        
    car.update()
    d=car.direction if car.direction>=0 else 4+car.direction
    screen.blit(car.image[d], [car.x - car.image[d].get_width() / 2, car.y - car.image[d].get_height() / 2])

    arg = math.pi*3/4-math.pi/2*car.gas/car.max_gas
    if car.gas > car.max_gas*0.2:
        screen.blit(car.meter_img[0], [210, height - 150])
        pygame.draw.polygon(screen, [0, 0, 0], [[269, height-77], [289, height-77],[279-34*math.cos(arg), height-77-34*math.sin(arg)]], 0)
    else:
        screen.blit(car.meter_img[1], [210, height - 150])
        pygame.draw.polygon(screen, [255, 0, 0], [[269, height-77], [289, height-77],[279-34*math.cos(arg), height-77-34*math.sin(arg)]], 0)

    # 0-200にpassengersを表示
    pygame.draw.rect(screen, (100, 100, 100), Rect(0, 0, 200, height))
    for i in range(len(car.passengers)):
        pygame.draw.rect(screen, (0,200,0), Rect(10,200*i+10,180,180))
        text = font.render(str(car.passengers[i])[:10], True, (255, 255, 255))
        screen.blit(text, [20, 200*i+85])
    #-200-にoutgoingを表示
    pygame.draw.rect(screen, (100, 100, 100), Rect(width - 200, 0, 200, height))
    if not the_map[car.x][car.y] is None and len(the_map[car.x][car.y].outgoing) > 0:
        if car.willpickup==True:
            pygame.draw.rect(screen, (0, 200, 0),Rect(width - 190, 10, 180, 180))
        else:
            pygame.draw.rect(screen, (200, 0, 0), Rect(width - 190, 10, 180, 180))
        text = font.render(str(the_map[car.x][car.y].outgoing[0]), True, (255, 255, 255))
        screen.blit(text,[width - 180, 85])
        for i in range(1,min(len(the_map[car.x][car.y].outgoing),3)):
            pygame.draw.rect(screen, (200,0,0), Rect(width - 190, 200*i+10, 180,180))
            text = font.render(str(the_map[car.x][car.y].outgoing[i]), True, (255,255,255))
            screen.blit(text,[width - 180, 200 * i + 85])
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        #マウスクリック
        elif event.type == MOUSEBUTTONDOWN and event.button == 1:
            x,y = event.pos
            if width - 200 < x:
                if not the_map[car.x][car.y] is None and len(the_map[car.x][car.y].outgoing)>0:
                    car.willpickup^=True
            elif car.willpickup:
                for key,val in loclist.items():
                    if val.arrival_function is None:
                        continue
                    if val.x-20<x<val.x+20 and val.y-20<y<val.y+20:
                        car.pickup_passenger(val.x,val.y)
                        break
        #キー
        elif event.type == KEYDOWN:
            if event.key == K_LEFT:
                car.move(mul(D_WEST, car.v))
            elif event.key == K_RIGHT:
                car.move(mul(D_EAST, car.v))
            elif event.key == K_UP:
                car.move(mul(D_NORTH, car.v))
            elif event.key == K_DOWN:
                car.move(mul(D_SOUTH, car.v))
            elif event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
    #if car.ingarage:
    #    print("\n".join(code))
    return car.ingarage, ans

def testing(screen):
    global car, loclist, the_map, height, width, code, usecode, codereader, codetimer
    text = font.render("Testing...", True, (0,0,0))
    screen.blit(text, [(width-text.get_width())/2,20])
    if codereader > 0:
        text = font.render(code[codereader-1], True, (200,0,0))
        screen.blit(text, [400, height-40])
    for i in road:
        pygame.draw.line(screen, (200, 50, 0), i[0], i[1])
    for key,val in loclist.items():
        if key == "Wall" or key == "Road":
            continue
        else:
            pygame.draw.rect(screen, (0,80,0), Rect(val.x-10,val.y-10,20,20))
            text = font.render(key, True, (0, 80, 0))
            screen.blit(text, [val.x-text.get_width()/2,val.y+10])
        
    car.update()
    d=car.direction if car.direction>=0 else 4+car.direction
    screen.blit(car.image[d], [car.x - car.image[d].get_width() / 2, car.y - car.image[d].get_height() / 2])

    arg = math.pi*3/4-math.pi/2*car.gas/car.max_gas
    if car.gas > car.max_gas*0.2:
        screen.blit(car.meter_img[0], [210, height - 150])
        pygame.draw.polygon(screen, [0, 0, 0], [[269, height-77], [289, height-77],[279-34*math.cos(arg), height-77-34*math.sin(arg)]], 0)
    else:
        screen.blit(car.meter_img[1], [210, height - 150])
        pygame.draw.polygon(screen, [255, 0, 0], [[269, height-77], [289, height-77],[279-34*math.cos(arg), height-77-34*math.sin(arg)]], 0)

    # 0-200にpassengersを表示
    pygame.draw.rect(screen, (100, 100, 100), Rect(0, 0, 200, height))
    for i in range(len(car.passengers)):
        pygame.draw.rect(screen, (0,200,0), Rect(10,200*i+10,180,180))
        text = font.render(str(car.passengers[i])[:10], True, (255, 255, 255))
        screen.blit(text, [20, 200*i+85])
    #-200-にoutgoingを表示
    pygame.draw.rect(screen, (100, 100, 100), Rect(width - 200, 0, 200, height))
    if not the_map[car.x][car.y] is None and len(the_map[car.x][car.y].outgoing) > 0:
        if car.willpickup==True:
            pygame.draw.rect(screen, (0, 200, 0),Rect(width - 190, 10, 180, 180))
        else:
            pygame.draw.rect(screen, (200, 0, 0), Rect(width - 190, 10, 180, 180))
        text = font.render(str(the_map[car.x][car.y].outgoing[0]), True, (255, 255, 255))
        screen.blit(text,[width - 180, 85])
        for i in range(1,min(len(the_map[car.x][car.y].outgoing),3)):
            pygame.draw.rect(screen, (200,0,0), Rect(width - 190, 200*i+10, 180,180))
            text = font.render(str(the_map[car.x][car.y].outgoing[i]), True, (255,255,255))
            screen.blit(text,[width - 180, 200 * i + 85])
    
    if usecode == "":
        usecode = code[codereader].split()
        codereader += 1
    else:
        if codetimer is None:
            if usecode[0]=="Pickup":
                car.pickup_passenger(loclist[" ".join(usecode[5:])[:-1]].x,loclist[" ".join(usecode[5:])[:-1]].y)
                codetimer = time.time()
            elif usecode[0]=="Go":
                if not the_map[car.x][car.y] is None:
                    idx = 0
                    while idx<len(usecode) and usecode[idx][-1]!=":":
                        idx+=1
                    if idx+1 >= len(usecode):
                        if car.direction%4==0:
                            car.move(mul(D_EAST, car.v))
                        elif car.direction%4==1:
                            car.move(mul(D_SOUTH, car.v))
                        elif car.direction%4==2:
                            car.move(mul(D_WEST, car.v))
                        elif car.direction%4==3:
                            car.move(mul(D_NORTH, car.v))
                        codetimer = time.time()
                    elif usecode[idx+1][0] in "123456789":
                        num = int(usecode[idx+1][:-2])
                        if usecode[idx+2][:-1]=="left":
                            if leftcnt+1 < num:
                                if car.direction%4==0:
                                    car.move(mul(D_EAST, car.v))
                                elif car.direction%4==1:
                                    car.move(mul(D_SOUTH, car.v))
                                elif car.direction%4==2:
                                    car.move(mul(D_WEST, car.v))
                                elif car.direction%4==3:
                                    car.move(mul(D_NORTH, car.v))
                                codetimer=time.time()
                            else:
                                if car.direction%4 == 0 and (the_map[car.x][car.y-1] is None or the_map[car.x][car.y-1].name!="Wall"):
                                    car.move(mul(D_NORTH, car.v))
                                    del usecode[idx+1:idx+3]
                                    codetimer=time.time()
                                elif car.direction%4 == 1 and (the_map[car.x+1][car.y] is None or the_map[car.x+1][car.y].name!="Wall"):
                                    car.move(mul(D_EAST, car.v))
                                    del usecode[idx+1:idx+3]
                                    codetimer=time.time()
                                elif car.direction%4 == 2 and (the_map[car.x][car.y+1] is None or the_map[car.x][car.y+1].name!="Wall"):
                                    car.move(mul(D_SOUTH, car.v))
                                    del usecode[idx+1:idx+3]
                                    codetimer = time.time()
                                elif car.direction%4 == 3 and (the_map[car.x-1][car.y] is None or the_map[car.x-1][car.y].name!="Wall"):
                                    car.move(mul(D_WEST, car.v))
                                    del usecode[idx+1:idx+3]
                                    codetimer = time.time()
                        elif usecode[idx + 2][:-1] == "right":
                            if rightcnt + 1 < num:
                                if car.direction%4==0:
                                    car.move(mul(D_EAST, car.v))
                                elif car.direction%4==1:
                                    car.move(mul(D_SOUTH, car.v))
                                elif car.direction%4==2:
                                    car.move(mul(D_WEST, car.v))
                                elif car.direction%4==3:
                                    car.move(mul(D_NORTH, car.v))
                                codetimer = time.time()
                            else:
                                if car.direction%4 == 0 and (the_map[car.x][car.y + 1] is None or the_map[car.x][car.y + 1].name != "Wall"):
                                    car.move(mul(D_SOUTH, car.v))
                                    del usecode[idx+1:idx+3]
                                    codetimer = time.time()
                                elif car.direction%4 == 1 and (the_map[car.x - 1][car.y] is None or the_map[car.x - 1][car.y].name != "Wall"):
                                    car.move(mul(D_WEST, car.v))
                                    del usecode[idx+1:idx+3]
                                    codetimer = time.time()
                                elif car.direction%4 == 2 and (the_map[car.x][car.y - 1] is None or the_map[car.x][car.y - 1].name != "Wall"):
                                    car.move(mul(D_NORTH, car.v))
                                    del usecode[idx+1:idx+3]
                                    codetimer = time.time()
                                elif car.direction%4 == 3 and (the_map[car.x + 1][car.y] is None or the_map[car.x + 1][car.y].name != "Wall"):
                                    car.move(mul(D_EAST, car.v))
                                    del usecode[idx+1:idx+3]
                                    codetimer = time.time()
                    elif usecode[idx+1][:4]=="east":
                        car.move(mul(D_EAST,car.v))
                        del usecode[idx+1]
                        codetimer = time.time()
                    elif usecode[idx+1][:5]=="south":
                        car.move(mul(D_SOUTH,car.v))
                        del usecode[idx+1]
                        codetimer = time.time()
                    elif usecode[idx+1][:4]=="west":
                        car.move(mul(D_WEST,car.v))
                        del usecode[idx+1]
                        codetimer = time.time()
                    elif usecode[idx+1][:5]=="north":
                        car.move(mul(D_NORTH,car.v))
                        del usecode[idx+1]
                        codetimer = time.time()
        elif time.time()-codetimer > 0.5:
            if usecode[0]=="Pickup":
                usecode=""
                codetimer = None
            elif usecode[0]=="Go":
                idx = 0
                while idx<len(usecode) and usecode[idx][-1]!=":":
                    idx+=1
                if not the_map[car.x][car.y] is None:
                    codetimer = None
                    if the_map[car.x][car.y].name == " ".join(usecode[2:idx+1])[:-1]:
                        usecode = ""
    
    for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
    return car.ingarage, ans
