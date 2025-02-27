from typing import List, Dict, Generator, Union
from openai import OpenAI
import os

class Debater:
    def __init__(self, name: str, system_prompt: str, model: str = "deepseek-chat", api_key: str = None):
        """
        初始化辩论者
        :param name: 辩论者名称（正方/反方）
        :param system_prompt: 系统提示词，定义辩论者的立场
        :param model: 使用的模型名称
        :param api_key: API密钥
        """
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.conversation_history: List[Dict] = []
        
        # 打印初始化信息
        print(f"\n=== 初始化 {name} ===")
        print(f"Model: {model}")
        print(f"API Key: {'已设置' if api_key else '未设置'}")
        
        # 初始化API客户端
        try:
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com/v1"
            )
        except Exception as e:
            print(f"初始化错误：{str(e)}")
            raise

    def generate_response(self, opponent_message: str) -> str:
        """
        生成对辩论对手发言的回应（非流式）
        :param opponent_message: 对手的发言内容
        :return: 生成的回应内容
        """
        print(f"\n=== {self.name} 正在生成回应 ===")
        
        try:
            # 构建完整的对话历史
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # 添加所有历史对话
            messages.extend(self.conversation_history)
            
            # 添加当前需要回应的消息
            messages.append({"role": "user", "content": opponent_message})
            
            # 打印请求信息
            print("\n发送请求：")
            print(f"Model: {self.model}")
            print("Messages:")
            for msg in messages:
                print(f"- {msg['role']}: {msg['content'][:50]}...")
            
            # 调用API生成回应并添加错误捕获和重试机制
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=0.7,  # 控制回答的创造性
                        max_tokens=2000   # 控制回答的最大长度
                    )
                    
                    # 获取生成的回应
                    response_content = response.choices[0].message.content
                    
                    # 更新对话历史
                    self.conversation_history.append({"role": "user", "content": opponent_message})
                    self.conversation_history.append({"role": "assistant", "content": response_content})
                    
                    return response_content
                except Exception as retry_error:
                    retry_count += 1
                    print(f"API调用失败，尝试第 {retry_count} 次重试。错误: {str(retry_error)}")
                    if retry_count >= max_retries:
                        raise retry_error
                    import time
                    time.sleep(1)  # 重试前稍微等待一段时间
            
        except Exception as e:
            print(f"\n=== API调用错误 ===")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误信息: {str(e)}")
            if hasattr(e, 'response'):
                print(f"响应状态码: {e.response.status_code if e.response else 'N/A'}")
                print(f"响应内容: {e.response.text if e.response else 'N/A'}")
            raise

    def stream_response(self, opponent_message: str) -> Generator[str, None, None]:
        """
        流式生成对辩论对手发言的回应
        :param opponent_message: 对手的发言内容
        :return: 生成器，逐步返回生成的内容
        """
        print(f"\n=== {self.name} 正在流式生成回应 ===")
        
        try:
            # 构建完整的对话历史
            messages = [
                {"role": "system", "content": self.system_prompt}
            ]
            
            # 添加所有历史对话
            messages.extend(self.conversation_history)
            
            # 添加当前需要回应的消息
            messages.append({"role": "user", "content": opponent_message})
            
            # 打印请求信息
            print("\n发送流式请求：")
            print(f"Model: {self.model}")
            
            # 调用API生成流式回应
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                stream=True  # 启用流式输出
            )
            
            # 收集完整的回应用于更新历史记录
            full_response = ""
            
            # 逐步产出生成的内容
            for chunk in stream:
                if hasattr(chunk.choices[0], 'delta') and hasattr(chunk.choices[0].delta, 'content'):
                    content = chunk.choices[0].delta.content
                    if content:
                        full_response += content
                        yield content
            
            # 更新对话历史
            self.conversation_history.append({"role": "user", "content": opponent_message})
            self.conversation_history.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            print(f"\n=== 流式API调用错误 ===")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误信息: {str(e)}")
            if hasattr(e, 'response'):
                print(f"响应状态码: {e.response.status_code if e.response else 'N/A'}")
                print(f"响应内容: {e.response.text if e.response else 'N/A'}")
            raise
    
    def get_response(self, opponent_message: str, stream: bool = False) -> Union[str, Generator[str, None, None]]:
        """
        获取对辩论对手发言的回应，支持流式和非流式两种模式
        :param opponent_message: 对手的发言内容
        :param stream: 是否使用流式输出
        :return: 如果stream=False返回完整回应字符串，如果stream=True返回生成器
        """
        if stream:
            return self.stream_response(opponent_message)
        else:
            return self.generate_response(opponent_message)
