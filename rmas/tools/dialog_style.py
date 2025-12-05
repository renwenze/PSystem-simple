from random import choice
class Dialog_Style:
    def __init__(self):
        self.style = [style1,style2,style3]

    def random_style(self):
        return choice(self.style)

    def inject_style(self,style,input):
        pass

