from typing import Literal
stance = Literal["agree","disagree","neutral"]
import time 
class UserProfile:

    def __init__(self,name,topic='是否开放校园',stance= 0 ,points=[]):
        self.name :str = name
        self.topic :str = topic
        self.stance :int = stance
        self.init_stance :int = stance
        self.points :list = points
        self.stance_track = {}
    def show(self):
        print('we are talking abot '+self.topic+'\n')
        if self.init_stance > 5:
            print(self.name +'\'s attitude is supportive at the beginning'+'\n')
        else :
            print(self.name +'\'s attitude is opposed at the beginning'+'\n')
        time.sleep(2)
        # TODO 历史转变图绘制

        print('and his points are as follows:\n')
        for i in self.points:
            print(i+'\n')
        time.sleep(2)    
        print('and his stance_track is as follows:\n')
        for r,n in self.stance_track.items():
            print('round '+str(r)+' :'+str(n)+' ' )
   
    def update_stance(self,stance):
        self.stance = stance
    def update_points(self,points):
        if points is not None:
            self.points.extend(points)
    def update_stance_track(self,round,status):
        self.stance_track[round] = status
 