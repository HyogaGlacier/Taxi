#-*- coding:utf-8 -*-
import pygame
from pygame.locals import *
import sys
import os

# データベース初期設定
import mysql.connector
conn = mysql.connector.connect(user='root', password='', host='localhost', database='taxi')
cur=conn.cursor()
txtrank = []
runrank = []

# ゲームの状態遷移
G_TITLE = 0
G_SELECT_MAP = 1
G_SELECT_PROBLEM = 2
G_GAME = 3
G_TEST = 4
G_NAME = 5
G_RANKING = 6
G_FIRED = 7

mode = 0
w=1280
h=720

SCREEN_SIZE = (w, h)

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
pygame.display.set_caption("Taxi")
font50 = pygame.font.Font(None, 50)
font80 = pygame.font.Font(None, 80)
font100 = pygame.font.Font(None, 100)
font160 = pygame.font.Font(None, 160)
from driver import *
import writer

maplist = os.listdir("map")
mapstr = ""
for i in reversed(range(len(maplist))):
    if maplist[i][:2] == "__":
        del maplist[i]
    else:
        maplist[i] = maplist[i][:-3]
maplist.append("back")
mapselector = 0

setupMapfunction = None

problemlist = os.listdir("problem")
problemstr = ""
for i in reversed(range(len(problemlist))):
    if problemlist[i][:2] == "__":
        del problemlist[i]
    else:
        problemlist[i] = problemlist[i][:-3]
problemlist.append("back")
problemselector = 0

titlelogo = pygame.image.load("img/logo.png")
fired = pygame.image.load("img/gameover.png")
textinput = writer.TextInput()
clock = pygame.time.Clock()

while True:
    if mode == G_TITLE:
        if "map.easy" in sys.modules:
            sys.modules.pop("map.easy")
        screen.fill((255, 255, 255))
        screen.blit(titlelogo, [(w - titlelogo.get_width()) / 2.0, (h - titlelogo.get_height()) / 2.0])
        x, y = pygame.mouse.get_pos()
        text = font80.render("start", True, (255, 255, 255))
        if (w - text.get_width()) / 2 - 20 < x < (w + text.get_width()) / 2 + 20 and h * 3 / 4 - 10 < y < h * 3 / 4 + text.get_height() + 10:
            text = font80.render("start", True, (0, 0, 0))
            pygame.draw.rect(screen, (255, 255, 255), Rect((w - text.get_width()) / 2 - 20, h * 3 / 4 - 10, text.get_width() + 40, text.get_height() + 20))
        else:
            pygame.draw.rect(screen, (0, 0, 0), Rect((w - text.get_width()) / 2 - 20, h * 3 / 4 - 10, text.get_width() + 40, text.get_height() + 20))
        screen.blit(text, [(w - text.get_width()) / 2, h * 3 / 4])
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                cur.close
                conn.close
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                if (w - text.get_width()) / 2 - 20 < x < (w + text.get_width()) / 2 + 20 and h * 3 / 4 - 10 < y < h * 3 / 4 + text.get_height() + 10:
                    mode = G_SELECT_MAP
            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    mode = G_SELECT_MAP
                elif event.key == K_ESCAPE:
                    pygame.quit()
                    cur.close
                    conn.close
                    sys.exit()
    
    elif mode == G_SELECT_MAP:
        if "problem.addition" in sys.modules:
            sys.modules.pop("problem.addition")
        if "problem.xor01" in sys.modules:
            sys.modules.pop("problem.xor01")
        screen.fill((255, 255, 255))
        text = font160.render("MAP SELECT", True,(0,0,0))
        screen.blit(text, [(w - text.get_width()) / 2, 0])
        x, y = pygame.mouse.get_pos()
        #1つあたり160x80位
        for i in range(len(maplist)):
            if w / 2 - 80 < x < w / 2 + 80 and h / 2 - 50 - (len(maplist) / 2 - i) * 100 < y < h / 2 + 30 - (len(maplist) / 2 - i) * 100:
                mapselector = i
                break
        for i in range(len(maplist)):
            if i == mapselector:
                pygame.draw.rect(screen, (0, 0, 0), Rect(w / 2 - 80, h / 2 - 50 - (len(maplist) / 2 - i) * 100, 160, 80))
                text = font80.render(maplist[i], True, (255, 255, 255))
            else:
                pygame.draw.rect(screen, (255, 255, 255), Rect(w / 2 - 80, h / 2 - 50 - (len(maplist) / 2 - i ) * 100, 160, 80))
                text = font80.render(maplist[i], True, (0, 0, 0))  
            screen.blit(text, [(w - text.get_width()) / 2, (h - 80) / 2 - (len(maplist) / 2 - i ) * 100])
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                cur.close
                conn.close
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                for i in range(len(maplist)):
                    if w / 2 - 80 < x < w / 2 + 80 and h / 2 - 50 - (len(maplist) / 2 - i) * 100 < y < h / 2 + 30 - (len(maplist) / 2 - i) * 100:
                        if maplist[i] == "back":
                            mapselector = 0
                            mode = G_TITLE
                        elif maplist[i] == "easy":
                            from map.easy import *
                            mapstr = "easy"
                            setupMapfunction = setEasy
                            car, the_map, loclist, road = setEasy(w, h)
                            mode = G_SELECT_PROBLEM
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    cur.close
                    conn.close
                    sys.exit()
                elif event.key == K_DOWN:
                    mapselector = min(mapselector + 1, len(maplist) - 1)
                elif event.key == K_UP:
                    mapselector = max(mapselector - 1, 0)
                elif event.key == K_RETURN:
                    if maplist[mapselector] == "back":
                        mapselector = 0
                        mode = G_TITLE
                    elif maplist[mapselector] == "easy":
                        from map.easy import *
                        mapstr = "easy"
                        setupMapfunction = setEasy
                        car, the_map, loclist, road = setEasy(w, h)
                        mode = G_SELECT_PROBLEM
    
    elif mode == G_SELECT_PROBLEM:
        screen.fill((255, 255, 255))
        text = font160.render("PROBLEM SELECT", True, (0, 0, 0))
        screen.blit(text, [(w - text.get_width()) / 2, 0])
        x, y = pygame.mouse.get_pos()
        #1つあたり240x80位
        for i in range(len(problemlist)):
            if w / 2 - 80 < x < w / 2 + 80 and h / 2 - 50 - (len(problemlist) / 2 - i) * 100 < y < h / 2 + 30 - (len(problemlist) / 2 - i) * 100:
                problemselector = i
                break
        for i in range(len(problemlist)):
            if i == problemselector:
                text = font80.render(problemlist[i], True, (255, 255, 255))
                pygame.draw.rect(screen, (0, 0, 0), Rect(w / 2 - 120, (h - 80) / 2 - (len(maplist) / 2 - i) * 100, 240, 80))
            else:
                text = font80.render(problemlist[i], True, (0, 0, 0))
                pygame.draw.rect(screen, (255, 255, 255), Rect(w / 2 - 120, (h - 80) / 2 - (len(maplist) / 2 - i) * 100, 240, 80))
            screen.blit(text, [(w - text.get_width()) / 2, (h - 80) / 2 - (len(maplist) / 2 - i) * 100])
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                cur.close
                conn.close
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                x,y = event.pos
                for i in range(len(problemlist)):
                    if w / 2 - 80 < x < w / 2 + 80 and h / 2 - 50 - (len(problemlist) / 2 - i) * 100 < y < h / 2 + 30 - (len(problemlist) / 2 - i) * 100:
                        if problemlist[i] == "back":
                            problemselector = 0
                            mode = G_SELECT_MAP
                        elif problemlist[i] == "addition":
                            mode = G_GAME
                            problemstr = "addition"
                            from problem.addition import *
                            set_problem(loclist)
                            setup(car,loclist,the_map,road,h,w,False)
                        elif problemlist[i] == "xor01":
                            mode = G_GAME
                            problemstr = "xor01"
                            from problem.xor import *
                            set_problem(loclist)
                            setup(ca,loclist,the_map,road,h,w,False)
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    cur.close
                    conn.close
                    sys.exit()
                elif event.key == K_DOWN:
                    problemselector = min(problemselector + 1, len(problemlist) - 1)
                elif event.key == K_UP:
                    problemselector = max(problemselector - 1, 0)
                elif event.key == K_RETURN:
                    if problemlist[problemselector] == "back":
                        problemselector = 0
                        mode = G_SELECT_MAP
                    elif problemlist[problemselector] == "addition":
                        mode = G_GAME
                        problemstr = "addition"
                        from problem.addition import *
                        set_problem(loclist)
                        setup(car,loclist,the_map,road,h,w,False)
                    elif problemlist[problemselector] == "xor01":
                        mode = G_GAME
                        problemstr = "xor01"
                        from problem.xor01 import *
                        set_problem(loclist)
                        setup(car,loclist,the_map,road,h,w,False)
    
    elif mode == G_GAME:
        screen.fill((255, 255, 255))
        finished, ans = gaming(screen)
        if finished:
            if ans == check:
                car, the_map, loclist, road = setEasy(w, h)
                set_test(loclist, 0)
                setup(car, loclist, the_map, road, h, w, True)
                mode = G_TEST
            else:
                mode = G_FIRED

    elif mode == G_TEST:
        screen.fill((255, 255, 255))
        finished, result = testing(screen)
        if finished:
            if result == check_test[testphase]:
                testphase+=1
                if testphase == len(check_test):
                    mode = G_NAME
                    cur.execute("SELECT name, txt FROM ranking WHERE map = \"" + mapstr + "\" AND problem = \"" + problemstr + "\" ORDER BY txt LIMIT 5")
                    txtrank = cur.fetchall()
                    cur.execute("SELECT name, run FROM ranking WHERE map = \"" + mapstr + "\" AND problem = \"" + problemstr + "\" ORDER BY run LIMIT 5")
                    runrank = cur.fetchall()
                else:
                    car, the_map, loclist, road = setupMapfunction(w, h)
                    set_test(loclist, testphase)
                    setup(car, loclist, the_map, road, h, w, True)
            else:
                mode = G_FIRED
    
    elif mode == G_NAME:
        pygame.draw.rect(screen, (255, 255, 200), Rect(30, 10, 1220, 700))
        txt,run=get_score()
        text = font100.render("Score: {:d}bytes / {:.3f}miles".format(txt,run), True, (0, 0, 0))
        screen.blit(text, [(w-text.get_width())//2,10])
        text = font80.render("code", True, (0, 0, 0))
        screen.blit(text,[320-text.get_width()/2,150])
        text = font80.render("distance", True, (0, 0, 0))
        screen.blit(text,[960-text.get_width()/2,150])
        #左は(70-620)x(200-470)
        for i in range(len(txtrank)):
            rankstr = font50.render(countingStr(i+1), True, (0, 0, 0))
            username = font50.render(str(txtrank[i][0]), True, (0, 0, 0))
            txtscore = font50.render(str(txtrank[i][1]), True, (0, 0, 0))
            screen.blit(rankstr, [80, 210+70*i])
            screen.blit(username, [210,210+70*i])
            screen.blit(txtscore, [500,210+70*i])
            pygame.draw.rect(screen, (0,0,0), Rect(70,200+70*i,550,70),10)
            pygame.draw.line(screen, (0,0,0), (190,200+70*i), (190,270+70*i), 10)
            pygame.draw.line(screen, (0,0,0), (480,200+70*i), (480,270+70*i), 10)
        #右は(660-1210)x(120-470)
        for i in range(len(runrank)):
            rankstr = font50.render(countingStr(i+1), True, (0, 0, 0))
            username = font50.render(str(runrank[i][0]), True, (0, 0, 0))
            runscore = font50.render(str(runrank[i][1]), True, (0, 0, 0))
            screen.blit(rankstr, [670, 210+70*i])
            screen.blit(username, [800, 210 + 70 * i])
            screen.blit(runscore, [1090, 210 + 70 * i])
            pygame.draw.rect(screen, (0, 0, 0), Rect(660, 200 + 70 * i, 550, 70), 10)
            pygame.draw.line(screen, (0, 0, 0), (790, 200 + 70 * i), (790, 270 + 70 * i), 10)
            pygame.draw.line(screen, (0, 0, 0), (1070, 200 + 70 * i), (1070, 270 + 70 * i), 10)
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                pygame.quit()
                cur.close
                conn.close
                sys.exit()
            elif event.type == KEYDOWN: 
                if event.key == K_ESCAPE:
                    pygame.quit()
                    cur.close
                    conn.close
                    sys.exit()
                elif event.key == K_RETURN:
                    username = textinput.get_text()
                    ok = len(username)<64
                    for i in username:
                        if not i in "abcdefghijklmnopqretuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_!?.,(){}[]@":
                            ok = False
                    if ok:
                        cur.execute("SELECT run,txt FROM ranking WHERE name = \""+username+"\" AND map =  \"" + mapstr + "\" AND problem = \"" + problemstr + "\"")
                        result = cur.fetchall()
                        if len(result)==0:
                            cur.execute("INSERT INTO ranking VALUE(\""+username+"\", {:.3f}, {:d}, \"".format(run,txt)+mapstr+"\", \""+problemstr+"\")")
                        else:
                            run = min(run, result[0][0])
                            txt = min(txt, result[0][1])
                            cur.execute("UPDATE ranking SET run = {:.3f}, txt = {:d} WHERE name = \"".format(run,txt)+username+"\"")
                        conn.commit()
                        cur.execute("SELECT name, txt FROM ranking WHERE map = \"" + mapstr +
                                    "\" AND problem = \"" + problemstr + "\" ORDER BY txt LIMIT 5")
                        txtrank = cur.fetchall()
                        cur.execute("SELECT name, run FROM ranking WHERE map = \"" + mapstr +
                                "\" AND problem = \"" + problemstr + "\" ORDER BY run LIMIT 5")
                        runrank = cur.fetchall()
                        mode = G_RANKING
        text = font50.render("Register with the ranking!! Your Name:", True, (0, 0, 0))
        screen.blit(text, (50, 600))
        textinput.update(events)
        screen.blit(textinput.get_surface(), (700, 600))
    elif mode == G_RANKING:
        pygame.draw.rect(screen, (255, 255, 200), Rect(30, 10, 1220, 700))
        txt, run = get_score()
        text = font100.render(
            "Score: {:d}bytes / {:.3f}miles".format(txt, run), True, (0, 0, 0))
        screen.blit(text, [(w - text.get_width()) // 2, 10])
        text = font80.render("code", True, (0, 0, 0))
        screen.blit(text, [320 - text.get_width() / 2, 150])
        text = font80.render("distance", True, (0, 0, 0))
        screen.blit(text, [960 - text.get_width() / 2, 150])
        #左は(70-620)x(200-470)
        for i in range(len(txtrank)):
            rankstr = font50.render(countingStr(i + 1), True, (0, 0, 0))
            username = font50.render(str(txtrank[i][0]), True, (0, 0, 0))
            txtscore = font50.render(str(txtrank[i][1]), True, (0, 0, 0))
            screen.blit(rankstr, [80, 210 + 70 * i])
            screen.blit(username, [210, 210 + 70 * i])
            screen.blit(txtscore, [500, 210 + 70 * i])
            pygame.draw.rect(screen, (0, 0, 0), Rect(
                70, 200 + 70 * i, 550, 70), 10)
            pygame.draw.line(screen, (0, 0, 0), (190, 200 +
                                                 70 * i), (190, 270 + 70 * i), 10)
            pygame.draw.line(screen, (0, 0, 0), (480, 200 +
                                                 70 * i), (480, 270 + 70 * i), 10)
        #右は(660-1210)x(120-470)
        for i in range(len(runrank)):
            rankstr = font50.render(countingStr(i + 1), True, (0, 0, 0))
            username = font50.render(str(runrank[i][0]), True, (0, 0, 0))
            runscore = font50.render(str(runrank[i][1]), True, (0, 0, 0))
            screen.blit(rankstr, [670, 210 + 70 * i])
            screen.blit(username, [800, 210 + 70 * i])
            screen.blit(runscore, [1090, 210 + 70 * i])
            pygame.draw.rect(screen, (0, 0, 0), Rect(
                660, 200 + 70 * i, 550, 70), 10)
            pygame.draw.line(screen, (0, 0, 0), (790, 200 +
                                                 70 * i), (790, 270 + 70 * i), 10)
            pygame.draw.line(screen, (0, 0, 0), (1070, 200 +
                                                 70 * i), (1070, 270 + 70 * i), 10)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                cur.close
                conn.close
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    cur.close
                    conn.close
                    pygame.quit()
                    sys.exit()
                elif event.key == K_RETURN:
                    mode = G_SELECT_MAP
    elif mode == G_FIRED:
        screen.blit(fired,[(w-fired.get_width())/2,(h-fired.get_height())/2])
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                cur.close
                conn.close
                sys.exit()
            elif event.type == KEYDOWN: 
                if event.key == K_ESCAPE:
                    pygame.quit()
                    cur.close
                    conn.close
                    sys.exit()
                if event.key == K_RETURN:
                    mode = G_TITLE
    
    pygame.display.update()
    clock.tick(30)
