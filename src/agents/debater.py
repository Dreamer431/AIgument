from typing import List, Dict
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
        生成对辩论对手发言的回应
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
            
            # 调用API生成回应
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
            
        except Exception as e:
            print(f"\n=== API调用错误 ===")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误信息: {str(e)}")
            if hasattr(e, 'response'):
                print(f"响应状态码: {e.response.status_code if e.response else 'N/A'}")
                print(f"响应内容: {e.response.text if e.response else 'N/A'}")
            raise
