from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO, emit

import logging
from flask import request, jsonify
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

dialogue = []


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('update_dialogue', dialogue, broadcast=False)


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@app.route('/add_message', methods=['POST'])
def add_message():
    try:
        # 记录请求数据
        logger.info("Received request to add message.")
        data = request.json
        logger.info(f"Request data: {data}")

        # 检查必要字段
        if not data or 'role' not in data or 'content' not in data:
            logger.error("Invalid request data: missing 'role' or 'content'")
            return jsonify({"status": "error", "message": "Missing 'role' or 'content' in request"}), 400   

        # 构造消息对象
        message = {
            'role': data.get('role'),
            'content': data.get('content'),
            'start_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # 记录当前时间
            'end_time': "",
            'audio_file': "",
            'tts_file': "",
            'vad_status': ""
        }
        logger.info(f"Constructed message: {message}")

        # 将消息添加到对话列表
        dialogue.append(message)
        logger.info(f"Added message to dialogue. Total messages: {len(dialogue)}")

        # 推送更新到客户端
        socketio.emit('update_dialogue', dialogue)
        logger.info("Emitted 'update_dialogue' event to clients.")

        # 返回成功响应
        return jsonify({"status": "success"}), 200

    except Exception as e:
        # 捕获并记录异常
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500
    


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0',port= 5000, debug=True, allow_unsafe_werkzeug=True)
