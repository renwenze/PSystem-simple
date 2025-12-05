from openai import OpenAI
import json
from .config import API

# 初始化 OpenAI 客户端
client = OpenAI(api_key=API)

# 定义工具
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"],
            },
        },
    }
]

# 模拟获取天气的函数
def get_weather(location):
    # 这里可以调用实际的天气 API
    return "24℃ and sunny"

# 初始化对话
messages = [{"role": "user", "content": "What's the weather in Hangzhou?"}]

# 第一次调用模型
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=messages,
    tools=tools,
)

# 解析模型的响应
message = response.choices[0].message

# 检查是否有工具调用
if message.tool_calls:
    for tool_call in message.tool_calls:
        # 获取工具名称和参数
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        # 调用相应的工具
        if function_name == "get_weather":
            location = function_args["location"]
            weather = get_weather(location)  # 调用工具函数

            # 将 assistant 消息（包含 tool_calls）添加到对话历史中
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [tool_call],
            })

            # 将工具结果添加到对话历史中
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,  # 确保 tool_call_id 匹配
                "name": function_name,
                "content": weather,
            })

    # 再次调用模型
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=tools,
    )

    # 获取模型的最终回复
    final_message = response.choices[0].message
    print(f"Assistant: {final_message.content}")



