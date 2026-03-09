import socketio
import eventlet
from flask import Flask
from flask_cors import CORS
import json

# 创建 Socket.IO 服务器
sio = socketio.Server(cors_allowed_origins='*')
app = Flask(__name__)
# 包装 Flask 应用
app = socketio.WSGIApp(sio, app)

# 存储游戏房间状态
# rooms = { room_id: { "players": {"black": sid, "white": sid}, "board_state": ... } }
rooms = {}

@sio.event
def connect(sid, environ):
    print(f"Player connected: {sid}")

@sio.event
def disconnect(sid, *args):
    print(f"Player disconnected: {sid}")
    # 清理房间信息
    for room_id, room in list(rooms.items()):
        if sid in room['players'].values():
            # 找到对应的角色并移除
            roles_to_remove = [role for role, psid in room['players'].items() if psid == sid]
            for role in roles_to_remove:
                del room['players'][role]
            
            # 通知房间内剩余玩家
            sio.emit('player_disconnected', room=room_id)
            print(f"Notified room {room_id} about player departure")

@sio.on('join_room')
def on_join(sid, data):
    room_id = data.get('room_id')
    player_type = data.get('player_type') # 'black' or 'white'
    
    if not room_id or player_type not in ['black', 'white']:
        return {"status": "error", "message": "Invalid join data"}

    if room_id not in rooms:
        rooms[room_id] = {
            "players": {},
            "state": None # 这里可以存储序列化后的 Board 对象
        }
    
    # 检查位置是否已被占用
    if player_type in rooms[room_id]['players']:
        if rooms[room_id]['players'][player_type] != sid:
            return {"status": "error", "message": f"{player_type} already taken"}
    
    rooms[room_id]['players'][player_type] = sid
    sio.enter_room(sid, room_id)
    
    print(f"Player {sid} joined room {room_id} as {player_type}")
    
    # 如果两名玩家都到齐了，由服务器生成统一的初始化棋盘并发送
    if len(rooms[room_id]['players']) == 2:
        import random
        cols = list(range(9))
        
        # 统一生成黑白双方的位置
        black_cols = random.sample(cols, 5)
        white_cols = random.sample(cols, 5)
        
        # 这里只给模板，具体的 symbol 由客户端根据 type 自行渲染，保持协议精简
        init_data = {
            "black_positions": black_cols,
            "white_positions": white_cols,
            "templates": ['metal', 'wood', 'water', 'fire', 'earth']
        }
        
        sio.emit('init_game', init_data, room=room_id)
        print(f"Game initialized in room {room_id}")
    
    return {"status": "success", "room_id": room_id}

@sio.on('action')
def on_action(sid, data):
    """
    处理玩家动作 (move, drop, reveal)
    data格式: { "room_id": "...", "action_type": "...", "payload": { ... } }
    """
    room_id = data.get('room_id')
    if room_id not in rooms:
        return {"status": "error", "message": "Room not found"}
    
    # 广播这个动作给房间内的所有人（包括发送者，以便同步）
    sio.emit('sync_action', data, room=room_id)
    print(f"Action in room {room_id}: {data['action_type']}")

if __name__ == '__main__':
    print("Starting Five Elements Chess Server on port 5000...")
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
