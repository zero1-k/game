# server.py 蓝图

## Metadata
- title: server
- type: service
- summary: 提供五行卡棋联机房间管理、玩家配对与动作广播服务。

## 关键方法单元

### 方法单元：on_join
- location: `on_join()`
- purpose: 处理玩家加入房间与阵营占位，并在双方就绪后下发统一初始化布局。
- input: `sid, data`：连接标识与包含房间号、玩家阵营的请求数据
- output: `dict`：加入结果与错误信息
- core_steps:
  1. 校验房间号与阵营字段是否合法。
  2. 创建或更新房间玩家映射并让连接进入房间。
  3. 当双方都已就位时随机生成初始布局并广播开局数据。

### 方法单元：on_action
- location: `on_action()`
- purpose: 接收客户端动作消息并把动作广播给房间内其他客户端进行同步。
- input: `sid, data`：连接标识与动作数据
- output: `dict | None`：错误结果或空值
- core_steps:
  1. 校验目标房间是否存在。
  2. 读取动作类型与动作载荷。
  3. 将动作广播给房间内全部玩家以保持状态一致。

### 方法单元：disconnect
- location: `disconnect()`
- purpose: 处理玩家断线后的房间清理与剩余玩家通知。
- input: `sid, *args`：断线连接标识与附加参数
- output: `void`
- core_steps:
  1. 扫描房间映射并定位断线玩家所在房间。
  2. 从房间玩家列表中移除该连接对应角色。
  3. 向房间内剩余玩家广播断线事件。

## 变更记录
- 2026-03-09: 初始化联机服务蓝图，记录入房、同步与断线清理主流程。
