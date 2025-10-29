from flask import Flask, render_template, request, jsonify, Response, stream_with_context, send_from_directory, g
from flask_caching import Cache
from dotenv import load_dotenv
import os
import sys
import time
from agents.debater import Debater
import locale
import json
from flask_cors import CORS
from datetime import datetime, timedelta
from models import db, Session, Message
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, func
from functools import wraps
from performance import before_request, after_request, performance_monitor
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
CORS(app)
load_dotenv()

# 配置缓存
cache = Cache(app, config={
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300  # 5分钟缓存
})

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

# 数据库配置
# 确保instance目录存在
instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "instance")
os.makedirs(instance_dir, exist_ok=True)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(instance_dir, "aigument.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}

# 初始化数据库
db.init_app(app)

# 注册性能监控钩子
app.before_request(before_request)
app.after_request(after_request)

# 创建数据库表
with app.app_context():
    print("正在创建数据库表...")
    try:
        db.create_all()
        print("数据库表创建成功！")
        # 检查表是否存在
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"当前数据库中的表：{tables}")
    except Exception as e:
        print(f"创建数据库表时发生错误：{str(e)}")
        raise

def safe_error_message(error, default_message="操作失败"):
    """
    安全地格式化错误消息，避免在生产环境泄露敏感信息
    
    Args:
        error: 异常对象
        default_message: 默认错误消息
        
    Returns:
        安全的错误消息字符串
    """
    # 在开发环境返回详细错误，生产环境返回通用消息
    if app.debug:
        return str(error)
    
    # 对于已知的安全错误类型，可以返回消息
    if isinstance(error, (ValueError, TypeError)):
        return str(error)
    
    # 其他错误只返回通用消息，并记录到日志
    logger.error(f"Error occurred: {str(error)}", exc_info=True)
    return default_message

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

def validate_input(data, required_fields, optional_fields=None):
    """验证输入数据
    
    Args:
        data: 输入数据字典
        required_fields: 必需字段字典 {field_name: (type, max_length)}
        optional_fields: 可选字段字典 {field_name: (type, max_length, default)}
    
    Returns:
        验证并清理后的数据字典
        
    Raises:
        ValueError: 验证失败时抛出
    """
    if optional_fields is None:
        optional_fields = {}
    
    result = {}
    
    # 检查必需字段
    for field, (field_type, max_length) in required_fields.items():
        if field not in data or data[field] is None:
            raise ValueError(f"缺少必需字段: {field}")
        
        value = data[field]
        
        # 类型检查
        if not isinstance(value, field_type):
            raise ValueError(f"字段 {field} 类型错误，期望 {field_type.__name__}")
        
        # 长度检查（针对字符串）
        if field_type == str and max_length and len(value) > max_length:
            raise ValueError(f"字段 {field} 超过最大长度 {max_length}")
        
        # 字符串去除首尾空格
        if field_type == str:
            value = value.strip()
            if not value:
                raise ValueError(f"字段 {field} 不能为空")
        
        result[field] = value
    
    # 处理可选字段
    for field, (field_type, max_length, default) in optional_fields.items():
        value = data.get(field, default)
        
        if value is not None:
            # 类型检查
            if not isinstance(value, field_type):
                value = default
            
            # 长度检查（针对字符串）
            if field_type == str and max_length and len(value) > max_length:
                value = value[:max_length]
            
            # 字符串去除首尾空格
            if field_type == str and value:
                value = value.strip()
        
        result[field] = value
    
    return result

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

@app.route('/history')
def history():
    return render_template('history.html')

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
        
        # 验证输入
        validated = validate_input(
            data,
            required_fields={
                'topic': (str, 500)
            },
            optional_fields={
                'rounds': (int, None, DEFAULT_CONFIG["rounds"]),
                'stream': (bool, None, False),
                'provider': (str, 50, DEFAULT_CONFIG["provider"]),
                'model': (str, 100, DEFAULT_CONFIG["model"])
            }
        )
        
        topic = validated['topic']
        rounds = validated['rounds']
        stream = validated['stream']
        provider = validated['provider']
        model = validated['model']
        
        # 验证轮次范围
        if not 1 <= rounds <= 10:
            return jsonify({'error': '辩论轮次必须在1-10之间'}), 400
        
        # 如果请求流式输出，但通过普通API调用，则返回错误
        if stream:
            return jsonify({'error': '流式输出请使用 /api/debate/stream 端点'}), 400

        print(f"开始新的辩论，主题：{topic}")
        
        # 创建新的会话记录
        session = Session(
            session_type='debate',
            topic=topic,
            settings={
                'rounds': rounds,
                'provider': provider,
                'model': model
            }
        )
        db.session.add(session)
        db.session.commit()
        print(f"创建新会话成功，ID：{session.id}")

        api_key = get_api_key(provider)
        debater_1 = create_debater("正方", "支持", provider, model, api_key)
        debater_2 = create_debater("反方", "反对", provider, model, api_key)

        debate_history = []
        current_message = topic

        # 保存主题消息
        topic_message = Message(
            session_id=session.id,
            role='topic',
            content=topic,
            meta_info={
                'round': 0,
                'provider': provider,
                'model': model
            }
        )
        db.session.add(topic_message)
        print("保存主题消息成功")

        # 多轮辩论
        for round in range(rounds):
            print(f"开始第 {round + 1} 轮辩论")
            
            # 正方发言
            try:
                response_1 = debater_1.generate_response(current_message)
                print(f"正方生成回应成功，长度：{len(response_1)}")
                
                debate_history.append({
                    'round': round + 1,
                    'side': '正方',
                    'content': response_1
                })
                
                # 保存正方消息
                message_1 = Message(
                    session_id=session.id,
                    role='正方',
                    content=response_1,
                    meta_info={
                        'round': round + 1,
                        'provider': provider,
                        'model': model
                    }
                )
                db.session.add(message_1)
                print("保存正方消息成功")
                
                time.sleep(DEFAULT_CONFIG["delay"])
            except Exception as e:
                print(f"正方发言时发生错误：{str(e)}")
                return jsonify({'error': f'正方发言时发生错误：{str(e)}'}), 500

            # 反方发言
            try:
                response_2 = debater_2.generate_response(response_1)
                print(f"反方生成回应成功，长度：{len(response_2)}")
                
                debate_history.append({
                    'round': round + 1,
                    'side': '反方',
                    'content': response_2
                })
                
                # 保存反方消息
                message_2 = Message(
                    session_id=session.id,
                    role='反方',
                    content=response_2,
                    meta_info={
                        'round': round + 1,
                        'provider': provider,
                        'model': model
                    }
                )
                db.session.add(message_2)
                print("保存反方消息成功")
                
                time.sleep(DEFAULT_CONFIG["delay"])
            except Exception as e:
                print(f"反方发言时发生错误：{str(e)}")
                return jsonify({'error': f'反方发言时发生错误：{str(e)}'}), 500

            current_message = response_2

        # 提交所有数据库更改
        db.session.commit()
        print("所有消息保存成功")

        return jsonify({
            'topic': topic,
            'rounds': rounds,
            'debate_history': debate_history,
            'session_id': session.id
        })

    except Exception as e:
        print(f"辩论过程中发生错误：{str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/debate/init', methods=['POST'])
def init_debate():
    """初始化辩论并创建会话记录"""
    try:
        data = request.get_json()
        
        # 验证输入
        validated = validate_input(
            data,
            required_fields={
                'topic': (str, 500)
            },
            optional_fields={
                'rounds': (int, None, 3),
                'provider': (str, 50, 'deepseek'),
                'model': (str, 100, 'deepseek-chat')
            }
        )
        
        topic = validated['topic']
        rounds = validated['rounds']
        provider = validated['provider']
        model = validated['model']
        
        # 验证轮次范围
        if not 1 <= rounds <= 10:
            return jsonify({'error': '辩论轮次必须在1-10之间'}), 400
        
        # 创建新的会话记录
        session = Session(
            session_type='debate',
            topic=topic,
            settings={
                'rounds': rounds,
                'provider': provider,
                'model': model
            }
        )
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'session_id': session.id,
            'topic': topic,
            'rounds': rounds
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"初始化辩论错误: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': safe_error_message(e, '初始化辩论失败')}), 500

@app.route('/api/debate/stream')
def stream_debate():
    """流式辩论接口"""
    try:
        topic = request.args.get('topic', '').strip()
        
        if not topic:
            return jsonify({'error': '请提供辩论主题'}), 400
        
        if len(topic) > 500:
            return jsonify({'error': '主题长度不能超过500个字符'}), 400
        
        try:
            rounds = int(request.args.get('rounds', DEFAULT_CONFIG["rounds"]))
            if not 1 <= rounds <= 10:
                return jsonify({'error': '辩论轮次必须在1-10之间'}), 400
        except ValueError:
            return jsonify({'error': '轮次必须是有效的整数'}), 400
        
        provider = request.args.get('provider', DEFAULT_CONFIG["provider"])[:50]
        model = request.args.get('model', DEFAULT_CONFIG["model"])[:100]
        
    except Exception as e:
        logger.error(f"参数验证失败: {str(e)}", exc_info=True)
        return jsonify({'error': '参数验证失败，请检查输入参数'}), 400
    
    def generate():
        try:
            # 创建新的会话记录
            session = Session(
                session_type='debate',
                topic=topic,
                settings={
                    'rounds': rounds,
                    'provider': provider,
                    'model': model
                }
            )
            db.session.add(session)
            db.session.commit()
            print(f"创建新会话成功，ID：{session.id}")
            
            # 保存主题消息
            topic_message = Message(
                session_id=session.id,
                role='topic',
                content=topic,
                meta_info={
                    'round': 0,
                    'provider': provider,
                    'model': model
                }
            )
            db.session.add(topic_message)
            db.session.commit()
            print("保存主题消息成功")
            
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
                
                # 保存正方消息
                message_1 = Message(
                    session_id=session.id,
                    role='正方',
                    content=full_positive_response,
                    meta_info={
                        'round': round_num,
                        'provider': provider,
                        'model': model
                    }
                )
                db.session.add(message_1)
                db.session.commit()
                print(f"保存第 {round_num} 轮正方消息成功")
                
                # 更新当前消息为正方回应
                current_message = full_positive_response
                
                # 反方流式回应
                full_negative_response = ""
                for chunk in negative_debater.get_response(current_message, stream=True):
                    full_negative_response += chunk
                    yield f'data: {json.dumps({"type": "content", "round": round_num, "side": "反方", "content": full_negative_response})}\n\n'
                    time.sleep(0.05)  # 控制输出速度
                
                # 保存反方消息
                message_2 = Message(
                    session_id=session.id,
                    role='反方',
                    content=full_negative_response,
                    meta_info={
                        'round': round_num,
                        'provider': provider,
                        'model': model
                    }
                )
                db.session.add(message_2)
                db.session.commit()
                print(f"保存第 {round_num} 轮反方消息成功")
                
                # 更新当前消息为反方回应
                current_message = full_negative_response
            
            # 辩论完成
            yield f'event: debate_complete\ndata: {json.dumps({"type": "complete", "message": "辩论已完成"})}\n\n'
            
        except Exception as e:
            error_msg = str(e)
            print(f"流式辩论错误: {error_msg}")
            yield f'event: error\ndata: {json.dumps({"type": "error", "message": error_msg})}\n\n'
            yield f'event: debate_complete\ndata: {json.dumps({"type": "complete", "message": "辩论因错误而终止"})}\n\n'
            if 'session' in locals():
                db.session.rollback()
    
    # 返回流式响应
    return Response(stream_with_context(generate()), mimetype="text/event-stream")

@app.route('/api/debate/single', methods=['POST'])
def single_debate():
    """单次辩论接口，用于逐步生成辩论内容"""
    try:
        data = request.json
        
        # 验证输入
        validated = validate_input(
            data,
            required_fields={
                'topic': (str, 2000),
                'side': (str, 10)
            },
            optional_fields={
                'round': (int, None, 1),
                'provider': (str, 50, DEFAULT_CONFIG["provider"]),
                'model': (str, 100, DEFAULT_CONFIG["model"]),
                'session_id': (int, None, None)
            }
        )
        
        topic = validated['topic']
        side = validated['side']
        round_num = validated['round']
        provider = validated['provider']
        model = validated['model']
        session_id = validated['session_id']
        
        # 验证参数
        if side not in ['正方', '反方']:
            return jsonify({'error': '辩论方必须为"正方"或"反方"'}), 400
        
        if not 1 <= round_num <= 10:
            return jsonify({'error': '轮次必须在1-10之间'}), 400
            
        api_key = get_api_key(provider)
        
        # 根据辩论方创建辩论者
        if side == '正方':
            debater = create_debater("正方", "支持", provider, model, api_key)
        else:
            debater = create_debater("反方", "反对", provider, model, api_key)
            
        # 生成回应
        response_content = debater.generate_response(topic)
        
        # 保存消息到数据库
        if session_id:
            message = Message(
                session_id=session_id,
                role=side,
                content=response_content,
                meta_info={
                    'round': round_num,
                    'provider': provider,
                    'model': model
                }
            )
            db.session.add(message)
            db.session.commit()
        
        # 返回生成的内容
        return jsonify({
            'side': side,
            'round': round_num,
            'content': response_content,
        })
        
    except Exception as e:
        print(f"单次辩论错误: {str(e)}")
        return jsonify({'error': f'{side}生成回应时发生错误：{str(e)}'}), 500

# 新增：会话管理API
@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """获取会话列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    session_type = request.args.get('type')
    
    query = Session.query
    if session_type:
        query = query.filter_by(session_type=session_type)
    
    sessions = query.order_by(Session.updated_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'total': sessions.total,
        'pages': sessions.pages,
        'current_page': sessions.page,
        'sessions': [session.to_dict() for session in sessions.items]
    })

@app.route('/api/sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    """获取单个会话详情"""
    session = Session.query.get_or_404(session_id)
    return jsonify(session.to_dict())

@app.route('/api/sessions/<int:session_id>/export', methods=['GET'])
def export_session(session_id):
    """导出会话内容"""
    session = Session.query.get_or_404(session_id)
    format_type = request.args.get('format', 'json')
    
    if format_type == 'json':
        return jsonify(session.to_dict())
    elif format_type == 'markdown':
        # 生成Markdown格式
        markdown_content = f"# {session.topic}\n\n"
        markdown_content += f"会话类型: {session.session_type}\n"
        markdown_content += f"创建时间: {session.created_at}\n\n"
        
        for msg in session.messages:
            markdown_content += f"## {msg.role}\n\n{msg.content}\n\n"
        
        return Response(
            markdown_content,
            mimetype='text/markdown',
            headers={"Content-disposition": f"attachment; filename=session_{session_id}.md"}
        )
    else:
        return jsonify({"error": "Unsupported format"}), 400

@app.route('/api/history')
@cache.cached(timeout=60, query_string=True)  # 缓存1分钟
def get_history():
    try:
        print("正在获取历史记录...")
        # 获取类型参数
        session_type = request.args.get('type', 'all')
        print(f"请求的会话类型: {session_type}")
        
        # 验证session_type
        valid_types = ['all', 'debate', 'chat', 'qa']
        if session_type not in valid_types:
            return jsonify({'error': f'无效的会话类型，必须是 {", ".join(valid_types)} 之一'}), 400
        
        # 构建查询
        query = Session.query
        if session_type and session_type != 'all':
            query = query.filter_by(session_type=session_type)
            
        # 执行查询（避免N+1：一次性统计消息数）- 优化：使用子查询
        sessions = query.order_by(Session.created_at.desc()).limit(100).all()
        print(f"查询到 {len(sessions)} 个会话")

        if not sessions:
            return jsonify({'history': []})

        session_ids = [s.id for s in sessions]
        counts_map = {}
        if session_ids:
            counts = db.session.query(Message.session_id, func.count(Message.id)) \
                .filter(Message.session_id.in_(session_ids)) \
                .group_by(Message.session_id).all()
            counts_map = {sid: cnt for sid, cnt in counts}

        history = []
        for session in sessions:
            message_count = counts_map.get(session.id, 0)
            history.append({
                'session_id': session.id,
                'topic': session.topic,
                'start_time': session.created_at.isoformat(),
                'message_count': message_count,
                'type': session.session_type
            })
        
        print(f"返回 {len(history)} 条历史记录")
        return jsonify({'history': history})
        
    except Exception as e:
        print(f"获取历史记录错误: {str(e)}")
        return jsonify({'error': f'获取历史记录时发生错误：{str(e)}'}), 500

@app.route('/api/history/<session_id>')
@cache.cached(timeout=120, query_string=True)  # 缓存2分钟
def get_session_detail(session_id):
    """获取特定会话的详细记录"""
    try:
        # 验证session_id
        try:
            session_id = int(session_id)
        except ValueError:
            return jsonify({'error': '无效的会话ID'}), 400
        
        print(f"正在获取会话 {session_id} 的详情...")
        
        # 使用join优化查询
        messages = Message.query.filter_by(
            session_id=session_id
        ).order_by(Message.created_at).all()
        
        if not messages:
            # 检查会话是否存在
            session = Session.query.get(session_id)
            if not session:
                return jsonify({'error': '会话不存在'}), 404
        
        print(f"查询到 {len(messages)} 条消息")
        return jsonify({
            'session_id': session_id,
            'messages': [msg.to_dict() for msg in messages]
        })
        
    except Exception as e:
        print(f"获取会话详情错误: {str(e)}")
        return jsonify({'error': f'获取会话详情时发生错误：{str(e)}'}), 500

@app.route('/api/history/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    try:
        # 验证session_id
        try:
            session_id = int(session_id)
        except ValueError:
            return jsonify({'success': False, 'message': '无效的会话ID'}), 400
        
        print(f"正在删除会话 {session_id}...")
        # 先删除该会话的所有消息
        Message.query.filter_by(session_id=session_id).delete()
        # 再删除会话本身
        session = Session.query.get(session_id)
        if session:
            db.session.delete(session)
            db.session.commit()
            
            # 清除缓存
            cache.clear()
            
            print(f"会话 {session_id} 删除成功")
            return jsonify({'success': True, 'message': '删除成功'})
        else:
            print(f"未找到会话 {session_id}")
            return jsonify({'success': False, 'message': '会话不存在'}), 404
    except Exception as e:
        print(f"删除会话失败: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

@app.route('/api/history/<session_id>/export')
def export_history_session(session_id):
    try:
        # 验证session_id
        try:
            session_id = int(session_id)
        except ValueError:
            return jsonify({'error': '无效的会话ID'}), 400
        
        print(f"正在导出会话 {session_id}...")
        format_type = request.args.get('format', 'json').lower()
        
        # 验证format参数
        if format_type not in ['json', 'markdown']:
            return jsonify({'error': '不支持的导出格式，仅支持 json 或 markdown'}), 400
        
        # 获取会话和消息
        session = Session.query.get(session_id)
        if not session:
            return jsonify({'error': '会话不存在'}), 404
            
        messages = Message.query.filter_by(session_id=session_id).order_by(Message.created_at).all()
        
        if format_type == 'json':
            # 构建 JSON 格式的数据
            data = {
                'session_id': session.id,
                'topic': session.topic,
                'session_type': session.session_type,
                'start_time': session.created_at.isoformat(),
                'messages': [{
                    'role': msg.role,
                    'content': msg.content,
                    'created_at': msg.created_at.isoformat()
                } for msg in messages]
            }
            return jsonify(data)
            
        elif format_type == 'markdown':
            # 构建 Markdown 格式的内容
            markdown_content = f"# {session.topic}\n\n"
            markdown_content += f"会话ID: {session.id}\n"
            markdown_content += f"会话类型: {session.session_type}\n"
            markdown_content += f"开始时间: {session.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            for msg in messages:
                markdown_content += f"## {msg.role}\n\n"
                markdown_content += f"{msg.content}\n\n"
                markdown_content += f"时间: {msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                markdown_content += "---\n\n"
            
            return Response(
                markdown_content,
                mimetype='text/markdown',
                headers={
                    'Content-Disposition': f'attachment; filename=session_{session_id}.md'
                }
            )
            
    except Exception as e:
        print(f"导出会话失败: {str(e)}")
        return jsonify({'error': f'导出失败: {str(e)}'}), 500

@app.route('/api/stats')
def get_stats():
    """获取性能统计信息"""
    try:
        stats = performance_monitor.get_stats()
        return jsonify({
            'performance': stats,
            'cache_info': {
                'type': app.config.get('CACHE_TYPE', 'SimpleCache'),
                'timeout': app.config.get('CACHE_DEFAULT_TIMEOUT', 300)
            },
            'database': {
                'pool_size': app.config['SQLALCHEMY_ENGINE_OPTIONS']['pool_size'],
                'pool_recycle': app.config['SQLALCHEMY_ENGINE_OPTIONS']['pool_recycle']
            }
        })
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}", exc_info=True)
        return jsonify({'error': safe_error_message(e, '获取统计信息失败')}), 500

if __name__ == '__main__':
    app.run(debug=True) 