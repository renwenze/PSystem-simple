from ast import Pass


class validator:
    '''
     post validate:验证输出内容是否存在事实上的活着逻辑上的错误
    '''
    def __init__(self):
        self.check_point = ['knowledge','logic']
        self.check_source = ['web','local']
    
    def _check(self,contrxtcheck_point:str = 'knowledge',check_source:str='web'):
        if check_point == 'knowledge':
            if check_source == 'web':
                pass
            if check_source == 'local':
                pass
        if check_point == 'logic':
            pass
    
    def check_logic(self):
        result = self._check('logic')
        return result

    def check_knowledge(self):
        result = self._check('knowledge')
        return result

        

            