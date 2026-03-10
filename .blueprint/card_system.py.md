# card_system.py 蓝图

## Metadata
- title: card_system
- type: module
- summary: 定义卡牌基础抽象以及玩家牌库、手牌、持续效果的管理逻辑。

## 关键方法单元

### 方法单元：Card.can_use
- location: `Card.can_use()`
- purpose: 在发动卡牌前检查资源是否足够以及时机是否满足。
- input: `board, player_color`：棋盘对象与执行方颜色
- output: `tuple[bool, str]`：是否可用与失败原因
- core_steps:
  1. 检查玩家当前气值是否足以支付卡牌费用。
  2. 预留时机校验入口以衔接回合与状态规则。
  3. 返回可发动结果及对应提示信息。

### 方法单元：CardManager.initialize_decks
- location: `CardManager.initialize_decks()`
- purpose: 为双方生成内容一致但顺序打乱的初始牌库。
- input: `card_list`：作为牌库模板的卡牌列表
- output: `void`
- core_steps:
  1. 为黑白双方复制同一套卡牌模板。
  2. 分别对双方牌组进行随机打乱。
  3. 将洗好的牌组写入各自牌库状态。

### 方法单元：CardManager.draw_card
- location: `CardManager.draw_card()`
- purpose: 从指定玩家牌库顶抽取一张卡加入手牌。
- input: `player_color`：玩家颜色
- output: `Card | None`：抽到的卡牌或空值
- core_steps:
  1. 检查对应牌库是否仍有剩余卡牌。
  2. 从牌库顶部取出一张牌。
  3. 将该牌加入玩家手牌并返回结果。

### 方法单元：CardManager.use_card
- location: `CardManager.use_card()`
- purpose: 驱动一次完整的卡牌发动流程，包括校验、扣费、移除手牌和记录持续效果。
- input: `player_color, card_instance_idx, target_pos`：执行方、手牌索引与可选目标位置
- output: `tuple[bool, str]`：是否成功与结果消息
- core_steps:
  1. 校验手牌索引是否合法并读取目标卡牌。
  2. 调用卡牌可用性检查并扣除玩家气值成本。
  3. 从手牌移除卡牌、应用效果并在需要时登记持续效果。

## 变更记录
- 2026-03-09: 初始化卡牌系统蓝图，记录牌库、手牌与卡牌发动主流程。
