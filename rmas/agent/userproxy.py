"""
User Proxy Agent Module.
"""
#TODO: 构建画像时异步调用llm
import time
from ..core import UserProfile
from .baseagent import BaseAgent
class UserProxy(BaseAgent):
    def __init__(self, topic,name,role):
        super().__init__(role) #self.llm
        self.up = UserProfile(name)
        self.round = 1
        self.history = [{"role": "system", "content": f"你是一个说服专家,你需要说服对方支持{topic},请根据用户的输入以对话的形式给出你的回复"}]
        self.end = False
        self.emo = -1
        print('-----用户代理初始化成功-----\n')
        time.sleep(2)
    def _talk_with_group(self,group,input):
        pass
    def _translate2system(self, input,group):
        self.history.append({"role": "user", "content": input})
        support=group.talk_by_order(input)
        #TODO:引入策略，画像等其他模块
        self.history.append(support)
        return self.llm.mt_chat(self.history,out=False)
    def _translate2user(self,output):
        print('\n'+self.role+':\n')
        match self.emo:
            case 1:
                emo_infect = '你是一个语言学家，把下面的内容变成更加贴近真实人类对话的内容，语气生动平缓，逻辑清晰，如果需要的话可以适当夹杂一些语气词，尽量减少列表等形式的输出，但是不能改变原本对话的意思，不要有多余的输出\n###注意：使用“共情”+“尊重差异”的语气，避免强硬推理'
            case 2:
                emo_infect = '你是一个语言学家，把下面的内容变成更加贴近真实人类对话的内容，语气生动平缓，逻辑清晰，如果需要的话可以适当夹杂一些语气词，尽量减少列表等形式的输出，但是不能改变原本对话的意思，不要有多余的输出\n###注意：激发兴趣点，用类比/故事拉近距离'  
            case 3:
                emo_infect = '你是一个语言学家，把下面的内容变成更加贴近真实人类对话的内容，语气生动平缓，逻辑清晰，如果需要的话可以适当夹杂一些语气词，尽量减少列表等形式的输出，但是不能改变原本对话的意思，不要有多余的输出\n###注意：乘胜追击，引入更多逻辑证据巩固立场'
            case 4:
                emo_infect = '你是一个语言学家，把下面的内容变成更加贴近真实人类对话的内容，语气生动平缓，逻辑清晰，如果需要的话可以适当夹杂一些语气词，尽量减少列表等形式的输出，但是不能改变原本对话的意思，不要有多余的输出\n###注意：提供选择空间，引导用户表达理由，有助于认知调整'
            case 5:
                emo_infect = '你是一个语言学家，把下面的内容变成更加贴近真实人类对话的内容，语气生动平缓，逻辑清晰，如果需要的话可以适当夹杂一些语气词，尽量减少列表等形式的输出，但是不能改变原本对话的意思，不要有多余的输出\n###注意：简化信息结构，使用图示或明确类比，帮助理'
        real_output=self.llm(output,emo_infect,out=True)
        return  real_output
    def _get_point(self,input):
        points=self.llm(input,'你是一个语言学家,现在你正在参加一场辩论会,你需要记录对话者的具体观点,并以列表（无需符号）的形式返回观点,,但是如果你未识别到观点,直接返回NONE即可.注意:严格按照要求输出内容，不要有多余的字符',out=False)
        #TODO: 简单prompt封装至config
        if 'NONE' in points.upper():
            return None
        else:
            points=points.split(',')
            print('-----提取观点成功-----\n')
            time.sleep(3)
            for _  in points:
                print(_+'\n')
        return points
    def _get_stance(self,input):
        stance=self.llm(input,'你是一个语言学家,现在你正在参加一场辩论会,你需要记录对话者对'+self.up.topic+'的态度,并以数字(0-10)的形式返回态度,0为反对,10为支持,如果对话的内容没有明确的倾向,请输出5.注意：不要有数字以外的输出！',out=False)
        stance = int(stance)
        print('-----提取态度成功-----\n')
        time.sleep(3)
        return stance
    def emo_recgonition(self,input):
        emo = self.llm(input,'''你是一个心理学家,现在你正在参加一场讨论,你需要记录对话者的情感进行识别，并归类到下列5种中的一种：
        *1愤怒 / 防御
        *2冷漠 / 怀疑
        *3共鸣 / 被理解
        *4矛盾 / 反思
        *5焦虑 / 困惑
        注意：最后输出的只要是数字，不要有其他字符或者多余的输出！！     
        ''',out=False)
        emo = int(emo)
        print('-----情感识别成功-----\n')
        time.sleep(3)
        return emo
    def set_user_profile(self,input):
        points=self._get_point(input)
        self.up.update_points(points)
        stance=self._get_stance(input)
        self.up.update_stance(stance)
        self.up.update_stance_track(self.round,stance)
        print('-----用户画像更新成功-----\n')
        time.sleep(3)
 
    def _terminate(self,input):
          if 'ACCEPT' in input.upper():
            self.end = True
            print('-----用户已被说服-----\n')
            time.sleep(3)


    def get_input(self):#TODO：发起对话
        if self.round == 1:
            print('\n'+self.role+':\n')
            ask = self.llm('你是一个说服专家，你的目的是说服对方支持对公众开放校园，请你先问候对方，然后生成一段话来首先开启这个话题，简单的介绍背景并引起对话者沟通的兴趣，注意：只要按要求输出内容即可，不要有多余的输出,也不要解释',out=True)       
        else:
            ask = None
            #ask = self.llm('你是一个说服专家，你的目的是说服对方支持对公众开放校园，请你根据对方的下述观点生成对话内容来继续这个话题，注意不要有多余的输出.:'+';'.join(self.up.points),out=True)
        return ask
    def judeg_complex(self,input):
        mode = self.llm(input,'你是一个语言专家，你需要判断对话者的输入是否有额外的信息输入，如果有则输出1，如果没有，比如就是“嗯嗯，行吧”这种则输出0，注意不要有其他多余的输出',out=False)
        mode = int(mode) 
        return mode
    def simple_chat(self,input,group):
        mode = self.judeg_complex(input)
        if mode == 1:
            self.set_user_profile(input)
        self.emo = self.emo_recgonition(input)
        output = self._translate2system(input,group)
        real_output=self._translate2user(output)
        self.history.append({"role": "assistant", "content": real_output})
        self.round+=1


