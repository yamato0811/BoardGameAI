# ソケット通信クライアント

import socket
import time
import json

BUFSIZE = 1024

# 接続先(どうぶつしょうぎサーバを起動したPC)の情報
serverName = "localhost"
serverPort = 4444

# ソケット通信を確立
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((serverName, serverPort))

######## 関数 ###########################################################

#オフライン開発用関数
def printBoard(boardinfo):
    #Player2の持ち駒を出力
    print("-------------------")
    print("Player2:", end='')
    for num in "123456":
        print(boardinfo.get("E" + num, ""), end='')
    print("\n")

    #盤面を出力
    for num in "1234":
        for alpha in "ABC":
            print(boardinfo.get(alpha + num, "--"), end='')
            if(alpha == "C"):
                print()
    print()

    #Player1の持ち駒を出力
    print("Player1:", end='')
    for num in "123456":
        print(boardinfo.get("D" + num, ""), end='')
    print("\n-------------------")


#盤面を読み取る関数
def readBoard():
    s.send(("boardjson" + "\n").encode()) 
    time.sleep(0.1)
    boardinfo = json.loads(s.recv(BUFSIZE).rstrip().decode())  #初期の盤面情報を取得
    return boardinfo


# 引数：マスを表す文字列（例：'B2'）
# 返り値：座標を表すタプル（例: (1,1)）
def masuToXy(st):
    x = 0
    y = 0
    if st[0] == "A":
        x = 0
    elif st[0] == "B":
        x = 1
    elif st[0] == "C":
        x = 2
        
    if st[1] == "1":
        y = 0
    elif st[1] == "2":
        y = 1
    elif st[1] == "3":
        y = 2
    elif st[1] == "4":
        y = 3
    
    return (x,y)

# 引数：座標を表すタプル（例: (1,1)）
# 返り値：マスを表す文字列（例：'B2'）
def xyToMasu(t):
    if t[0] == 0:
        xstr = "A"
    elif t[0] == 1:
        xstr = "B"
    elif t[0] == 2:
        xstr = "C"
        
    if t[1] == 0:
        ystr = "1"
    elif t[1] == 1:
        ystr = "2"
    elif t[1] == 2:
        ystr = "3"
    elif t[1] == 3:
        ystr = "4"

    return xstr + ystr


#勝敗判定関数
def judgeWL(boardinfo):
    if("l"+player not in boardinfo.values()):
        return False
    elif("l"+aite not in boardinfo.values()):
        return True
    
    #トライ判定
    for srcStr, komaStr in boardinfo.items():
        Flag = False
        #勝ち
        if(komaStr == "l"+player and srcStr[1] == aiteField):
            for aiteTe in showMoveRange(boardinfo, aite):
                if(aiteTe[1] == srcStr):
                    Flag = True
            if(Flag == False):
                return True
        #負け
        elif(komaStr == "l"+aite and srcStr[1] == playerField):
            for Te in showMoveRange(boardinfo, player):
                if(Te[1] == srcStr):
                    Flag = True
            if(Flag == False):
                return False


#🦁
lionKiki = ((0,  -1), (1,  -1), (-1, -1), (1,  0), (-1,  0),
                (1,  1),  (-1,  1), (0,   1))
#🦒
kirinKiki = ((0, 1), (0, -1), (1, 0), (-1, 0))
#🐤
hiyokoKiki_1 = ((0, -1),)
hiyokoKiki_2 = ((0, 1),)
#🐓
niwatoriKiki_1 = ((0,  -1), (1,  -1), (-1, -1), (1,  0), (-1,  0), (0,   1))
niwatoriKiki_2 = ((0,  -1), (1,  0), (-1,  0),(1,  1),  (-1,  1), (0,   1))
#🐘
zouKiki = ((1, 1), (1, -1), (-1, -1), (-1, 1))

komaToKiki = {"l1":lionKiki, "l2":lionKiki, "g1":kirinKiki, "g2":kirinKiki,
                "c1":hiyokoKiki_1, "c2":hiyokoKiki_2, "h1":niwatoriKiki_1, "h2":niwatoriKiki_2,
                "e1":zouKiki, "e2":zouKiki}

#着手可能な手を返す関数                
def showMoveRange(boardinfo, player):
    allTe = []

    for srcStr, komaStr in boardinfo.items():
        #駒の所有者とプレイヤーが一致していたら
        if(komaStr[1] == player):
            #持ち駒以外の処理
            if(srcStr[0] == "A" or srcStr[0] == "B" or srcStr[0] == "C"):
                Kiki = komaToKiki[komaStr]

                (srcX, srcY) = masuToXy(srcStr)

                # 各駒の動き方すべてについて
                for (deltaX, deltaY) in Kiki:
                    # 行先のマスを計算
                    dstX = srcX + deltaX
                    dstY = srcY + deltaY

                    # 行先が盤内の場合のみ考慮
                    if dstX >= 0 and dstX <= 2 and dstY >= 0 and dstY <= 3:
                        # 行先をマスを表す文字列に変換
                        dstStr = xyToMasu((dstX, dstY))
                        
                        # 盤面のディクショナリを見て、
                        # 行先に駒がないか、あるいは自分の駒ではないとき着手可能
                        if boardinfo.get(dstStr) is None or boardinfo.get(dstStr)[1] != player:
                            allTe.append((srcStr, dstStr))
            
            #持ち駒の処理
            else:
                #駒がない場所が着手可能
                for num in "1234":
                     for alpha in "ABC":
                         if boardinfo.get(alpha + num) is None:
                            allTe.append((srcStr, (alpha + num)))

    return allTe


#着手可能な手を返す関数(持ち駒を含めない)      
def boardShowMoveRange(boardinfo, player):
    allTe = []

    for srcStr, komaStr in boardinfo.items():
        #駒の所有者とプレイヤーが一致していたら
        if(komaStr[1] == player):
            #持ち駒以外の処理
            if(srcStr[0] == "A" or srcStr[0] == "B" or srcStr[0] == "C"):
                Kiki = komaToKiki[komaStr]

                (srcX, srcY) = masuToXy(srcStr)

                # 各駒の動き方すべてについて
                for (deltaX, deltaY) in Kiki:
                    # 行先のマスを計算
                    dstX = srcX + deltaX
                    dstY = srcY + deltaY

                    # 行先が盤内の場合のみ考慮
                    if dstX >= 0 and dstX <= 2 and dstY >= 0 and dstY <= 3:
                        # 行先をマスを表す文字列に変換
                        dstStr = xyToMasu((dstX, dstY))
                        
                        # 盤面のディクショナリを見て、
                        # 行先に駒がないか、あるいは自分の駒ではないとき着手可能
                        if boardinfo.get(dstStr) is None or boardinfo.get(dstStr)[1] != player:
                            allTe.append((srcStr, dstStr))

    return allTe


#一手指す関数
def itteSaki(boardinfo, te):
    newBoardinfo = boardinfo.copy()
    #プレイヤー情報
    player = newBoardinfo.get(te[0])[1]

    if(player == "1"):
        mochi = "D"
        aite = "2"
        aiteField = "1"
    elif(player == "2"):
        mochi = "E"
        aite = "1"
        aiteField = "4"

    #ひよこが相手の陣地に入ったらにわとりにする
    if(te[1][1] == aiteField and newBoardinfo.get(te[0])[0] == "c" and not(te[0][0] == mochi)):
        newBoardinfo[te[0]] = "h"+player

    #とった駒が相手の駒だったら
    if(not(newBoardinfo.get(te[1]) == None)):
        #持ち駒の空いている場所に置く
        for num in "123456":
            if(newBoardinfo.get(mochi + num) == None):
                if(not(newBoardinfo.get(te[1]) == None)):
                    #とった駒がにわとりだったら
                    if(newBoardinfo.get(te[1]) == "h"+aite): 
                        newBoardinfo[mochi + num] = "c"+player
                    else:
                        newBoardinfo[mochi + num] = newBoardinfo[te[1]][0]+player
                break

    #駒を移動させる
    newBoardinfo[te[1]] = newBoardinfo.pop(te[0])

    return newBoardinfo


# Player1 に指させて、最も良くなる手を選ぶと仮定して評価
# 評価値は Player1 の観点
def itte1_ab(kyoku, depth, alpha, beta):
    #もし負けていたら
    if(judgeWL(kyoku) == False):
        return -10000, None
   
    # 末端なら静的評価
    if depth == 0:
        return hyouka(kyoku), None

    # 末端でないなら、以降、動的評価
    # Player1 の観点なので、指させて最も良い手を選ぶと仮定して評価

    # bestTe は、最大の評価値を達成する手を記録するための変数
    bestTe = None

    for te in showMoveRange(kyoku, player):
        sennitite = False

        # 手を指したあとの局面を表す辞書を計算
        sk = itteSaki(kyoku, te)

        for senBoard in sennititeList:
            if(sk == senBoard):
                sennitite = True
                
        if sennitite != True:
            # 再帰呼び出しにより、手を指したあとの局面の評価値を計算
            tmp_alpha, tedummy = itte2_ab(sk, depth - 1, beta, alpha)
                    
            if (depth == resultDepth):
                print("al ", tmp_alpha, " te ", te)

            # 手を指したあとの局面の評価値が alpha より大きければ alpha を更新
            # かつ、その手を bestTe として記録
            if tmp_alpha > alpha:
                alpha = tmp_alpha
                bestTe = te

            if alpha >= beta:
                break

    return alpha, bestTe

# Player2 に指させて、(Player1 にとって)最も悪くなる手を選ぶと仮定して評価
# 評価値は Player1 の観点
def itte2_ab(kyoku, depth, alpha, beta):
    #もし勝っていたら
    if(judgeWL(kyoku) == True):
        return 10000 + 100*depth, None
    
    # 末端なら静的評価
    if depth == 0:
        return hyouka(kyoku), None

    # 末端でないなら、以降、動的評価
    # Player1 の観点なので、指させて最も良い手を選ぶと仮定して評価

    # bestTe は、最小の評価値を達成する手を記録するための変数
    bestTe = None

    for te in showMoveRange(kyoku, aite):
        # 手を指したあとの局面を表す辞書を計算
        sk = itteSaki(kyoku, te)

        # 再帰呼び出しにより、手を指したあとの局面の評価値を計算
        tmp_alpha, tedummy = itte1_ab(sk, depth - 1, beta, alpha)

        # 手を指したあとの局面の評価値が alpha より小さければ alpha を更新
        # かつ、その手を bestTe として記録
        if tmp_alpha < alpha:
            alpha = tmp_alpha
            bestTe = te

        if alpha <= beta:
            break

    return alpha, bestTe



#評価関数
point = {"l":0,"c":284, "e":826, "h":600, "g":1000}
def hyouka(newBoardinfo):
    hyoukaNum = 0

    #利き数
    hyoukaNum += 100*(len(boardShowMoveRange(newBoardinfo, player)) - len(boardShowMoveRange(newBoardinfo, aite)))

    #駒の点数
    for srcStr, komaStr in newBoardinfo.items():
        #自分の駒
        if(komaStr[1] == player):
            #持ち駒の時
            if(srcStr[0] == mochi):
                hyoukaNum += point.get(komaStr[0])/1.2
            #盤面にあるとき
            else:
                hyoukaNum += point.get(komaStr[0])
        #相手の駒
        elif(komaStr[1] == aite):
            #持ち駒の時
            if(srcStr[0] == aiteMochi):
                hyoukaNum -= point.get(komaStr[0])/1.2
            #盤面にあるとき
            else:
                #相手の駒がにわとりの時
                if(komaStr[0] == "h"):
                    hyoukaNum -= point.get("c") + 100
                else:
                    hyoukaNum -= point.get(komaStr[0])

        if komaStr == "l"+player and (srcStr == "A4" or srcStr =="C4"):
            hyoukaNum -= 100 

    return int(hyoukaNum)


#深さを決める
def decideDepth(boardinfo):
    #持ち駒の個数
    lenMochi = len([key for key in boardinfo.keys() if(key[0] in ["D", "E"])])

    #0の時
    if lenMochi <= 1:
        return 9-1
    #1,2の時
    elif lenMochi == 2:
        return 8-1
    #3の時
    elif lenMochi == 3:
        return 7-1
    #4以上の時
    else:
        return 6-1

#千日手判定
def sennitite(boardinfo):
    boardList.append(boardinfo)
    #2回同じ盤面が出現したら千日手リストに盤面を追加
    if(boardList.count(boardinfo) == 2):
        sennititeList.append(boardinfo)


# -------------------------------------------------------
# ここから main
# -------------------------------------------------------
msg = s.recv(BUFSIZE).rstrip().decode()
print(msg)
player = msg[14]   #先手なら1、後手なら2
count = 0

#千日手判定用変数
boardList = []
sennititeList = []

#プレイヤー情報
if(player == "1"):
    mochi = "D"
    aiteMochi = "E"
    aite = "2"
    playerField = "4"
    aiteField = "1"
elif(player == "2"):
    mochi = "E"
    aiteMochi = "D"
    aite = "1"
    playerField = "1"
    aiteField = "4"


# 無限ループ
while True:
    #自分の手番を待つ
    while True:
        s.send(("turn" + "\n").encode())
        time.sleep(0.1)
        msg = s.recv(BUFSIZE).rstrip().decode()
        if(player == msg[6]):
            break

    print("#############################################")    

    #盤面を読み取る
    boardinfo = readBoard()
    
    #勝敗判定
    result = judgeWL(boardinfo)
    if result == True:
        print("You won.")
        break
    elif result == False:
        print("You lost.")
        break

    #最善手を計算
    resultDepth = decideDepth(boardinfo)  #持ち駒の数によって深さを変える
    print("Depth:", resultDepth)

    alpha ,bestTe = itte1_ab(boardinfo, resultDepth, -50000, 50000)

    if bestTe == None:
        sennititeList = []
        alpha ,bestTe = itte1_ab(boardinfo, resultDepth, -50000, 50000)

    print("best", alpha)

    #駒を動かす
    s.send(("mv {} {}\n".format(bestTe[0], bestTe[1])).encode())

    # メッセージを受信
    msg = s.recv(BUFSIZE).rstrip().decode()
    print(msg)

    #自分が打った後の盤面を読み取る
    time.sleep(0.3)
    boardinfo = readBoard()

    #千日手判定
    sennitite(boardinfo)

print("bye")
s.close()
