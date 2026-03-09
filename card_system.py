import enum

class CardTiming(enum.IntEnum):
    """卡牌使用时机"""
    ACTIVE = 1    # 己方回合使用
    COUNTER = 2   # 对方回合使用 (反制)
    INSTANT = 3   # 全回合通用的即时效果

class CardDuration(enum.IntEnum):
    """卡牌效果持续时间"""
    INSTANT = 1   # 一次性
    TURN = 2      # 持续本回合
    PERMANENT = 3 # 永久有效

class Card:
    """卡牌基类"""
    def __init__(self, card_id, name, cost, timing, duration):
        self.card_id = card_id
        self.name = name
        self.cost = cost  # 消耗的玩家气 (Vitality)
        self.timing = timing
        self.duration = duration

    def can_use(self, board, player_color):
        """检查卡牌是否可以使用 (时机与资源校验)"""
        # 1. 资源校验
        if board.player_vitality[player_color] <= self.cost:
            return False, "气值不足"
        
        # 2. 时机校验 (在此处可以增加基于 board.turn_count 或状态的逻辑)
        # TODO: 接入 Board 类的当前轮序判断
        
        return True, ""

    def apply_effect(self, board, player_color, target_pos=None):
        """执行卡牌效果，子类需重写此方法"""
        raise NotImplementedError("子类必须实现此方法以操作 Board")

class CardManager:
    """卡牌管理器，负责每个玩家独立的卡牌库、手牌及执行逻辑"""
    def __init__(self, board):
        self.board = board
        # 针对每个玩家独立存储
        self.player_decks = {'black': [], 'white': []}  # 牌库
        self.player_hands = {'black': [], 'white': []}  # 手牌
        self.active_effects = [] # 存储持续性效果

    def initialize_decks(self, card_list):
        """为双方初始化完全相同的牌组"""
        import random
        # 保持公平，但打乱顺序 (种子也可以同步)
        for color in ['black', 'white']:
            deck = card_list[:]
            random.shuffle(deck)
            self.player_decks[color] = deck

    def draw_card(self, player_color):
        """从对应玩家的牌库抽一张牌到手牌"""
        if self.player_decks[player_color]:
            card = self.player_decks[player_color].pop(0)
            self.player_hands[player_color].append(card)
            return card
        return None

    def use_card(self, player_color, card_instance_idx, target_pos=None):
        """使用手牌中索引为 card_instance_idx 的卡牌"""
        if card_instance_idx >= len(self.player_hands[player_color]):
            return False, "非法的手牌索引"

        card = self.player_hands[player_color][card_instance_idx]
        
        success, msg = card.can_use(self.board, player_color)
        if not success:
            return False, msg

        # 1. 扣除代价
        self.board.player_vitality[player_color] -= card.cost
        
        # 2. 从手牌移除
        self.player_hands[player_color].pop(card_instance_idx)
        
        # 3. 应用效果
        card.apply_effect(self.board, player_color, target_pos)
        
        # 4. 处理持续性逻辑
        if card.duration != CardDuration.INSTANT:
            self.active_effects.append({
                'card_obj': card,
                'player': player_color,
                'duration': card.duration,
                'start_turn': self.board.turn_count
            })
            
        return True, f"成功发动卡牌: {card.name}"
