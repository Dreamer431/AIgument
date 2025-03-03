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

app = Flask(__name__, 
            static_folder='static',  # 设置静态文件夹的路径
            static_url_path='/static')  # 设置静态文件URL前缀
load_dotenv()

# 配置
DEFAULT_CONFIG = {
    "rounds": 3,
    "delay": 1,
    "provider": "deepseek",
    "model": "deepseek-chat",
    "encoding": "utf-8",
    "api_base": "https://api.deepseek.com/v1"
}

# 确保API基础URL正确设置
if 'DEEPSEEK_API_BASE' not in os.environ:
    os.environ['DEEPSEEK_API_BASE'] = DEFAULT_CONFIG["api_base"]

def get_api_key(provider="deepseek"):
    """获取API密钥"""
    if provider == "deepseek":
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            raise ValueError("未找到DEEPSEEK_API_KEY环境变量")
    elif provider == "openai":
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("未找到OPENAI_API_KEY环境变量")
    else:
        raise ValueError(f"不支持的提供商: {provider}")
    
    return api_key

def create_debater(name, position, provider, model, api_key):
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
            provider=provider,
            model=model,
            api_key=api_key
        )
    except Exception as e:
        raise Exception(f"创建辩手 {name} 时发生错误：{str(e)}")

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

# 添加一个路由以便在开发过程中重新加载静态文件
@app.route('/static/<path:filename>')
def serve_static(filename):
    """提供静态文件的路由，用于开发过程中防止缓存问题"""
    response = app.send_static_file(filename)
    # 添加no-cache头，防止浏览器缓存
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/debate', methods=['POST'])
def debate():
    try:
        data = request.json
        topic = data.get('topic')
        rounds = data.get('rounds', DEFAULT_CONFIG["rounds"])
        stream = data.get('stream', False)  # 添加流式参数支持
        provider = data.get('provider', DEFAULT_CONFIG["provider"])  # 新增参数
        model = data.get('model', DEFAULT_CONFIG["model"])  # 新增参数
        
        if not topic:
            return jsonify({'error': '请提供辩论主题'}), 400
            
        # 如果请求流式输出，但通过普通API调用，则返回错误
        if stream:
            return jsonify({'error': '流式输出请使用 /api/debate/stream 端点'}), 400

        api_key = get_api_key(provider)
        debater_1 = create_debater("正方", "支持", provider, model, api_key)
        debater_2 = create_debater("反方", "反对", provider, model, api_key)

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
        provider = data.get('provider', DEFAULT_CONFIG["provider"])  # 新增
        model = data.get('model', DEFAULT_CONFIG["model"])  # 新增
        
        if not topic:
            return jsonify({'error': '请提供辩论主题'}), 400
            
        # 验证API密钥可用
        api_key = get_api_key(provider)
        
        return jsonify({
            'status': 'success',
            'message': '辩论初始化成功',
            'topic': topic,
            'rounds': rounds,
            'provider': provider,
            'model': model
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'message': '初始化辩论失败'}), 500

@app.route('/api/debate/stream')
def stream_debate():
    """流式辩论接口"""
    topic = request.args.get('topic')
    rounds = int(request.args.get('rounds', DEFAULT_CONFIG["rounds"]))
    provider = request.args.get('provider', DEFAULT_CONFIG["provider"])  # 新增
    model = request.args.get('model', DEFAULT_CONFIG["model"])  # 新增
    
    if not topic:
        return jsonify({'error': '请提供辩论主题'}), 400
    
    def generate():
        try:
            api_key = get_api_key(provider)
            positive_debater = create_debater("正方", "支持", provider, model, api_key)
            negative_debater = create_debater("反方", "反对", provider, model, api_key)
            
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

@app.route('/api/debate/single', methods=['POST'])
def single_debate():
    """单次辩论接口，用于逐步生成辩论内容"""
    try:
        data = request.json
        topic = data.get('topic')  # 当前的辩论主题或上一轮的回应
        side = data.get('side')    # 正方或反方
        round_num = data.get('round', 1)  # 当前轮次
        provider = data.get('provider', DEFAULT_CONFIG["provider"])  # 新增
        model = data.get('model', DEFAULT_CONFIG["model"])  # 新增
        
        if not topic or not side:
            return jsonify({'error': '请提供辩论主题和辩论方'}), 400
            
        # 验证参数
        if side not in ['正方', '反方']:
            return jsonify({'error': '辩论方必须为"正方"或"反方"'}), 400
            
        api_key = get_api_key(provider)
        
        # 根据辩论方创建辩论者
        if side == '正方':
            debater = create_debater("正方", "支持", provider, model, api_key)
        else:
            debater = create_debater("反方", "反对", provider, model, api_key)
            
        # 生成回应
        response_content = debater.generate_response(topic)
        
        # 返回生成的内容
        return jsonify({
            'side': side,
            'round': round_num,
            'content': response_content,
        })
        
    except Exception as e:
        print(f"单次辩论错误: {str(e)}")
        return jsonify({'error': f'{side}生成回应时发生错误：{str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True) 