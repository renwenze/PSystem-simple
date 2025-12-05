from ..model import deepseek_api
class agent_integrated():
    def __init__(self,name:str):
        self.llm = deepseek_api()
        self.name = name
    def emotion_analyze(self,history):
        pass
    def emotion_inject(self,mode):
        pass
    def global_strategy(self,mode):
        pass
    def local_strategy(self,mode):
        pass
