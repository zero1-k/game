# game.html 蓝图

## Metadata
- title: game
- type: module
- summary: 提供五行卡棋的主界面、前端对局逻辑、卡牌交互与联机同步能力。

## 关键方法单元

### 方法单元：joinRoom
- location: `joinRoom()`
- purpose: 建立与联机服务器的连接并加入指定房间与阵营。
- input: `无`：从界面读取房间号与玩家阵营
- output: `void`
- core_steps:
  1. 读取用户输入的房间号与黑白阵营。
  2. 建立 Socket.IO 连接并注册联机事件回调。
  3. 向服务端发送入房请求并在成功后记录本地联机身份。

### 方法单元：handleRemoteAction
- location: `handleRemoteAction()`
- purpose: 接收服务端广播的远端动作并把本地棋盘同步到相同状态。
- input: `data`：包含动作类型与动作载荷的同步消息
- output: `Promise<void>`
- core_steps:
  1. 解析动作类型与所需参数。
  2. 根据落子、移动、揭开等动作更新本地状态。
  3. 在同步后重绘棋盘和相关界面信息。

### 方法单元：canMove
- location: `canMove()`
- purpose: 在前端侧复刻棋子移动规则，用于交互校验与可行动作提示。
- input: `p, from, to`：棋子数据、起点坐标、终点坐标
- output: `boolean`：该移动是否允许
- core_steps:
  1. 读取棋子实时内气并判断是否达到移动门槛。
  2. 根据终点目标、隐藏状态与卡牌强化效果构造规则上下文。
  3. 按棋子属性应用对应的路径与几何规则得出结果。

### 方法单元：selectIntersection
- location: `selectIntersection()`
- purpose: 统一处理玩家点击棋盘交点后的落子、翻牌、移动与卡牌选点行为。
- input: `r, c`：被点击交点的行列坐标
- output: `void`
- core_steps:
  1. 判断当前是否处于卡牌选目标、储备落子或选中棋子后的行动状态。
  2. 根据阶段规则执行落子、揭开或移动逻辑。
  3. 在动作完成后刷新棋盘、状态提示并按需上报联机动作。

### 方法单元：renderBoard
- location: `renderBoard()`
- purpose: 根据当前棋盘状态重新生成全部交点与棋子视觉表现。
- input: `无`
- output: `void`
- core_steps:
  1. 清空棋盘容器并按尺寸遍历所有交点。
  2. 为每个交点附加状态样式、点击行为与棋子元素。
  3. 将实时内气、隐藏态与危险态等视觉信息渲染到界面上。

### 方法单元：resolveCaptures
- location: `resolveCaptures()`
- purpose: 在前端侧结算包围提子与自杀，用于单机对局和界面即时反馈。
- input: `movedR, movedC, moverColor`：最后动作位置与行动方颜色
- output: `boolean`：是否有棋子被提走
- core_steps:
  1. 扫描敌方棋块并找出共同气数为零的目标。
  2. 执行敌方提子并扣减对应玩家气值。
  3. 检查行动方自杀情况并同步移除己方无气棋块。

### 方法单元：useSelectedCard
- location: `useSelectedCard()`
- purpose: 处理当前选中卡牌的实际发动流程，包括代价扣除、目标校验与远端同步。
- input: `targetPos, options`：可选目标坐标与额外执行参数
- output: `Promise<void>`
- core_steps:
  1. 读取当前选中卡牌与执行方信息并校验目标是否合法。
  2. 结算卡牌费用、移除手牌并调用具体效果执行逻辑。
  3. 更新手牌区、场地区、棋盘状态并按需发送联机同步消息。

### 方法单元：applyCardEffect
- location: `applyCardEffect()`
- purpose: 根据卡牌类型修改棋盘、牌库、手牌、持续效果与行动限制。
- input: `card, color, targetPos, remotePayload, wzsyCost`：卡牌对象、执行方、目标坐标与附加参数
- output: `Promise<object|null>`：用于远端同步的效果载荷或空值
- core_steps:
  1. 根据卡牌标识分发到不同效果分支。
  2. 修改玩家牌库、手牌、持续效果或目标棋子状态。
  3. 返回需要广播的效果结果并刷新卡牌相关界面。

## 变更记录
- 2026-03-09: 初始化前端主入口蓝图，记录对局流程、联机同步与卡牌交互核心结构。
