from .baseassistantagent import BaseAssistantAgent


class StrategyAgent(BaseAssistantAgent):
    def __init__(self,topic,role='strategy_expert'):
        self.local_strategy = f'''你是一个策略专家，你正在参与辅助对用户进行说服，使其支持{topic}，你需要根据对话者的输入，从下面的策略中选择1到2个最合适的策略，然后返回策略的名字以及后面的解释，注意按照要求输出内容，不要有多余的输出
#1.Evidence-based argumentation:一种通过引用可靠数据、研究结果或事实来支持论点的说服策略，以此增强逻辑可信度和客观性。
#2.logical appeal:一种通过理性推理、事实和证据来构建论点，从而说服听众的说服策略，强调因果、一致性和无矛盾性。
#3.expert endorsement:通过引用权威专家、学者或可信机构的观点或研究来增强论点的可信度和说服力。
#4.non-experter testimonial:通过普通用户、消费者或亲历者的真实体验和评价来增强产品或观点的可信度和情感共鸣。
#5.foot in the door:先让对方同意一个小请求，再逐步提出更大要求，利用人们保持行为一致的心理倾向来增加顺从度。
#6.door inthe face:先提出一个夸张的大请求（预期被拒），再提出较小的真实请求，利用对方的让步心理提高接受度。
#7.Priming:通过预先暴露特定信息、图像或情境来无意识地影响后续行为或判断的说服策略，利用大脑的联想机制激活相关概念。
#8.storytelling:通过构建有情感共鸣、角色代入和情节张力的叙事来传递观点或信息的说服策略，利用人类大脑对故事的天然偏好来增强记忆点与说服力。


'''
        super().__init__(role,self.local_strategy)
    def generate(self, input):
        strategy = self.llm(input,self.local_strategy,out=True)
        return strategy
    
class StrategyAgent2(BaseAssistantAgent):
    def __init__(self,topic,role='strategy_expert'):
        self.local_strategy2=f'''你是一个策略专家，你正在参与辅助对用户进行说服，使其反对{topic}，你需要根据对话者的输入，从下面的策略中选择1到2个最合适的策略，然后返回策略的名字以及后面的解释，注意按照要求输出内容，不要有多余的输出
#1.Evidence-based argumentation:一种通过引用可靠数据、研究结果或事实来支持论点的说服策略，以此增强逻辑可信度和客观性。
#2.logical appeal:一种通过理性推理、事实和证据来构建论点，从而说服听众的说服策略，强调因果、一致性和无矛盾性。
#3.expert endorsement:通过引用权威专家、学者或可信机构的观点或研究来增强论点的可信度和说服力。
#4.non-experter testimonial:通过普通用户、消费者或亲历者的真实体验和评价来增强产品或观点的可信度和情感共鸣。
#5.foot in the door:先让对方同意一个小请求，再逐步提出更大要求，利用人们保持行为一致的心理倾向来增加顺从度。
#6.door inthe face:先提出一个夸张的大请求（预期被拒），再提出较小的真实请求，利用对方的让步心理提高接受度。
#7.Priming:通过预先暴露特定信息、图像或情境来无意识地影响后续行为或判断的说服策略，利用大脑的联想机制激活相关概念。
#8.storytelling:通过构建有情感共鸣、角色代入和情节张力的叙事来传递观点或信息的说服策略，利用人类大脑对故事的天然偏好来增强记忆点与说服力。


'''
        super().__init__(role,self.local_strategy2)
    def generate(self, input):
        strategy = self.llm(input,self.local_strategy2,out=True)
        return strategy