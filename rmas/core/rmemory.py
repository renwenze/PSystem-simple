from typing import Dict, List
class Memory:
    def __init__(self):
        self.history:List[Dict] = []
    def memory_pruning(self):
        if len(self.history) > 10:
            self.history = self.history[0:2].extend(self.hisroty[-5:])
    def memory_summary(self):
        pass
    #TODO:优化memory
    def memory_append(self,content:str):
        self.history.append(content)
    def multi_layer_memory(self):
        #TODO:群体先验记忆 数据库接口
        pass