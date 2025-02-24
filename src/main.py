from dotenv import load_dotenv
import os
import sys
from typing import Optional
import time
from rich.console import Console
from rich.panel import Panel
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
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 设置本地化编码
try:
    locale.setlocale(locale.LC_ALL, '.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, '')
    except:
        pass

load_dotenv()  # 加载.env文件中的环境变量

from agents.debater import Debater

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

console = Console(force_terminal=True)

def get_api_key() -> str:
    """获取API密钥"""
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        console.print("[red]错误：未找到DEEPSEEK_API_KEY环境变量[/red]")
        console.print("请在.env文件中设置DEEPSEEK_API_KEY=你的DeepSeek API密钥")
        sys.exit(1)
    return api_key

def safe_print(text: str, **kwargs) -> None:
    """安全打印函数，处理编码问题"""
    try:
        console.print(text, **kwargs)
    except UnicodeEncodeError as e:
        fallback_text = text.encode(DEFAULT_CONFIG["encoding"], errors='ignore').decode(DEFAULT_CONFIG["encoding"])
        console.print(fallback_text, **kwargs)

def create_debater(name: str, position: str, api_key: str, model: str) -> Optional[Debater]:
    """创建辩论者实例"""
    try:
        return Debater(
            name=name,
            system_prompt=f"你是一位专业的辩手，支持{position}观点。请使用逻辑和事实来{position}。保持专业和礼貌。请用中文回复。",
            api_key=api_key,
            model=model
        )
    except Exception as e:
        safe_print(f"[red]创建辩手 {name} 时发生错误：{str(e)}[/red]")
        return None

def display_response(response: str, title: str, style: str) -> None:
    """显示辩论回应"""
    try:
        safe_print(Panel(response, title=title, border_style=style))
    except Exception as e:
        safe_print(f"[red]显示回应时发生错误：{str(e)}[/red]")

def main():
    # 获取API密钥
    api_key = get_api_key()
    
    # 创建两个辩论者
    debater_1 = create_debater("正方", "支持", api_key, DEFAULT_CONFIG["model"])
    debater_2 = create_debater("反方", "反对", api_key, DEFAULT_CONFIG["model"])
    
    if not (debater_1 and debater_2):
        return
    
    # 设置辩论主题
    topic = "人工智能是否会取代人类工作？"
    current_message = topic
    
    # 显示辩论主题
    safe_print(Panel(f"辩论主题：{topic}", title="AI辩论赛", border_style="blue"))
    
    # 开始辩论
    try:
        for round in range(DEFAULT_CONFIG["rounds"]):
            safe_print(f"\n[bold blue]--- 第{round + 1}轮辩论 ---[/bold blue]")
            
            # 正方发言
            try:
                response_1 = debater_1.generate_response(current_message)
                display_response(response_1, "正方观点", "green")
                time.sleep(DEFAULT_CONFIG["delay"])
            except Exception as e:
                safe_print(f"[red]正方发言时发生错误：{str(e)}[/red]")
                if isinstance(e, UnicodeEncodeError):
                    safe_print("[yellow]提示：这可能是由于终端编码设置导致的问题。请尝试在运行前设置环境变量：set PYTHONIOENCODING=utf8[/yellow]")
                continue
            
            # 反方发言
            try:
                response_2 = debater_2.generate_response(response_1)
                display_response(response_2, "反方观点", "red")
                time.sleep(DEFAULT_CONFIG["delay"])
            except Exception as e:
                safe_print(f"[red]反方发言时发生错误：{str(e)}[/red]")
                if isinstance(e, UnicodeEncodeError):
                    safe_print("[yellow]提示：这可能是由于终端编码设置导致的问题。请尝试在运行前设置环境变量：set PYTHONIOENCODING=utf8[/yellow]")
                continue
            
            current_message = response_2
            
    except KeyboardInterrupt:
        safe_print("\n[yellow]辩论被用户中断[/yellow]")
    except Exception as e:
        safe_print(f"\n[red]辩论过程中发生错误：{str(e)}[/red]")
    finally:
        safe_print("\n[bold blue]辩论结束[/bold blue]")

if __name__ == "__main__":
    main() 