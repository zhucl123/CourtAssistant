from ollama_model import model
import json
import argparse

class CourtAssistant(model):
    def __init__(self):
        super().__init__()
        self.model = "courtAssistant"

        self.templates = {
                "party_extraction": """你是一名资深法官助理，请从以下裁判文书中：
                1. 识别所有诉讼参与方（如原告、被告、上诉人、被上诉人）
                2. 提取各方主张及理由（注意'称''辩称''主张'等关键词）
                3. 按JSON格式返回，结构示例：
                {
                "上诉人": {
                    "诉求": ["撤销原判", "改判..."],
                    "理由": ["[事实认定]...", "[法律适用]..."]
                },
                "被上诉人": {
                    "答辩": ["维持原判"],
                    "理由": ["[证据]...", "[法律依据]..."]
                }
                }""",
                            
                            "conflict_detection": """请分析以下双方陈述，识别至少3类矛盾：
                1. 事实认定矛盾（如金额、时间等不一致）
                2. 证据有效性矛盾
                3. 法律适用矛盾
                返回示例：
                {
                "矛盾点": [
                    "事实矛盾：原告主张工资未支付 vs 被告声称已结清",
                    "证据矛盾：原告提供银行流水 vs 被告质疑真实性"
                ]
                }""",
                            
                            "legal_elements": """根据《民法典》第XXX条，分析以下案件：
                要件1: 合同成立（要约+承诺）
                要件2: 履行义务（付款+交付）
                要件3: 违约责任（违约事实+损失证明）
                请判断案件事实与要件的匹配情况，返回示例：
                {
                "法律要件": {
                    "合同成立": {"满足": true, "依据": "微信记录显示双方达成合意"},
                    "履行义务": {"满足": false, "缺失要素": "被告未提供交货凭证"}
                }
                }"""
            }

    def step(self, text: str) -> dict:
        # 诉讼两造切割
        parties = self.ask(
            prompt=self.templates["party_extraction"],
            message=text
        )
        
        # 矛盾分析
        conflicts = self.ask(
            prompt=self.templates["conflict_detection"],
            message=parties
        )
        
        # 法律要件匹配
        legal_analysis = self.ask(
            prompt=self.templates["legal_elements"],
            message=f"{parties}\n{conflicts}"
        )
        
        return {
            "诉讼主体": json.loads(parties),
            "争议焦点": json.loads(conflicts),
            "法律要件": json.loads(legal_analysis)
        }
    
    def analyze(self, case):
        t = self.step(case)
        return self.ask(
            t
        )
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Set model name for the model class.')
    parser.add_argument('--model', type=str, default="courtAssistant:lastest", help='调用模型 (默认: courtAssistant:lastest)')
    parser.add_argument('--case', type=str, help='输入案情')

    args = parser.parse_args()

    ca = CourtAssistant(model_name=args.model)
    ca.analyze(args.case)
