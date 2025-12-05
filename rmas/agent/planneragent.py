from ..model import deepseek_api
from ..config import plan_summary
class PlannerAgent:
    """Planner agent in RMAS."""
    def __init__(self,role:str,origin_task:str):
        self.llm = deepseek_api()
        self.role = role
        self.origin_task = plan_summary
        #print('接入deepdeek')
    def summary(self,input):
        result = self.llm(input,self.origin_task,out=True)
        return result