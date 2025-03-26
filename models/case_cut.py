from qwen import Qwen
import re
import Levenshtein
from fuzzywuzzy import fuzz

class case_cut(Qwen):
    def __init__(self):
        super().__init__()
        self.path = 'cases.csv'

        with open(self.path, 'a', encoding='utf-8') as f:
            if not f.readable() or not f.read():
                f.write('id,debate,judge,point,score\n')

    @staticmethod
    def lcs(X, Y):
        m = len(X)
        n = len(Y)

        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if X[i - 1] == Y[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        lcs_length = dp[m][n]
        lcs_str = []
        i, j = m, n
        while i > 0 and j > 0:
            if X[i - 1] == Y[j - 1]:
                lcs_str.append(X[i - 1])
                i -= 1
                j -= 1
            elif dp[i - 1][j] >= dp[i][j - 1]:
                i -= 1
            else:
                j -= 1

        return lcs_length / n

    def __debate(self, c):
        r = self.ask(
            "你需要从裁判书原文中提取出双方诉求与辩论的部分，也就是在原文的当事人信息之下，法院审理的判决之上."
            "例如:原告成小东诉称：2011年10月4日，被告陈金锁向我购买价值3330元的汽车配件，2012年5月3日，被告仅支付500元，尚欠2830元的货款，我多次催要，至今此款未付。现我要求被告立即支付拖欠的货款2830元。"
            "被告陈金锁辩称：我不欠原告钱，我经营的爱车驿站是在2011年年底前一两个月关门的，关门前所欠的债务都已结清。2011年10月4日，我有没有向原告成小东购买过汽车配件，因为时间太长我已经记不清了，我只知道我不欠钱。"
            f"下面是裁判书原文：{c}"
            "你不可以回答原文中没有的内容",
            prompt="你是一个被开发用于文本切割的助手，你的任务只是剪切文本，从原文中摘取出用户需要的信息，你不需要总结和概括"
        )
        return str(r)
    
    def __judge(self, c):
        r = self.ask(
            "你需要从裁判书原文中提取出法院审理和判决的部分，包括在此之前的法院判决内容，也就是在原文的当事人双方诉求和辩诉之下."
            "例如:天津自由贸易试验区人民法院认为，双方贷款合同约定，本合同发生争议，应向合同签订地人民法院管辖。本案消费信贷合同条款载明合同签订地为杭州市西湖区文三路259号1幢昌地火炬大厦901室。本案系签订、履行行为，均在互联网上完成的金融借款合同纠纷，应由杭州互联网法院集中管辖。天津自由贸易试验区人民法院作出(2022)津0319民初1000号民事裁定，将本案移送杭州互联网法院处理。杭州互联网法院认为移送不当，遂层报浙江省高级人民法院。"
            "浙江省高级人民法院经审查认为，本案系金融借款合同纠纷。案涉合同虽然约定“合同签订地的人民法院”管辖，但因该合同系被告事先拟定好的格式合同，现有证据亦未证明被告在合同双方签订时已对原告尽到提醒义务，故不应认定该管辖协议的效力。且案涉合同系在互联网虚拟空间中签署确认，不存在地理意义上的签订地，因此在适用《中华人民共和国民事诉讼法》第三十五条协议管辖的规定时，应审查约定的管辖地点是否与争议有实际联系。本案中，双方当事人住所地均非杭州市西湖区，且无证据证明杭州市西湖区为案涉合同数据电文发出地与接收地，或为案涉合同数据存储服务器所在地，因此杭州市西湖区与案涉争议缺乏实际联系。本案应当按照合同纠纷的一般管辖原则，由被告住所地或者合同履行地人民法院管辖。天津自由贸易试验区人民法院作为被告住所地人民法院对本案具有管辖权，该院将本案移送处理不当。经与天津市高级人民法院协商未果，依照《中华人民共和国民事诉讼法》第三十八条第二款规定，报请本院指定管辖。"
            "本院认为，本案系金融借款合同纠纷。《中华人民共和国民事诉讼法》第三十五条规定，合同或者其他财产权益纠纷的当事人可以书面协议选择被告住所地、合同履行地、合同签订地、原告住所地、标的物所在地等与争议有实际联系的地点的人民法院管辖，但不得违反本法对级别管辖和专属管辖的规定。案涉合同虽然约定“合同签订地的人民法院”管辖，但是，双方当事人未提供证据材料用以证明案涉合同的实际签订地在浙江省杭州市，同时，双方当事人的住所地均不在浙江省杭州市，浙江省杭州市与本案争议没有任何实际联系。此类小额金融借款合同纠纷，出借方一方主体特定、借款方一方主体不特定，存在着面广量大的情形，虽然协议选择合同签订地人民法院管辖，但是，在无证据材料可以用以证明浙江省杭州市与本案争议有实际联系的情况下，就此认定杭州互联网法院是本案的管辖法院，势必造成大量的“异地”案件通过协议管辖进入约定法院，破坏正常的民事诉讼管辖公法秩序，故案涉协议管辖条款无效。《中华人民共和国民事诉讼法》第二十四条规定，因合同纠纷提起的诉讼，由被告住所地或者合同履行地人民法院管辖。本案中，天津自由贸易试验区人民法院，作为被告住所地人民法院，对本案具有管辖权，裁定将本案移送杭州互联网法院处理不当。"
            "综上，本院依照《中华人民共和国民事诉讼法》第三十八条第二款、《最高人民法院关于适用<中华人民共和国民事诉讼法>的解释》第四十条、第四十一条规定，裁定如下："
            "一、撤销天津自由贸易试验区人民法院(2022)津0319民初1000号民事裁定；"
            "二、本案由天津自由贸易试验区人民法院审理。"
            "本裁定一经作出即发生法律效力。"
            f"下面是裁判书原文：{c}"
            "你不可以回答原文中没有的内容,我所要求的是当事人辩诉部分以下的内容",
            prompt="你是一个被开发用于文本切割的助手，你的任务只是剪切文本，从原文中摘取出用户需要的信息，你不需要总结和概括"
        )
        return r
    
    def __point(self, judge):
        r = self.ask(
            "你需要从下面原文中提取法院总结出的争议焦点部分"
            "比如:"
            "'本院认为，本案的争议焦点如下："
            "一、李遵基与彭超之间是否存在委托关系"
            "通过在案当事人陈述、证人证言、录音、短信、转账记录等证据，可以证明涉案款项借款时，孙成光系联系李遵基商谈借款事宜，彭超接受李遵基指示办理出借事宜，涉案款项最初源自李遵基账户，实际出借人是李遵基。彭超主张其与李遵基间系借款关系，就此未签订借款协议，未约定借款期限及利息。但如此大额款项却不签订借款协议、不约定借款期限及利息，与常理不符，李遵基此后亦向彭超出借款项，彭超即向李遵基出具借据，彭超前后行为与其所述相矛盾；相关借款合同原件由李遵基持有，彭超称其销毁，如彭超系相关款项的出借人，其将协议等交付他人自己并不持有，显然不合常理。彭超在原一审中称其与李遵基间系借款关系，在原二审中称对于650万元合同中的500万元与李遵基系委托关系，在再审中又称与李遵基间系借款关系，其前后陈述相矛盾，综上，本院对其主张不予采信。故本院综合认定李遵基与彭超之间就本案借款存在委托关系。"
            "二、在委托人李遵基起诉要求还款的情况下，孙成光向彭超还款是否具有正当性和合理性"
            "（一）孙成光与彭超签订借款合同时明知李遵基与彭超间存在委托关系，故借款合同约束李遵基与孙成光。《中华人民共和国合同法》第402条规定：“受托人以自己的名义，在委托人的授权范围内与第三人订立的合同，第三人在订立合同时知道受托人与委托人之间的代理关系的，该合同直接约束委托人和第三人，但有确切证据证明该合同只约束受托人和第三人的除外。”本案中，第一，通过录音、短信、微信聊天记录、证人证言、庭审笔录等证据，可以证明：涉案借款系孙成光通过肖某联系李遵基，共同商量向李遵基借款事宜，借款时孙成光知道所借款项来源于李遵基。结合孙成光认可的肖某证人证言中称“孙成光称彭超替李遵基签订借款协议”，以及借款后李遵基向孙成光催要款项，孙成光亦接受李遵基的催款等，上述形成一个完整的证据链，能够证明孙成光在借款时知晓李遵基与彭超间的委托关系。第二，孙成光在原一、二审称在两份合同签订时均不知道李遵基与彭超间的委托关系，而再审中又称对650万元借款合同在签订时认为李遵基与彭超间存在委托关系、对300万元借款合同在签订时不知道存在委托关系，其前后陈述具有不一致性，本院认为其在主观上有故意隐瞒事实之嫌。第三，从三方主体多次转账借款、整体对账、催促还款、转账还款等交易习惯来看，650万元借款合同与300万元借款合同的交易具有高度的一致性，因此，孙成光关于本案借款合同签订时不知道委托关系的陈述本院不予采信。故本案借款合同直接约束委托人李遵基和第三人孙成光。在李遵基起诉要求孙成光履行合同义务时，孙成光应当向李遵基还款。"
            "（二）即便孙成光在签订本案合同时，不知道李遵基与彭超间的委托关系，在李遵基起诉要求还款时，其仍应向李遵基还款。《中华人民共和国合同法》第403条之规定：“受托人以自己的名义与第三人订立合同时，第三人不知道受托人与委托人之间的代理关系的，受托人因第三人的原因对委托人不履行义务，受托人应当向委托人披露第三人，委托人因此可以行使受托人对第三人的权利，但第三人与受托人订立合同时如果知道该委托人就不会订立合同的除外。”该条明确规定了在委托人权益无法保障时委托人的主动介入权。根据该条文意，当受托人因第三人原因对委托人不履行义务时，若委托人原本就知道第三人，便无需受托人告知，更可以直接向第三人主张权利。本案中，即便孙成光在签订合同时不知道委托关系，但至李遵基起诉时，孙成光确实未能按时履行还款义务，故李遵基有权直接向孙成光主张权利。2019年李遵基起诉孙成光、彭超要求其还款时，李遵基已经履行了通知义务。2020年1月孙成光收到诉讼材料时，此时孙成光已收到通知，则委托人李遵基取代了受托人彭超的地位，涉案借款合同对委托人李遵基与第三人孙成光具有约束力，孙成光应按合同约定向李遵基履行义务。"
            "综上，在李遵基起诉要求孙成光还款时，此时无论李遵基与彭超委托关系是否解除，孙成光均应向李遵基还款。孙成光称录音中李遵基没有反对其向彭超还款，因录音时间为2019年，仅能表明当时李遵基的意见，并不意味着其后李遵基始终认可该行为，在李遵基已经起诉的情况下，孙成光以此抗辩，本院不予采信。"
            "在2020年1月孙成光收到李遵基起诉其与彭超还款的诉讼材料后，孙成光已明知李遵基要求其将借款偿还给李遵基本人，而孙成光在诉讼期间仍与彭超签署《借款和抵押续期协议》等协议，并将款项付至相关人员账户，损害李遵基的合法权益。故孙成光向彭超的相关付款行为不能约束李遵基，即不能视为对李遵基的还款，其可就相关款项与彭超另行解决。"
            "三、关于李遵基主张的借款本金及利息"
            "合法的债务应当清偿。《最高人民法院关于审理民间借贷案件适用法律若干问题的规定》（2015年9月1日起施行）第二十六条第一款规定：“借贷双方约定的利率未超过年利率24%，出借人请求借款人按照约定的利率支付利息的，人民法院应予支持。”；第二十七条规定：“借据、收据、欠条等债权凭证载明的借款金额，一般认定为本金。预先在本金中扣除利息的，人民法院应当将实际出借的金额认定为本金。”；第二十九条第一款规定：“借贷双方对逾期利率有约定的，从其约定，但以不超过年利率24%为限。”本案中，李遵基实际提供借款本金200万元，故孙成光应按该金额予以偿还。借款合同约定借款期限内的年利率为12.5%，未超过法律规定的限度范围，故孙成光应按照年利率12.5%的标准支付借款期限内的利息。因李遵基分别于2018年5月30日转款50万元、2018年7月11日转款150万元，故孙成光应分别以该两笔款项为基数，自转款之日至2018年12月31日借款期限届满之日止按照前述利率支付标准支付借款期限内的利息。就该项请求李遵基借款起算时间有误，本院予以调整。借款合同中关于逾期还款的利息、滞纳金作出了约定，李遵基主张的标准超过了法律规定的限度，本院在年利率24%的范围内予以支持。'"
            "你应当回答：一、李遵基与彭超之间是否存在委托关系。二、在委托人李遵基起诉要求还款的情况下，孙成光向彭超还款是否具有正当性和合理性。关于李遵基主张的借款本金及利息。"
            "你并不是自己总结和概括争议焦点，而是从原文中提取，如果原文中没有提到，则回答无"
            f"下面是法院审理的原文：{judge}",
            prompt="你是一个被开发用于文本切割的助手，你的任务只是剪切文本，从原文中摘取出用户需要的信息，你不需要总结和概括"
        )
        return r

    def find_debate_position(self, original_text, debate_text):
        pattern = re.escape(debate_text)
        match = re.search(pattern, original_text, re.IGNORECASE)

        if match:
            return match.end()
        else:
            return -1

    def cut_from_debate(self, original_text, debate_text):
        start_pos = self.find_debate_position(original_text, debate_text)
        
        if start_pos != -1:
            return original_text[start_pos:].strip()
        else:
            return None

    def find_best_match(self, original_text, debate_text):
        # 使用Levenshtein距离找出最相似的文本
        start_pos = -1
        best_score = float('inf')
        for i in range(len(original_text) - len(debate_text)):
            substring = original_text[i:i + len(debate_text)]
            score = Levenshtein.distance(substring, debate_text)
            if score < best_score:
                best_score = score
                start_pos = i
        return start_pos

    def cut_from_debate1(self, original_text, debate_text):
        start_pos = self.find_best_match(original_text, debate_text)
        if start_pos != -1:
            return original_text[start_pos:].strip()
        else:
            return None

    def find_debate_end(self, case, debate_part, threshold=80):
        preprocessed_case = case.replace(' ', '').replace('\n', '')
        preprocessed_debate = debate_part.replace(' ', '').replace('\n', '')
        
        len_debate = len(preprocessed_debate)
        if len_debate == 0:
            return 0
        
        max_score = 0
        best_end = -1
        step = max(1, len_debate // 2)
        
        for i in range(0, len(preprocessed_case) - len_debate + 1, step):
            window = preprocessed_case[i:i+len_debate]
            current_score = fuzz.partial_ratio(preprocessed_debate, window)
            if current_score > max_score:
                max_score = current_score
                best_end = i + len_debate
                if max_score == 100:
                    break
        
        # 返回原case中的实际位置（需调整预处理带来的偏移）
        if max_score >= threshold:
            # 找到预处理后的位置，映射回原文本的位置
            # 由于预处理移除了空格和换行，此处需重新计算实际位置
            # 此处简化处理，实际可能需要更精确的映射
            return best_end
        else:
            return -1

    def __point_extract(self, judge_text):
        patterns = [
            r'争议焦点(如下|包括|为：?)：?',
            r'焦点问题(如下|包括|为：?)：?',
            r'本案(主要|需要?)(解决|审查)的(问题|焦点)'
        ]
        
        start_pos = -1
        for pattern in patterns:
            match = re.search(pattern, judge_text)
            if match:
                start_pos = match.end()
                break
        
        if start_pos == -1:
            return self.__point_model_fallback(judge_text)

        focus_content = judge_text[start_pos:].strip()
        
        focus_items = re.findall(
            r'(?:^|\n)\s*([一二三四五六七八九十]+、|\d+\.)\s*([^\n]+?)(?=\s*(?:[一二三四五六七八九十]+、|\d+\.|$|。))',
            focus_content
        )

        if focus_items:
            return '\n'.join([f"{num}{text}" for num, text in focus_items])
        else:
            return self.__split_by_keywords(focus_content)

    def __split_by_keywords(self, text):
        splits = re.split(r'[；。]', text)
        return '\n'.join([s.strip() for s in splits if s.strip()])

    def __point_model_fallback(self, text):
        # 调用模型兜底
        return self.__point(text)

    def __point_validate(self, extracted, original):
        return fuzz.partial_ratio(extracted, original) > 85
    
    def fcut(self, case):
        return case.split('。')

    def __is_pass(self, case, debate):
        score = self.lcs(case, str(debate))
        print(score)
        return score > 0.9, score
    
    def cut(self, case, id):
        for _ in range(3):
            debate = self.__debate(case).strip("\n")
            t, score = self.__is_pass(case, debate)
            if t:
                break
        debate_end = self.find_debate_end(case, debate)
        if debate_end != -1:
            judge = case[debate_end:].strip()
        else:
            # 模糊匹配失败，使用模型提取
            judge = self.__judge(case).strip('\n')
            # judge = None
        point = self.__point_extract(judge)
        with open(self.path, 'a', encoding='utf-8') as f:
            f.write(f"{id},{debate},{judge},{point},{score}\n")
    
if __name__ == '__main__':
    cc = case_cut()

    import pandas as pd

    df = pd.read_csv('2021f.csv', encoding='gbk')
    df_case = df[['案号', '全文']]
    for _, row in df_case.iterrows():
        print(row['案号'])
        cc.cut(row['全文'], row['案号'])
        # break
