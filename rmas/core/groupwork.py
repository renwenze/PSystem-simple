import time 
class GroupChat:
    def __init__(self,members=[]):
        self.members=members
    def talk_by_order(self,input):
        out_context=[]
        print('\n--------------------AgentGroup开始讨论,依次发言--------------------\n')
        time.sleep(3)
        for agent in self.members:
                print('\n--------------------'+agent.role+':--------------------\n')
                if agent.role=='knowledge_expert':
                    print('\n-----调用rag,websearch-----\n')
                    time.sleep(3)
                    print('\n-----整理论据-----\n')
                    time.sleep(3)
                if agent.role=='strategy_expert':
                    print('\n-----调用strategy module-----\n')
                    time.sleep(3)
                    print('\n-----选取策略注入对话-----\n')
                    time.sleep(3)
                talk=agent.generate(input)
                out_context.append(talk)
        support = ','.join(out_context)
        print('\n--------------------AgentGroup讨论结束,返回用户代理--------------------\n')
        time.sleep(3)
        return {'role':'assistant','content':support}