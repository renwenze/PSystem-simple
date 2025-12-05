#TODO:rag
'''
local data manage tool for RMAS.

'''
class LocalData:
    def __init__(self,vector_db=None,text_db=None,kg_db=None):
        self.vector_db = vector_db
        self.text_db = text_db
        self.kg_db = kg_db
    
    
    def restore_vdb(self,content):
        pass
    def restore_tdb(self,content):
        pass
    def restore_kgdb(self,content):
        pass
    def retriver(self,input,mode='vector'):
        if mode == 'vector':
            pass
        if mode == 'keyword':
            pass
        if mode == 'kg':
            pass
        if mode == 'hyber':
            pass

    def local_validate(self,input):
        pass


