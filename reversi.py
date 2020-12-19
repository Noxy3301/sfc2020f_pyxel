import pyxel
import copy

pyxel.init(200,250)
pyxel.mouse(True)
header = 50

turn = 0
which_turn = 1
one_score = 2
two_score = 2
enemy = 1
cannot_put = False
gameEnd = 0 #1が1Pの盤面勝利 2が2Pの盤面勝利 3は盤面が埋まった時

board = []
okeru = []
weight = []
direction_xy = [[-1,-1], [ 0,-1], [ 1,-1],
                [-1, 0],          [ 1, 0],
                [-1, 1], [ 0, 1], [ 1, 1]]

can_put = [] #石を置けるところを保存しておく
put_line = [] #石を置いたときに変更されるところを置く


def init(): #初期化
    global board, weight, turn
    turn = 0
    board = []
    weight = []
    for i in range(8):
        if i == 0 or i == 7:
            tmp = [9 for j in range(8)]
        else:
            tmp = [9] + [0 for j in range(6)] + [9]
        board.append(tmp)
        weight = copy.deepcopy(board)
    board[3][3] = board[4][4] = 2
    board[3][4] = board[4][3] = 1
    weight[3][3] = weight[4][4] = weight[3][4] = weight[4][3] = 1

    init_okeru()
    search(1)

def init_okeru(): #置けるところの初期化
    global okeru
    okeru = []
    for i in range(8):
        if i == 0 or i == 7:
            tmp = [9 for j in range(8)]
        else:
            tmp = [9] + [0 for j in range(6)] + [9]
        okeru.append(tmp)

def search(you): #置けるところ検索
    global board, direction_xy, can_put, put_line
    flag = 0
    isloop = True
    if you == 1:
        enemy = 2
    else:
        enemy = 1
    can_put = []            #bebug
    put_line = []
    for i in range(1,7):
        for j in range(1,7):
            if board[i][j] != 0: #石が既に置かれていたら飛ばす
                continue
            for dx, dy in direction_xy:
                if board[i][j] != 0:
                    continue
                x = i
                y = j
                put_line_temp = []
                flag = 0 # 0:default / 1:隣接 / 2:ok
                isloop = True
                while isloop == True:
                    x += dx
                    y += dy
                    #敵の碁石が隣接しているか
                    if flag == 0:
                        if board[x][y] != enemy:
                            isloop = False
                        else:
                            flag = 1
                            put_line_temp.append([x,y])
                        continue
                    if flag == 1:
                        put_line_temp.append([x ,y])
                        if board[x][y] == you: #○●○とかのケース
                            flag = 2
                            isloop = False
                        elif board[x][y] == 0 or board[x][y] == 9: #空白か壁のケース
                            isloop = False
                    if flag == 2:
                        okeru[i][j] = 3
                        can_put.append([i,j])       #debug
                        put_line.append(put_line_temp)
    return len(can_put)

def cordinate_to_sq(cord): #マウスの座標をリバーシのマス目に変換
    if 2 <= cord and cord <= 33:
        return 1
    elif 35 <= cord and cord <= 66:
        return 2
    elif 68 <= cord and cord <= 99:
        return 3
    elif 101 <= cord and cord <= 132:
        return 4
    elif 134 <= cord and cord <= 165:
        return 5
    elif 167 <= cord and cord <= 198:
        return 6
    else:
        return 0

def mouse_cordinate():
    global header
    mx = cordinate_to_sq(pyxel.mouse_x)
    my = cordinate_to_sq(pyxel.mouse_y - header)
    return my, mx

def putHere(x,y): #そこに置けるかどうかの確認
    global board, can_put
    for i in range(len(can_put)):
        if can_put[i] == [x,y]:
            return True
    return False

def put(stone, px, py): #石を置く処理
    global board, can_put
    for i in range(len(can_put)):
        if can_put[i] == [px, py]:
            board[px][py] = stone
            for j in range(len(put_line[i])):
                board[put_line[i][j][0]][put_line[i][j][1]] = stone

def weight_update(): #石の価値を更新
    global board,weight, one_score, two_score
    one_score = two_score = 0
    for i in range(1,7):
        for j in range(1,7):
            if board[i][j] != 0:
                weight[i][j] += 1
                if board[i][j] == 1:
                    one_score += weight[i][j]
                elif board[i][j] == 2:
                    two_score += weight[i][j]

def find_space(): #空白があるかどうか
    global board
    num = 0
    for i in range(1,7):
        for j in range(1,7):
            if board[i][j] == 0:
                num += 1
    return num

def update():
    global turn, can_put, which_turn, enemy, cannot_put, one_score, two_score, gameEnd
    #途中で持ち駒が0になった時
    if one_score == 0:
        gameEnd = 2
    elif two_score == 1:
        gameEnd = 1
    #盤面が全部埋まった時
    elif find_space() == 0:
        gameEnd = 3
    
    if gameEnd == 0:
        if search(enemy) == 0:
            cannot_put = True
            if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
                cannot_put = False
                if enemy == 2:
                    enemy = 1
                    you = 2
                else:
                    enemy = 2
                    you = 1
                init_okeru()
                search(enemy)
                turn += 1
                if turn%2 == 0:
                    which_turn = 1
                else:
                    which_turn = 2
        elif pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
            px, py = mouse_cordinate()
            if px != 0 and py != 0 and putHere(px, py) == True:
                if turn%2 == 0:
                    you = 1
                    enemy = 2
                else:
                    you = 2
                    enemy = 1
                put(you, px, py)
                
                init_okeru()
                search(enemy)
                turn += 1
                if turn%2 == 0:
                    which_turn = 1
                else:
                    which_turn = 2
                weight_update()

def draw():
    global header, which_turn, one_score, two_score, weight, cannot_put, gameEnd
    pyxel.cls(9)
    pyxel.rect(0, header, 200, 200, 3)
    pyxel.circ(50,35,10,7)
    if which_turn == 1:
        pyxel.rect(80,10,40,15,7)
    else:
        pyxel.rect(80,10,40,15,0)
    pyxel.text(75+5,33,str(one_score),7)
    pyxel.circ(150,35,10,0)
    pyxel.text(125-12,33,str(two_score),0)
    pyxel.text(83,15,"{}P's turn".format(which_turn),5)
    
    for i in range(7):
        pyxel.rect(i*33,header, 2, 200, 0)
        pyxel.rect(0,header + (i*33), 200, 2, 0)

    for i in range(1,7):
        for j in range(1,7):
            tx = i-1
            ty = j-1
            margin = 17
            if board[i][j] == 1: #白
                pyxel.circ(ty*33 + margin,tx*33 + margin + header,14,7)
                pyxel.text(ty*33-1 + margin,tx*33 + margin + header-2,str(weight[i][j]),0)
            elif board[i][j] == 2: #黒
                pyxel.circ(ty*33 + margin,tx*33 + margin + header,14,0)
                pyxel.text(ty*33-1 + margin,tx*33 + margin + header-2,str(weight[i][j]),7)
            if okeru[i][j] == 3:
                pyxel.circ(ty*33 + margin,tx*33 + margin + header,14,10)

    if cannot_put == True and gameEnd == 0:
        pyxel.rect(40,125,120,25,15)
        pyxel.text(50,130,"there is no place to put",0)
        pyxel.text(75,140,"click to pass",0)
    if gameEnd == 1:
        pyxel.rect(40,125,120,25,15)
        pyxel.text(50,130,"1P win!",0)
    if gameEnd == 2:
        pyxel.rect(40,125,120,25,15)
        pyxel.text(50,130,"2P win!",0)
    if gameEnd == 3:
        pyxel.rect(40,125,120,25,15)
        if one_score > two_score:
            pyxel.text(85,135,"1P win!",0)
        elif two_score > one_score:
            pyxel.text(85,135,"2P win!",0)
        else:
            pyxel.text(90,135,"draw",0)

init()
pyxel.run(update, draw)