import ollama
from case_cut import case_cut
import re

class model(case_cut):
    def __init__(self):
        super().__init__()
        self.model = "qwen2.5:7b"

    def ask(self,
            message, 
            prompt="You are a helpful assistant."
            ):
        host="127.0.0.1"
        port="6399"
        client= ollama.Client(host=f"http://{host}:{port}")
        res = ollama.chat(
            model=self.model,
            stream=False,
            messages=[{"role": "user","content": message}],
            options={"temperature":0}
            )
        r = res['message']['content']
        if 'deepseek' in self.model:
            r = re.sub(r'</?thinker.*?>', '', r)
        self._last_question = message
        self._last_anwser = r
        return r
    
if __name__ == '__main__':

    ds = model()
    ds.model = "courtAssistant:latest"
    # with open(r'典型合同\（2014）津高民四终字第79号.txt', mode='r', encoding='utf-8') as f:
    #     c = f.read()
    # ds.cut(c)