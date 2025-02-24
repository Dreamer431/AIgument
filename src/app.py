from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import sys
import time
from agents.debater import Debater
import locale

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
            system_prompt=f"你是一位专业的辩手，支持{name}观点。请使用逻辑和事实来{position}。保持专业和礼貌。请用中文回复。",
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
        
        if not topic:
            return jsonify({'error': '请提供辩论主题'}), 400

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

if __name__ == '__main__':
    app.run(debug=True) 