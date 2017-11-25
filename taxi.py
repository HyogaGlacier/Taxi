#-*- coding:utf-8 -*-
import pygame
from pygame.locals import *
import sys
import os
import importlib

# データベース初期設定
import mysql.connector
conn = mysql.connector.connect(user='root', password='', host='localhost', database='taxi')
cur=conn.cursor()
txtrank = []
runrank = []
def updatesql():
    global cur, conn, problemstr, mapsttr, txtrank, runrank
    cur.execute("SELECT name, txt FROM ranking WHERE map = \"" + mapstr + "\" AND problem = \"" + problemstr + "\" ORDER BY txt LIMIT 5")
    txtrank = cur.fetchall()
    cur.execute("SELECT name, run FROM ranking WHERE map = \"" + mapstr + "\" AND problem = \"" + problemstr + "\" ORDER BY run LIMIT 5")
    runrank = cur.fetchall()
    conn.commit()

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

#ゲーム終了
def gameend():
    pygame.quit()
    cur.close
    conn.close
    sys.exit()

# 引数の2番目をFULLSCREENにするとフルスクリーンになります
screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32)
pygame.display.set_caption("Taxi")

#フォント設定
font50 = pygame.font.Font(None, 50)
font80 = pygame.font.Font(None, 80)
font100 = pygame.font.Font(None, 100)
font160 = pygame.font.Font(None, 160)
#その他インポート
from driver import *
import writer

#mapselectで用いるリスト設定
maplist = os.listdir("map")
mapstr = ""
for i in reversed(range(len(maplist))):
    if maplist[i][:2] == "__":
        del maplist[i]
    else:
        maplist[i] = maplist[i][:-3]
maplist.append("back")
maps = None
mapselector = 0
setupMapfunction = None
#mapのインポート
def mapset():
    global maplist, mapselector, maps, setupMapfunction, car, the_map, loclist, road, w, h
    maps = importlib.import_module("map." + maplist[mapselector])
    mapstr = maplist[mapselector]
    setupMapfunction = maps.set
    car, the_map, loclist, road = setupMapfunction(w, h)
#mapモジュールの削除
def mapdelete():
    global mapstr, maps, mapselector, setupMapfunction
    if "map." + mapstr in sys.modules:
        sys.modules.pop("map." + mapstr)
        mapstr = ""
        maps = None
        setupMapfunction = None
        mapselector = 0

#problemselectで用いるリスト設定
problemlist = os.listdir("problem")
problemstr = ""
for i in reversed(range(len(problemlist))):
    if problemlist[i][:2] == "__":
        del problemlist[i]
    else:
        problemlist[i] = problemlist[i][:-3]
problemlist.append("back")
problems = None
problemselector = 0
#problemのインポート
def problemset():
    global problemstr, problemlist, problemselector, problems, car, loclist, the_map, road, w, h
    problemstr = problemlist[problemselector]
    problems = importlib.import_module("problem." + problemstr)
    problems.set_problem(loclist)
    setup(car, loclist, the_map, road, h, w, False)
#problemモジュールの削除
def problemdelete():
    global problemstr, problems, problemselector
    if "problem." + problemstr in sys.modules:
        sys.modules.pop("problem." + problemstr)
        problemselector = 0
        problems = None

#画像、テキストエディタ、クロック
titlelogo = pygame.image.load("img/logo.png")
fired = pygame.image.load("img/gameover.png")
textinput = writer.TextInput()
clock = pygame.time.Clock()

while True:
    #タイトル画面
    if mode == G_TITLE:
        #ロゴ、背景表示
        screen.fill((255, 255, 255))
        screen.blit(titlelogo, [(w - titlelogo.get_width()) / 2.0, (h - titlelogo.get_height()) / 2.0])
        
        #スタート文字の表示（mouseonで変更）
        x, y = pygame.mouse.get_pos()
        text = font80.render("start", True, (255, 255, 255))
        if (w - text.get_width()) / 2 - 20 < x < (w + text.get_width()) / 2 + 20 and h * 3 / 4 - 10 < y < h * 3 / 4 + text.get_height() + 10:
            text = font80.render("start", True, (0, 0, 0))
            pygame.draw.rect(screen, (255, 255, 255), Rect((w - text.get_width()) / 2 - 20, h * 3 / 4 - 10, text.get_width() + 40, text.get_height() + 20))
        else:
            pygame.draw.rect(screen, (0, 0, 0), Rect((w - text.get_width()) / 2 - 20, h * 3 / 4 - 10, text.get_width() + 40, text.get_height() + 20))
        screen.blit(text, [(w - text.get_width()) / 2, h * 3 / 4])

        #イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:
                gameend()
            #クリック処理
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                if (w - text.get_width()) / 2 - 20 < x < (w + text.get_width()) / 2 + 20 and h * 3 / 4 - 10 < y < h * 3 / 4 + text.get_height() + 10:
                    mapdelete()
                    mode = G_SELECT_MAP
            #キー処理
            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    mapdelete()
                    mode = G_SELECT_MAP
                elif event.key == K_ESCAPE:
                    gameend()
    
    #マップ設定画面
    elif mode == G_SELECT_MAP:
        #画面表示
        screen.fill((255, 255, 255))
        text = font160.render("MAP SELECT", True, (0, 0, 0))
        screen.blit(text, [(w - text.get_width()) / 2, 0])
        x, y = pygame.mouse.get_pos()
        #map選択欄は1つあたり160x80位。mouseonで変更
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
        
        #イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:
                endgame()
            #クリック処理
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                for i in range(len(maplist)):
                    if w / 2 - 80 < x < w / 2 + 80 and h / 2 - 50 - (len(maplist) / 2 - i) * 100 < y < h / 2 + 30 - (len(maplist) / 2 - i) * 100:
                        if maplist[i] == "back":
                            mapselector = 0
                            mode = G_TITLE
                        else:
                            mapset()
                            problemdelete()
                            mode = G_SELECT_PROBLEM
            #キー処理
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    endgame()
                #セレクタ
                elif event.key == K_DOWN:
                    mapselector = min(mapselector + 1, len(maplist) - 1)
                elif event.key == K_UP:
                    mapselector = max(mapselector - 1, 0)
                elif event.key == K_RETURN:
                    if maplist[mapselector] == "back":
                        mapselector = 0
                        mode = G_TITLE
                    else:
                        mapset()
                        mode = G_SELECT_PROBLEM
    
    #問題設定画面
    elif mode == G_SELECT_PROBLEM:
        #画面表示
        screen.fill((255, 255, 255))
        text = font160.render("PROBLEM SELECT", True, (0, 0, 0))
        screen.blit(text, [(w - text.get_width()) / 2, 0])
        x, y = pygame.mouse.get_pos()
        #problem選択欄は1つあたり240x80位。
        for i in range(len(problemlist)):
            if w / 2 - 80 < x < w / 2 + 80 and h / 2 - 50 - (len(problemlist) / 2 - i) * 100 < y < h / 2 + 30 - (len(problemlist) / 2 - i) * 100:
                problemselector = i
                break
        for i in range(len(problemlist)):
            if i == problemselector:
                text = font80.render(problemlist[i], True, (255, 255, 255))
                pygame.draw.rect(screen, (0, 0, 0), Rect(w / 2 - 120, (h - 80) / 2 - (len(problemlist) / 2 - i) * 100, 240, 80))
            else:
                text = font80.render(problemlist[i], True, (0, 0, 0))
                pygame.draw.rect(screen, (255, 255, 255), Rect(w / 2 - 120, (h - 80) / 2 - (len(maplist) / 2 - i) * 100, 240, 80))
            screen.blit(text, [(w - text.get_width()) / 2, (h - 80) / 2 - (len(problemlist) / 2 - i) * 100])
        
        #イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:
                gameend()
            #クリック処理
            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                x,y = event.pos
                for i in range(len(problemlist)):
                    if w / 2 - 80 < x < w / 2 + 80 and h / 2 - 50 - (len(problemlist) / 2 - i) * 100 < y < h / 2 + 30 - (len(problemlist) / 2 - i) * 100:
                        if problemlist[i] == "back":
                            mapdelete()
                            mode = G_SELECT_MAP
                        else:
                            setproblem()
                            mode = G_GAME
            #キー処理
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    gameend()
                #セレクタ
                elif event.key == K_DOWN:
                    problemselector = min(problemselector + 1, len(problemlist) - 1)
                elif event.key == K_UP:
                    problemselector = max(problemselector - 1, 0)
                elif event.key == K_RETURN:
                    if problemlist[problemselector] == "back":
                        mapdelete()
                        mode = G_SELECT_MAP
                    else:
                        problemset()
                        mode = G_GAME
    # ゲーム中（基本的に画面含めdriverに投げます）
    elif mode == G_GAME:
        screen.fill((255, 255, 255))
        finished, ans = gaming(screen)
        #答え確認
        if finished:
            if ans == problems.check:
                car, the_map, loclist, road = setupMapfunction(w, h)
                problems.set_test(loclist, 0)
                setup(car, loclist, the_map, road, h, w, True)
                mode = G_TEST
            else:
                mode = G_FIRED
    # テスト中（基本的に画面含めdriverに投げます）
    elif mode == G_TEST:
        screen.fill((255, 255, 255))
        finished, result = testing(screen)
        if finished:
            #答え確認、残りの問題が無くなったら終了
            if result == problems.check_test[problems.testphase]:
                problems.testphase+=1
                if problems.testphase == len(problems.check_test):
                    mode = G_NAME
                else:
                    car, the_map, loclist, road = setupMapfunction(w, h)
                    problems.set_test(loclist, problems.testphase)
                    setup(car, loclist, the_map, road, h, w, True)
            else:
                mode = G_FIRED
    
    #クリア画面。名前の受け取りを行います
    elif mode == G_NAME:
        #枠
        pygame.draw.rect(screen, (255, 255, 200), Rect(30, 10, 1220, 700))
        #スコア
        txt,run=get_score()
        text = font100.render("Score: {:d}bytes / {:.3f}miles".format(txt,run), True, (0, 0, 0))
        screen.blit(text, [(w-text.get_width())//2,10])

        #ランキング表の表示
        text = font80.render("code", True, (0, 0, 0))
        screen.blit(text,[320-text.get_width()/2,150])
        text = font80.render("distance", True, (0, 0, 0))
        screen.blit(text,[960-text.get_width()/2,150])
        #左は(70-620)x(200-550)
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
        #右は(660-1210)x(200-550)
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
        
        #イベント処理
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                gameend()
            elif event.type == KEYDOWN: 
                if event.key == K_ESCAPE:
                    gameend()
                #ランキング登録
                elif event.key == K_RETURN:
                    username = textinput.get_text()
                    #一応のSQL対策
                    ok = len(username) < 64
                    for i in username:
                        if not i in "abcdefghijklmnopqretuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_!?.,(){}[]@":
                            ok = False
                    if ok:
                        #名前があるならそれぞれ最小値で更新、そうでないなら普通にinsertし、ランキング表示画面へ移行
                        cur.execute("SELECT run,txt FROM ranking WHERE name = \"" + username + "\" AND map =  \"" + mapstr + "\" AND problem = \"" + problemstr + "\"")
                        result = cur.fetchall()
                        if len(result) == 0:
                            cur.execute("INSERT INTO ranking VALUE(\""+username+"\", {:.3f}, {:d}, \"".format(run, txt) + mapstr + "\", \"" + problemstr + "\")")
                        else:
                            run = min(run, result[0][0])
                            txt = min(txt, result[0][1])
                            cur.execute("UPDATE ranking SET run = {:.3f}, txt = {:d} WHERE name = \"".format(run, txt) + username + "\"")
                        conn.commit()
                        updatesql()
                        mode = G_RANKING
        #ユーザーネーム入力欄
        text = font50.render("Register with the ranking!! Your Name:", True, (0, 0, 0))
        screen.blit(text, (50, 600))
        textinput.update(events)
        screen.blit(textinput.get_surface(), (700, 600))
    
    #ランキング表示
    elif mode == G_RANKING:
        #枠
        pygame.draw.rect(screen, (255, 255, 200), Rect(30, 10, 1220, 700))
        #あなたの記録
        txt, run = get_score()
        text = font100.render("Score: {:d}bytes / {:.3f}miles".format(txt, run), True, (0, 0, 0))
        screen.blit(text, [(w - text.get_width()) // 2, 10])

        #ランキング表示
        text = font80.render("code", True, (0, 0, 0))
        screen.blit(text, [320 - text.get_width() / 2, 150])
        text = font80.render("distance", True, (0, 0, 0))
        screen.blit(text, [960 - text.get_width() / 2, 150])
        #左は(70-620)x(200-550)
        for i in range(len(txtrank)):
            rankstr = font50.render(countingStr(i + 1), True, (0, 0, 0))
            username = font50.render(str(txtrank[i][0]), True, (0, 0, 0))
            txtscore = font50.render(str(txtrank[i][1]), True, (0, 0, 0))
            screen.blit(rankstr, [80, 210 + 70 * i])
            screen.blit(username, [210, 210 + 70 * i])
            screen.blit(txtscore, [500, 210 + 70 * i])
            pygame.draw.rect(screen, (0, 0, 0), Rect(70, 200 + 70 * i, 550, 70), 10)
            pygame.draw.line(screen, (0, 0, 0), (190, 200 + 70 * i), (190, 270 + 70 * i), 10)
            pygame.draw.line(screen, (0, 0, 0), (480, 200 + 70 * i), (480, 270 + 70 * i), 10)
        #右は(660-1210)x(120-550)
        for i in range(len(runrank)):
            rankstr = font50.render(countingStr(i + 1), True, (0, 0, 0))
            username = font50.render(str(runrank[i][0]), True, (0, 0, 0))
            runscore = font50.render(str(runrank[i][1]), True, (0, 0, 0))
            screen.blit(rankstr, [670, 210 + 70 * i])
            screen.blit(username, [800, 210 + 70 * i])
            screen.blit(runscore, [1090, 210 + 70 * i])
            pygame.draw.rect(screen, (0, 0, 0), Rect(660, 200 + 70 * i, 550, 70), 10)
            pygame.draw.line(screen, (0, 0, 0), (790, 200 + 70 * i), (790, 270 + 70 * i), 10)
            pygame.draw.line(screen, (0, 0, 0), (1070, 200 + 70 * i), (1070, 270 + 70 * i), 10)
        
        #イベント処理
        for event in pygame.event.get():
            if event.type == QUIT:
                gameend()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    gameend()
                elif event.key == K_RETURN:
                    mapdelete()
                    mode = G_SELECT_MAP
    
    #ゲームオーバー画面
    elif mode == G_FIRED:
        screen.blit(fired, [(w - fired.get_width()) / 2, (h - fired.get_height()) / 2])
        for event in pygame.event.get():
            if event.type == QUIT:
                gameend()
            elif event.type == KEYDOWN: 
                if event.key == K_ESCAPE:
                    gameend()
                if event.key == K_RETURN:
                    mode = G_TITLE
    
    pygame.display.update()
    clock.tick(30)
