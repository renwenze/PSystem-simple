from ..model import deepseek_api
class BaseAgent:
    """Base class for all agents in RMAS."""
    def __init__(self,role:str):
        self.llm = deepseek_api()
        self.role = role
        #print('接入deepdeek')