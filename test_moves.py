from basic_q import Board, FiveElementsPiece, YinYangPiece

def test_moves():
    b = Board(7)
    
    metal = FiveElementsPiece("金", "金", "white", "metal")
    wood = FiveElementsPiece("木", "木", "white", "wood")
    water = FiveElementsPiece("水", "水", "white", "water")
    fire = FiveElementsPiece("火", "火", "white", "fire")
    earth = FiveElementsPiece("土", "土", "white", "earth")
    
    # 1. 测试 金 (类似车，最大步长3)
    b.place_piece(metal, (3, 3))
    # 合法: 步长1, 2, 3
    assert metal.can_move((3, 3), (3, 4), b) == True
    assert metal.can_move((3, 3), (3, 6), b) == True
    assert metal.can_move((3, 3), (1, 3), b) == True
    # 非法: 步长>3
    assert metal.can_move((3, 3), (7, 3), b) == False 
    # 非法: 非直线
    assert metal.can_move((3, 3), (4, 4), b) == False
    
    # 添加阻挡
    blocker = YinYangPiece("挡", "x", "black")
    b.place_piece(blocker, (3, 5))
    assert metal.can_move((3, 3), (3, 6), b) == False # 被阻挡
    assert metal.can_move((3, 3), (3, 4), b) == True  # 阻挡前可以
    b.grid[3][5] = None # 移除阻挡
    
    # 2. 测试 木 (马步)
    b.place_piece(wood, (3, 3))
    assert wood.can_move((3, 3), (4, 5), b) == True # 1x2
    assert wood.can_move((3, 3), (5, 2), b) == True # 2x1
    # 非法: 对角线 或 步长超标
    assert wood.can_move((3, 3), (4, 4), b) == False
    assert wood.can_move((3, 3), (3, 5), b) == False
    assert wood.can_move((3, 3), (4, 6), b) == False # 1x3, 和为4不合法
    
    # 木的阻挡测试
    b.place_piece(blocker, (3, 4)) # 挡住横向路线
    b.place_piece(blocker, (4, 3)) # 挡住纵向路线
    assert wood.can_move((3, 3), (4, 5), b) == False # 往(4,5)的两条路(先横3,4;先竖4,3)都被挡(部分)
    b.grid[3][4] = None
    b.grid[4][3] = None
    
    # 3. 测试 水
    b.place_piece(water, (3, 3))
    # 1+√2: 相邻格 (0,1)
    assert water.can_move((3, 3), (3, 4), b) == True
    # 1+√2: 马步格 (1,2)
    assert water.can_move((3, 3), (4, 5), b) == True
    # √2+√2: 距离2同轴直格 (0,2)
    assert water.can_move((3, 3), (3, 5), b) == True
    # 非法水: 对角线 或 距离3
    assert water.can_move((3, 3), (4, 4), b) == False
    assert water.can_move((3, 3), (3, 6), b) == False
    
    # 4. 测试 火 (炮跳，最大3)
    b.place_piece(fire, (3, 3))
    b.place_piece(blocker, (3, 4))
    assert fire.can_move((3, 3), (3, 5), b) == True # 跳过 blocker
    assert fire.can_move((3, 3), (3, 6), b) == True # 跳过 blocker, 步长3
    assert fire.can_move((3, 3), (3, 4), b) == False # 不能直接吃相邻
    b.place_piece(blocker, (3, 5))
    assert fire.can_move((3, 3), (3, 6), b) == False # 两个炮架不合法
    b.grid[3][4] = None
    b.grid[3][5] = None
    assert fire.can_move((3, 3), (3, 5), b) == False # 没炮架不合法
    
    # 5. 测试 土 (受限象)
    b.place_piece(earth, (3, 3))
    assert earth.can_move((3, 3), (4, 4), b) == True # 步长1
    assert earth.can_move((3, 3), (5, 5), b) == True # 步长2
    assert earth.can_move((3, 3), (6, 6), b) == False # 步长3非法
    assert earth.can_move((3, 3), (3, 4), b) == False # 直线非法
    b.place_piece(blocker, (4, 4))
    assert earth.can_move((3, 3), (5, 5), b) == False # 阻挡
    
    print("All python tests passed successfully!")

if __name__ == '__main__':
    test_moves()
