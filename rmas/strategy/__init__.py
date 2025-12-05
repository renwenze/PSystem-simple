from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """基础策略类，定义策略模块的基本接口"""
    
    def __init__(self):
        self.name = self.__class__.__name__
    
    @abstractmethod
    def execute(self, context):
        """执行策略
        
        Args:
            context: 策略执行的上下文信息
            
        Returns:
            执行结果
        """
        pass
    
    @abstractmethod
    def evaluate(self, result):
        """评估策略执行结果
        
        Args:
            result: 策略执行的结果
            
        Returns:
            评估分数
        """
        pass