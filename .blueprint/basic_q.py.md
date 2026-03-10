# basic_q.py 蓝图

## Metadata
- title: basic_q
- type: module
- summary: 定义五行卡棋的棋子模型、棋盘状态、移动规则、内气计算与提子结算。

## 关键方法单元

### 方法单元：FiveElementsPiece.can_move
- location: `FiveElementsPiece.can_move()`
- purpose: 判定五行棋子在当前棋盘状态下是否可以按自身属性规则移动或攻击到目标位置。
- input: `start_pos, end_pos, board`：起点坐标、终点坐标、棋盘对象
- output: `bool`：是否允许该次移动
- core_steps:
  1. 读取起点棋子的实时内气并校验是否满足机动阈值。
  2. 根据目标位置占用情况与隐藏状态判断是否允许作为攻击目标。
  3. 按五行属性分别套用金木水火土的几何位移与路径阻挡规则。

### 方法单元：Board.place_piece
- location: `Board.place_piece()`
- purpose: 处理落子动作，并在落子后触发提子结算与阶段计数更新。
- input: `piece, pos`：待落下的棋子对象与目标坐标
- output: `bool`：落子是否成功
- core_steps:
  1. 校验位置是否合法、开荒期配额是否超限以及是否越过中线。
  2. 将棋子放入目标格位并拒绝覆盖已有棋子。
  3. 触发提子结算、更新动作计数并推进回合数。

### 方法单元：Board.reveal_piece
- location: `Board.reveal_piece()`
- purpose: 处理隐藏五行棋子的翻开动作，并在翻开后重新结算通透性变化造成的提子。
- input: `pos, mover_color`：翻开位置与执行方颜色
- output: `bool`：翻开是否成功
- core_steps:
  1. 校验目标棋子是否为未翻开的五行棋且当前配额允许揭开。
  2. 将棋子状态改为已揭开并记录揭开次数。
  3. 重新执行提子结算并推进回合。

### 方法单元：Board.get_calculated_energy
- location: `Board.get_calculated_energy()`
- purpose: 实时计算指定棋子的内气，用于移动资格、战斗伤害与界面展示。
- input: `x, y`：棋盘坐标
- output: `int`：当前位置棋子的实时内气值
- core_steps:
  1. 获取棋子的基础内气或阴阳固定内气。
  2. 扫描上下左右邻位，按阴阳场效、相生与相克规则累计修正值。
  3. 将结果限制在基础值上下四点波动范围内。

### 方法单元：Board.execute_move
- location: `Board.execute_move()`
- purpose: 执行一次合法位移或终点攻击，并在动作后完成战斗与提子结算。
- input: `start_pos, end_pos`：移动起点与终点坐标
- output: `bool`：移动是否执行成功
- core_steps:
  1. 读取攻击方与目标方棋子及其动态内气。
  2. 若终点有棋子则先结算基础战损与差值伤害。
  3. 更新棋盘位置，执行提子结算并推进回合。

### 方法单元：Board.resolve_captures
- location: `Board.resolve_captures()`
- purpose: 在落子、翻开或移动后，统一结算敌方被围困棋块与己方自杀棋块的移除和气值损失。
- input: `moved_x, moved_y, mover_color`：最后动作位置与行动方颜色
- output: `bool`：本次是否发生提子
- core_steps:
  1. 扫描敌方已揭开棋块并找出共同气数为零的目标。
  2. 先执行敌方提子并扣除对应五行棋的玩家气。
  3. 再检查行动方是否形成自杀并按相同规则移除。

## 变更记录
- 2026-03-09: 初始化规则引擎蓝图，记录棋子移动、内气与提子结算的核心结构。
