from flask import Flask, render_template, request, jsonify, Response, stream_with_context
from dotenv import load_dotenv
import os
import sys
import time
from agents.debater import Debater
import locale
import json

# 设置默认编码为UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stdin.encoding != 'utf-8':
    sys.stdin.reconfigure(encoding='utf-8')

# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONLEGACYWINDOWSFSENCODING'] = 'utf-8'

# 设置本地化编码
try:
    locale.setlocale(locale.LC_ALL, '.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, '')
    except:
        pass

app = Flask(__name__)
load_dotenv()

# 配置
DEFAULT_CONFIG = {
    "rounds": 3,
    "delay": 1,
    "model": "deepseek-chat",
    "encoding": "utf-8",
    "api_base": "https://api.deepseek.com/v1"
}

# 确保API基础URL正确设置
if 'DEEPSEEK_API_BASE' not in os.environ:
    os.environ['DEEPSEEK_API_BASE'] = DEFAULT_CONFIG["api_base"]

def get_api_key():
    """获取API密钥"""
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        raise ValueError("未找到DEEPSEEK_API_KEY环境变量")
    return api_key

def create_debater(name, position, api_key, model):
    """创建辩论者实例"""
    try:
        return Debater(
            name=name,
            system_prompt=f"""你是一位专业的辩手，支持{name}观点。请使用逻辑和事实来{position}。保持专业和礼貌。请用中文回复。

请使用Markdown格式来组织你的回应，这将使你的观点更加清晰：
- 使用**粗体**强调重要观点
- 使用*斜体*表示特殊概念
- 使用标题（# ## ###）组织层次结构
- 使用列表（有序或无序）呈现多个论点
- 使用>引用重要的事实或数据
- 在必要时使用表格整理对比信息
- 适当使用分隔线（---）分隔不同部分

总之，利用Markdown格式让你的辩论更有条理、更有说服力。""",
            api_key=api_key,
            model=model
        )
    except Exception as e:
        raise Exception(f"创建辩手 {name} 时发生错误：{str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/debate', methods=['POST'])
def debate():
    try:
        data = request.json
        topic = data.get('topic')
        rounds = data.get('rounds', DEFAULT_CONFIG["rounds"])
        stream = data.get('stream', False)  # 添加流式参数支持
        
        if not topic:
            return jsonify({'error': '请提供辩论主题'}), 400
            
        # 如果请求流式输出，但通过普通API调用，则返回错误
        if stream:
            return jsonify({'error': '流式输出请使用 /api/debate/stream 端点'}), 400

        api_key = get_api_key()
        debater_1 = create_debater("正方", "支持", api_key, DEFAULT_CONFIG["model"])
        debater_2 = create_debater("反方", "反对", api_key, DEFAULT_CONFIG["model"])

        debate_history = []
        current_message = topic

        # 多轮辩论
        for round in range(rounds):
            # 正方发言
            try:
                response_1 = debater_1.generate_response(current_message)
                debate_history.append({
                    'round': round + 1,
                    'side': '正方',
                    'content': response_1
                })
                time.sleep(DEFAULT_CONFIG["delay"])
            except Exception as e:
                return jsonify({'error': f'正方发言时发生错误：{str(e)}'}), 500

            # 反方发言
            try:
                response_2 = debater_2.generate_response(response_1)
                debate_history.append({
                    'round': round + 1,
                    'side': '反方',
                    'content': response_2
                })
                time.sleep(DEFAULT_CONFIG["delay"])
            except Exception as e:
                return jsonify({'error': f'反方发言时发生错误：{str(e)}'}), 500

            current_message = response_2

        return jsonify({
            'topic': topic,
            'rounds': rounds,
            'debate_history': debate_history
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/debate/init', methods=['POST'])
def init_debate():
    """初始化辩论设置"""
    try:
        data = request.json
        topic = data.get('topic')
        rounds = data.get('rounds', DEFAULT_CONFIG["rounds"])
        
        if not topic:
            return jsonify({'error': '请提供辩论主题'}), 400
            
        # 验证API密钥可用
        api_key = get_api_key()
        
        return jsonify({
            'status': 'success',
            'message': '辩论初始化成功',
            'topic': topic,
            'rounds': rounds
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'message': '初始化辩论失败'}), 500

@app.route('/api/debate/stream')
def stream_debate():
    """流式辩论接口"""
    topic = request.args.get('topic')
    rounds = int(request.args.get('rounds', DEFAULT_CONFIG["rounds"]))
    
    if not topic:
        return jsonify({'error': '请提供辩论主题'}), 400
    
    def generate():
        try:
            api_key = get_api_key()
            positive_debater = create_debater("正方", "支持", api_key, DEFAULT_CONFIG["model"])
            negative_debater = create_debater("反方", "反对", api_key, DEFAULT_CONFIG["model"])
            
            # 初始消息为辩论主题
            current_message = topic
            
            # 多轮辩论
            for round_num in range(1, rounds + 1):
                # 正方流式回应
                full_positive_response = ""
                for chunk in positive_debater.get_response(current_message, stream=True):
                    full_positive_response += chunk
                    yield f'data: {json.dumps({"type": "content", "round": round_num, "side": "正方", "content": full_positive_response})}\n\n'
                    time.sleep(0.05)  # 控制输出速度，避免前端刷新过快
                
                # 更新当前消息为正方回应
                current_message = full_positive_response
                
                # 反方流式回应
                full_negative_response = ""
                for chunk in negative_debater.get_response(current_message, stream=True):
                    full_negative_response += chunk
                    yield f'data: {json.dumps({"type": "content", "round": round_num, "side": "反方", "content": full_negative_response})}\n\n'
                    time.sleep(0.05)  # 控制输出速度
                
                # 更新当前消息为反方回应
                current_message = full_negative_response
            
            # 辩论完成
            yield f'event: debate_complete\ndata: {json.dumps({"type": "complete", "message": "辩论已完成"})}\n\n'
            
        except Exception as e:
            error_msg = str(e)
            print(f"流式辩论错误: {error_msg}")
            yield f'event: error\ndata: {json.dumps({"type": "error", "message": error_msg})}\n\n'
            yield f'event: debate_complete\ndata: {json.dumps({"type": "complete", "message": "辩论因错误而终止"})}\n\n'
    
    # 返回流式响应
    return Response(stream_with_context(generate()), mimetype="text/event-stream")

if __name__ == '__main__':
    app.run(debug=True) 