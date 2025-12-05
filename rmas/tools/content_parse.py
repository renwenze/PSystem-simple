'''
tools for parse  content from pdf,doc,txt 
basic compontent for  database construction
'''
class ContentParse:
    def __init__(self,content,source='doc'):
        self.content = content
        self.source = source

    def pdf_parse(self):
        pass

    def doc_parse(self):
        pass

    def txt_parse(self):
        pass

    def parse(self):
        if self.source == 'pdf':
            self.pdf_parse()
        elif self.source == 'doc':
            self.doc_parse()
        elif self.source == 'txt':
            self.txt_parse()
        else:
            raise ValueError('source must be pdf,doc,txt')




