from basic_q import Board, FiveElementsPiece, YinYangPiece

def test_captures():
    b = Board(7)
    
    # 初始化一些棋子
    wx = FiveElementsPiece("火", "火", "white", "fire")
    bx1 = YinYangPiece("兵", "兵", "black")
    bx2 = YinYangPiece("兵", "兵", "black")
    bx3 = YinYangPiece("兵", "兵", "black")
    bx4 = YinYangPiece("兵", "兵", "black")
    
    # 1. 测试终点吃子
    b.place_piece(wx, (0, 0))
    b.place_piece(bx1, (0, 1)) # 火的炮架
    b.place_piece(bx2, (0, 2)) # 目标敌方
    assert b.grid[0][2] == bx2
    
    # 验证能否吃到 (0,2) (因为 wx是白，bx是黑，应该能吃)
    assert wx.can_move((0, 0), (0, 2), b) == True
    assert b.execute_move((0, 0), (0, 2)) == True
    assert b.grid[0][0] is None
    assert b.grid[0][2] == wx # 黑子被火取而代之
    
    # 清理
    b.grid[0][1] = None
    b.grid[0][2] = None
    
    # 2. 测试包围吃子（气尽）
    # 中央放一个白子
    white_target = YinYangPiece("阳", "○", "white")
    b.place_piece(white_target, (3, 3))
    
    # 黑子开始包围
    b.place_piece(bx1, (2, 3))
    b.place_piece(bx2, (4, 3))
    b.place_piece(bx3, (3, 2))
    assert b.grid[3][3] == white_target # 还有1气 (3,4)
    
    # 最后一击
    b.place_piece(bx4, (3, 4))
    assert b.grid[3][3] is None # 被吃掉了！
    assert b.grid[3][4] == bx4 # 落子成功
    
    # 3. 测试自杀行为被系统允许（如果是纯自杀，自己死）
    b.place_piece(white_target, (3, 3)) # 此时四周全是黑子，白子下在 (3,3) 等于自杀
    # 验证落子后自己死了
    assert b.grid[3][3] is None
    
    print("Capture tests passed!")

if __name__ == '__main__':
    test_captures()
