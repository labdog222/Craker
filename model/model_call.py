import os
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class ModelAPI:
    def __init__(self, api_key=None, default_model=None):
        self.api_key = api_key or os.getenv("API_KEY")
        self.default_model = default_model or os.getenv("DEFAULT_MODEL", "gpt-4-turbo")

        if not self.api_key:
            raise ValueError("API key is required. Please set it in your .env file or pass it directly.")

    def call_model(self, prompt, model_name=None, **kwargs):
        """调用指定模型生成响应"""
        model_name = model_name or self.default_model
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
        }
        data.update(kwargs)  # 添加任何额外的参数，例如 max_tokens, temperature

        response = requests.post("https://api.openai.com/v1/chat/completions", json=data, headers=headers)

        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"API request failed with status {response.status_code}: {response.text}")

    def set_default_model(self, model_name):
        """设置默认模型"""
        self.default_model = model_name
        print(f"Default model set to {self.default_model}")

# 使用示例
if __name__ == "__main__":
    api = ModelAPI()  # 使用 .env 文件中的默认 API 密钥和模型
    prompt = "What are the main benefits of GPT-4?"

    try:
        response = api.call_model(prompt)
        print("Response:", response)
    except Exception as e:
        print("Error:", e)
