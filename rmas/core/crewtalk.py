from ..model import deepseek_api

class talkagent:
    def __init__(self,name,Character):
        self.llm = deepseek_api()
        self.name = name
        self.character = Character
    def  chat(self,history):
        real_history = [{"role": "system", "content": self.character}]
        for round in history:
            if round['role'] == 'user':  
                real_history.append({"role": "user", "content": round['content']})
        chat=self.llm.mt_chat(real_history,False)
        print(self.name+':'+chat)
        history.append({"role": "user", "content": self.name+chat})





