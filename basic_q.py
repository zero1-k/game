class Piece:
    """棋子基础类"""
    def __init__(self, name, symbol, color, internal_energy=0):
        self.name = name
        self.symbol = symbol
        self.color = color  # 'black' or 'white'
        self.internal_energy = internal_energy

    def can_move(self, start_pos, end_pos, board):
        """定义棋子是否可以从 start_pos 移动到 end_pos"""
        raise NotImplementedError("子类必须实现此方法")

class YinYangPiece(Piece):
    """阴阳棋子：只能落子，且只能横纵向移动1格，不能吃子"""
    def can_move(self, start_pos, end_pos, board):
        x1, y1 = start_pos
        x2, y2 = end_pos
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        # 只能横纵向移动一格
        if dx + dy == 1:
            # 终点不能有棋子（不能吃子）
            if hasattr(board, 'grid'):
                if board.grid[x2][y2] is not None:
                    return False
            return True
        return False

# 五行关系映射
# 相生：木->火->土->金->水->木
GENERA = {'wood': 'fire', 'fire': 'earth', 'earth': 'metal', 'metal': 'water', 'water': 'wood'}
# 相克：木->土->水->火->金->木
OVERCOMES = {'wood': 'earth', 'earth': 'water', 'water': 'fire', 'fire': 'metal', 'metal': 'wood'}
# 初始内气映射
INIT_ENERGY = {'water': 5, 'wood': 4, 'earth': 4, 'fire': 3, 'metal': 3, 'yin': 1, 'yang': 1}

class FiveElementsPiece(Piece):
    """五行棋子：根据元素类型有不同的移动规则"""
    def __init__(self, name, symbol, color, element, internal_energy=0):
        super().__init__(name, symbol, color, internal_energy)
        self.element = element  # 'metal', 'wood', 'water', 'fire', 'earth'

    def can_move(self, start_pos, end_pos, board):
        # 0. 实时内气获取与移动力检查
        current_energy = board.get_calculated_energy(*start_pos)
        # 【水系特殊限制】水内气 <= 2 无法移动，其他五行 <= 1 无法移动
        threshold = 2 if self.element == 'water' else 1
        if current_energy <= threshold:
            return False

        x1, y1 = start_pos
        x2, y2 = end_pos
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)

        # 检查目标位置是否有棋子
        target_piece = board.grid[x2][y2]

            # 【墙壁化修复】未揭开的棋子视为障碍物（墙），不可作为终点攻击
            if not target_piece.is_revealed and not getattr(target_piece, 'element', None) is None:
                # 只有五行棋子有 is_revealed 状态且会被遮蔽，阴阳棋子通常是直接落下的
                pass 
            
            # 这里的 target_piece 如果是未揭开的 FiveElementsPiece，直接返回 False
            if isinstance(target_piece, FiveElementsPiece) and not target_piece.is_revealed:
                return False
                
            # 阴阳棋子、克制、同名、母食子、无关属性均为后续逻辑判定
        
        # 2. 几何位移规则校验 (复用原有逻辑)
        if dx == 0 and dy == 0:
            return False

        # 辅助函数：获取两点之间的所有整数坐标点（不含起点和终点）
        def get_path_points(r1, c1, r2, c2):
            points = []
            steps = max(abs(r2 - r1), abs(c2 - c1))
            if steps == 0: return points
            step_r = (r2 - r1) // steps
            step_c = (c2 - c1) // steps
            for i in range(1, steps):
                points.append((r1 + i * step_r, c1 + i * step_c))
            return points

        # 辅助函数：判断给定点集上是否有棋子
        def is_path_clear(points):
            # 注意：基本版的 board 我们假设它传入的是一个支持 grid[r][c] 或拥有坐标读取能力的对象。
            # 这里按照二维数组 grid[x][y] 或者提供 get_piece(x, y) 检查
            for p_x, p_y in points:
                if hasattr(board, 'grid'):
                    if board.grid[p_x][p_y] is not None:
                        return False
            return True

        if self.element == 'metal':  # 金：水平或垂直移动，最大步长3，无阻挡
            if (dx == 0 and dy > 0) or (dy == 0 and dx > 0):
                if max(dx, dy) <= 3:
                    path = get_path_points(x1, y1, x2, y2)
                    return is_path_clear(path)
            return False
        
        elif self.element == 'wood':   # 木：L形移动，横纵绝对位移之和最大为3，路线上无阻挡
            # L形意味着 dx > 0, dy > 0 
            if dx > 0 and dy > 0 and (dx + dy) <= 3:
                # 检查两条折线路径是否有一条为空
                # 路径A: 先横后竖
                corner_a = (x2, y1)
                path_a1 = get_path_points(x1, y1, corner_a[0], corner_a[1])
                path_a2 = get_path_points(corner_a[0], corner_a[1], x2, y2)
                # 拐角点 corner_a 本身也必须为空
                is_corner_a_empty = (not hasattr(board, 'grid')) or (board.grid[corner_a[0]][corner_a[1]] is None)
                if is_corner_a_empty and is_path_clear(path_a1) and is_path_clear(path_a2):
                    return True
                
                # 路径B: 先竖后横
                corner_b = (x1, y2)
                path_b1 = get_path_points(x1, y1, corner_b[0], corner_b[1])
                path_b2 = get_path_points(corner_b[0], corner_b[1], x2, y2)
                is_corner_b_empty = (not hasattr(board, 'grid')) or (board.grid[corner_b[0]][corner_b[1]] is None)
                if is_corner_b_empty and is_path_clear(path_b1) and is_path_clear(path_b2):
                    return True
            return False
        
        elif self.element == 'water':
            # 水的折线判定：要么是 1+√2 的组合，要么是 √2+√2 的组合
            for cx in range(getattr(board, 'size', 7)):
                for cy in range(getattr(board, 'size', 7)):
                    dx1, dy1 = abs(cx - x1), abs(cy - y1)
                    dx2, dy2 = abs(x2 - cx), abs(y2 - cy)
                    
                    is_p1_1 = (dx1 + dy1 == 1)
                    is_p1_sqrt2 = (dx1 == 1 and dy1 == 1)
                    
                    is_p2_1 = (dx2 + dy2 == 1)
                    is_p2_sqrt2 = (dx2 == 1 and dy2 == 1)
                    
                    # 满足 1+√2 或 √2+√2 的折线组合
                    if (is_p1_1 and is_p2_sqrt2) or \
                       (is_p1_sqrt2 and is_p2_1) or \
                       (is_p1_sqrt2 and is_p2_sqrt2):
                        
                        # 折线要求三点不能在一条直线上
                        is_collinear = (cx - x1) * (y2 - cy) == (cy - y1) * (x2 - cx)
                        if not is_collinear:
                            # 判断该路径上的折点是否为空（折点上不能存在棋子）
                            if not hasattr(board, 'grid') or board.grid[cx][cy] is None:
                                return True
            return False
        
        elif self.element == 'fire':   # 火：1.短平移（距离1） 2.纯跳跃（距离2-3，且必须跳过一个棋子）
            if (dx == 0 and dy > 0) or (dy == 0 and dx > 0):
                dist = max(dx, dy)
                if dist == 1:
                    return True  # 允许1步直线平移
                elif 2 <= dist <= 3:
                    path = get_path_points(x1, y1, x2, y2)
                    # 路径上必须有且仅有一个棋子
                    pieces_in_path = 0
                    if hasattr(board, 'grid'):
                        for p_x, p_y in path:
                            if board.grid[p_x][p_y] is not None:
                                pieces_in_path += 1
                    return pieces_in_path == 1
            return False
        
        elif self.element == 'earth':  # 土：对角线移动，最大步长2，不可越子
            if dx > 0 and dx == dy:
                if dx <= 2:
                    path = get_path_points(x1, y1, x2, y2)
                    return is_path_clear(path)
            return False
        
        return False

# 示例棋子定义
# 示例棋子定义 (内气：水5, 木土4, 火金3, 阴阳1)
yin_piece = YinYangPiece("阴", "☯", "black", internal_energy=1)
yang_piece = YinYangPiece("阳", "○", "white", internal_energy=1)

metal_piece = FiveElementsPiece("金", "金", "white", "metal", internal_energy=3)
wood_piece = FiveElementsPiece("木", "木", "white", "wood", internal_energy=4)
water_piece = FiveElementsPiece("水", "水", "white", "water", internal_energy=5)
fire_piece = FiveElementsPiece("火", "火", "white", "fire", internal_energy=3)
earth_piece = FiveElementsPiece("土", "土", "white", "earth", internal_energy=4)
class Board:
    """9x9 棋盘类"""
    def __init__(self, size=9):
        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.player_vitality = {'black': 20, 'white': 20}
        self.turn_count = 1  # 初始第 1 回合
        # 开荒期动作计数：前10回合(20步)必须执行 5次揭开 (reveal) 和 5次落子 (drop)
        self.player_action_counts = {
            'black': {'reveal': 0, 'drop': 0},
            'white': {'reveal': 0, 'drop': 0}
        }
        # 【卡牌系统接入】
        from card_system import CardManager
        self.card_manager = CardManager(self)

    def handle_card_action(self, player_color, card_id, target_pos=None):
        """处理卡牌动作的入口接口"""
        return self.card_manager.use_card(player_color, card_id, target_pos)

    def place_piece(self, piece, pos):
        """落子，并触发落子后的吃子结算"""
        x, y = pos
        if 0 <= x < self.size and 0 <= y < self.size:
            # 【5+5配额检查】前10回合(20步)落子不能超过5次
            if self.turn_count <= 20: 
                if self.player_action_counts[piece.color]['drop'] >= 5:
                    return False
                # 【中线限制】前10回合落子不能超过中线 (9x9 中线是行 4)
                # 黑方(通常认为起始在上方或小行号区) vs 白方
                # 根据之前 server.py，黑方初始在 row 0, 白方在 row 8
                if piece.color == 'black' and x > 4:
                    return False
                if piece.color == 'white' and x < 4:
                    return False

            # 如果是落子（并非移动），要求目标点原本为空
            if self.grid[x][y] is not None:
                return False
            self.grid[x][y] = piece
            self.resolve_captures(x, y, piece.color) # 结算落子方的气
            self.player_action_counts[piece.color]['drop'] += 1
            self.turn_count += 1
            return True
        return False

    def reveal_piece(self, pos, mover_color):
        """揭开棋子，并触发由于通透性消失导致的提子结算"""
        x, y = pos
        piece = self.grid[x][y]
        if piece and isinstance(piece, FiveElementsPiece) and not getattr(piece, 'is_revealed', True):
            # 【5+5配额检查】前10回合揭开不能超过5次
            if self.turn_count <= 20:
                if self.player_action_counts[mover_color]['reveal'] >= 5:
                    return False

            piece.is_revealed = True
            self.player_action_counts[mover_color]['reveal'] += 1
            # 【逻辑联动修正】揭开后从“通透体”变回“实体”，可能导致邻近棋子气数归零，必须结算提子
            self.resolve_captures(x, y, mover_color)
            self.turn_count += 1
            return True
        return False

    def get_calculated_energy(self, x, y):
        """实时计算 (x, y) 处棋子的内气 (基础值 + 邻域场效)"""
        p = self.grid[x][y]
        if not p: return 0
        init = INIT_ENERGY.get(getattr(p, 'element', 'yin' if p.color=='black' else 'yang'), p.internal_energy)
        if isinstance(p, YinYangPiece): return init

        delta = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                nb = self.grid[nx][ny]
                if not nb: continue
                
                # 【墙壁化修复】未翻开的棋子不参与周边的生克贡献
                is_revealed = getattr(nb, 'is_revealed', True)
                if not is_revealed:
                    continue
                
                # 阴阳效应
                if isinstance(nb, YinYangPiece):
                    if nb.color == p.color: delta += 1
                    else: delta -= 1
                elif nb.color == p.color:
                    # 生我者增 (nb 生 p)
                    if GENERA.get(nb.element) == p.element: delta += 1
                else:
                    # 克我者减 (nb 克 p)
                    if OVERCOMES.get(nb.element) == p.element: delta -= 1
        
        # 限制 +/- 4
        return max(init - 4, min(init + 4, init + delta))

    def execute_move(self, start_pos, end_pos):
        """执行合法移动，并触发终点吃和包围吃子结算"""
        x1, y1 = start_pos
        x2, y2 = end_pos
        piece = self.grid[x1][y1]
        if not piece: return False
        
        # 1. 终点攻击结算
        attacker_energy = self.get_calculated_energy(x1, y1)
        target_piece = self.grid[x2][y2]
        if target_piece:
            defender_color = target_piece.color
            defender_energy = self.get_calculated_energy(x2, y2)
            
            # 基础惩罚：仅当五行棋子失去时扣除玩家气值
            if isinstance(target_piece, FiveElementsPiece):
                lost_vitality = INIT_ENERGY.get(target_piece.element, 1)
                self.player_vitality[defender_color] -= lost_vitality

            # 战斗动态伤害 (仅限五行 vs 五行)
            if isinstance(piece, FiveElementsPiece) and isinstance(target_piece, FiveElementsPiece):
                a_type = piece.element
                b_type = target_piece.element
                
                # 克制或同名产生的差值伤害
                if OVERCOMES.get(a_type) == b_type or a_type == b_type:
                    if attacker_energy > defender_energy:
                        self.player_vitality[defender_color] -= (attacker_energy - defender_energy)
                    elif a_type == b_type and defender_energy > attacker_energy:
                        self.player_vitality[piece.color] -= (defender_energy - attacker_energy)

        # 移动执行
        self.grid[x2][y2] = piece
        self.grid[x1][y1] = None
        
        # 2. 包围结算
        self.resolve_captures(x2, y2, piece.color)
        
        # 回合自增 (假设每次 execute_move 代表一个玩家操作完成)
        self.turn_count += 1
        return True

    def get_connected_group(self, x, y):
        """获取与 (x, y) 处棋子相连的同色棋子块 (混合连通)"""
        piece = self.grid[x][y]
        if not piece: return set()
        color = getattr(piece, 'color', None)
        
        group = set()
        visited = set()
        queue = [(x, y)]
        
        while queue:
            curr_x, curr_y = queue.pop(0)
            if (curr_x, curr_y) in visited: continue
            visited.add((curr_x, curr_y))
            group.add((curr_x, curr_y))
            
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = curr_x + dx, curr_y + dy
                if 0 <= nx < self.size and 0 <= ny < self.size:
                    neighbor = self.grid[nx][ny]
                    if neighbor and getattr(neighbor, 'color', None) == color:
                        # 【墙壁化修复】未揭开的棋子不参与连通
                        is_revealed = getattr(neighbor, 'is_revealed', True)
                        if is_revealed and (nx, ny) not in visited:
                            queue.append((nx, ny))
        return group

    def count_liberties(self, group):
        """计算一个棋块组合的共同气数 (支持隐藏棋子透气逻辑)"""
        liberties = set()
        checked_hidden = set()
        
        # 初始队列包含所有已知棋块的邻居
        queue = []
        for x, y in group:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                queue.append((x + dx, y + dy))
        
        while queue:
            curr_x, curr_y = queue.pop(0)
            if not (0 <= curr_x < self.size and 0 <= curr_y < self.size):
                continue
                
            target = self.grid[curr_x][curr_y]
            if target is None:
                # 找到空位气
                liberties.add((curr_x, curr_y))
            else:
                # 检查是否为未揭开的棋子 (独立透气)
                is_hidden = isinstance(target, FiveElementsPiece) and not target.is_revealed
                if is_hidden:
                    # 【通透体修正】未揭开格位本身计入气位，同时继续传导气路
                    liberties.add((curr_x, curr_y))
                    if (curr_x, curr_y) not in checked_hidden:
                        checked_hidden.add((curr_x, curr_y))
                        # 向四周扩散寻找更远的气位
                        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            queue.append((curr_x + dx, curr_y + dy))
                            
        return len(liberties)

    def resolve_captures(self, moved_x, moved_y, mover_color):
        """全局提子结算"""
        captured_any = False
        opponent_color = 'white' if mover_color == 'black' else 'black'
        
        # 1. 扫描所有敌方受威胁的块
        processed_groups = set()
        to_capture = []
        
        for r in range(self.size):
            for c in range(self.size):
                p = self.grid[r][c]
                if p and getattr(p, 'color', None) == opponent_color:
                    # 排除墙壁
                    if getattr(p, 'is_revealed', True) and (r, c) not in processed_groups:
                        group = self.get_connected_group(r, c)
                        for cell in group: processed_groups.add(cell)
                        if self.count_liberties(group) == 0:
                            to_capture.append(group)
        
        # 2. 执行提子 (敌方优先)
        if to_capture:
            for group in to_capture:
                for x, y in group:
                    p = self.grid[x][y]
                    if p:
                        # 提子惩罚 (五行棋扣血)
                        is_yin_yang = isinstance(p, YinYangPiece) or (getattr(p, 'element', None) is None)
                        if not is_yin_yang:
                            loss = INIT_ENERGY.get(p.element, 1)
                            self.player_vitality[p.color] -= loss
                        self.grid[x][y] = None
            captured_any = True
            
        # 3. 检查落子方自杀
        my_group = self.get_connected_group(moved_x, moved_y)
        if my_group and self.count_liberties(my_group) == 0:
            for x, y in my_group:
                p = self.grid[x][y]
                if p:
                    is_yin_yang = isinstance(p, YinYangPiece) or (getattr(p, 'element', None) is None)
                    if not is_yin_yang:
                        loss = INIT_ENERGY.get(p.element, 1)
                        self.player_vitality[p.color] -= loss
                    self.grid[x][y] = None
            captured_any = True
            
        return captured_any

    def check_game_over(self):
        """检查是否有玩家气值低于 10"""
        if self.player_vitality['black'] < 10: return 'white'
        if self.player_vitality['white'] < 10: return 'black'
        return None

    def display(self):
        """打印连续线条的围棋风格 7x7 棋盘"""
        # ANSI 颜色
        RESET = "\033[0m"
        BOLD = "\033[1m"
        FG_BOARD = "\033[38;2;160;120;60m"
        FG_COORD = "\033[38;2;150;150;150m"
        COLORS = {
            'black': "\033[38;5;232m", 'white': "\033[38;5;255m",
            'metal': "\033[38;5;251m", 'wood': "\033[38;5;34m",
            'water': "\033[38;5;33m", 'fire': "\033[38;5;196m", 'earth': "\033[38;5;94m",
        }
        # 棋盘符号：使用单字符交点，水平线增广以对接
        SYMBOLS = {
            'top_left': '┌', 'top_right': '┐', 'bottom_left': '└', 'bottom_right': '┘',
            'top': '┬', 'bottom': '┴', 'left': '├', 'right': '┤', 'cross': '┼',
            'line_h': '──', 'line_v': '│'
        }

        def get_intersection_symbol(r, c):
            if r == 0:
                if c == 0: return SYMBOLS['top_left']
                if c == self.size - 1: return SYMBOLS['top_right']
                return SYMBOLS['top']
            if r == self.size - 1:
                if c == 0: return SYMBOLS['bottom_left']
                if c == self.size - 1: return SYMBOLS['bottom_right']
                return SYMBOLS['bottom']
            if c == 0: return SYMBOLS['left']
            if c == self.size - 1: return SYMBOLS['right']
            return SYMBOLS['cross']

        # 打印顶部坐标 (每个单元格由 1个交点 + 2个水平线 组成，共 3 字符宽)
        coord_line = "    " + "  ".join([str(i) for i in range(self.size)])
        print(f"\n{FG_COORD}{coord_line}{RESET}")

        for r in range(self.size):
            # 1. 打印带棋子的行
            row_str = f"{FG_COORD} {r} {RESET}"
            for c in range(self.size):
                piece = self.grid[r][c]
                if piece:
                    # 棋子通常占用 2 个字符宽度
                    p_color = COLORS.get(getattr(piece, 'element_type', piece.color), COLORS['white'])
                    symbol = f"{p_color}{BOLD}{piece.symbol}{RESET}"
                else:
                    # 交叉点由于是 1 宽，补一个空格使其成为 2 宽，且避免与线断开
                    symbol = f"{FG_BOARD}{get_intersection_symbol(r, c)}{RESET} "
                
                row_str += symbol
                # 如果不是最后一列，添加水平连接线
                if c < self.size - 1:
                    row_str += f"{FG_BOARD}{SYMBOLS['line_h']}{RESET}"
            print(row_str)

            # 2. 打印行间的垂直连接线
            if r < self.size - 1:
                # 垂直线对齐交点，后面跟 3 个空格 (1空+2线)
                v_line = "    " + f"{FG_BOARD}{SYMBOLS['line_v']}{RESET}   " * self.size
                print(v_line)
        print("")
