from openai import OpenAI, NOT_GIVEN
import pandas as pd
import random
import os

class Qwen:
    def __init__(self):
        self._last_question = ''
        self._last_anwser = ''
    def ask(self,
            message, 
            api=os.getenv("OPENAI_API_KEY"),
            prompt="You are a helpful assistant.", 
            is_json=False,
            ):
        client = OpenAI(
            api_key=api,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        if is_json:
            prompt += ",你应当用json格式回答"
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[{'role': 'system', 'content': prompt},
                    {'role': 'user', 'content': message}],
            response_format={"type": "json_object"} if is_json else NOT_GIVEN,
            )
        r = completion.choices[0].message.content
        self._last_question = message
        self._last_anwser = r
        return eval(r) if is_json else r
    
if __name__ == '__main__':
    qwen = Qwen()
    anwser = qwen.ask('你是谁', is_json=True)
    print(anwser)