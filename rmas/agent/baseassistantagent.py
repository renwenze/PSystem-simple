from ..model import deepseek_api
class BaseAssistantAgent:
    """Assistant agent in RMAS."""
    def __init__(self,role:str,origin_task:str):
        self.llm = deepseek_api()
        self.role = role
        self.origin_task = origin_task
        #print('接入deepdeek')
    def generate(self,input):
        result = self.llm(input,self.origin_task,out=True)
        return result
        

    