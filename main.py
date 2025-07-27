import json
from zhipuai import ZhipuAI

# 题目要求实现函数
def get_weather(city: str) -> str:
    weather_data = {
        "beijing": {
            "location": "Beijing",
            "temperature": {"current": 32, "low": 26, "high": 35},
            "rain_probability": 10,
            "humidity": 40
        },
        "shenzhen": {
            "location": "Shenzhen",
            "temperature": {"current": 28, "low": 24, "high": 31},
            "rain_probability": 90,
            "humidity": 85
        }
    }
    city_key = city.lower()
    if city_key in weather_data:
        return json.dumps(weather_data[city_key], ensure_ascii=False)
    return json.dumps({"error": "Weather Unavailable"}, ensure_ascii=False)

# Agent 工作流 
def run_agent(user_task: str = "查找深圳的天气，然后用一句话告诉我出门要不要带伞"):
    client = ZhipuAI(api_key="YOUR_API_KEY") # 请替换为您的API Key 本人原本使用的是智谱AI API：https://bigmodel.cn/
    model = "glm-4"

    system_prompt = (
        "你是一个能够通过函数调用获取天气数据的助理。"
        "当你需要天气数据时，请调用 get_weather(city)。"
        "拿到天气信息后，请只用一句中文告诉用户是否需要带伞，并且只输出一次最终答案。"
    )

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "根据城市名称获取天气信息（含降雨概率等）",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "城市名称，例如 'shenzhen' 或 'beijing'"
                        }
                    },
                    "required": ["city"]
                }
            }
        }
    ]

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_task}
    ]

    while True:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        msg = resp.choices[0].message
        tool_calls = getattr(msg, "tool_calls", None)
        if tool_calls:
            for tc in tool_calls:
                if tc.function.name == "get_weather":
                    args = json.loads(tc.function.arguments)
                    result = get_weather(**args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": "get_weather",
                        "content": result
                    })
            continue

        final_answer = msg.content.strip()
        print("\n一句话建议：")
        print(final_answer)
        break

if __name__ == "__main__":
    run_agent()
