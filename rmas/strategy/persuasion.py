from . import BaseStrategy

class PersuasionStrategy(BaseStrategy):
    """说服策略类，实现基于对话的说服策略"""
    
    def __init__(self, max_turns=10):
        super().__init__()
        self.max_turns = max_turns
        self.current_turn = 0
        
    def execute(self, context):
        """执行说服策略
        
        Args:
            context: 包含对话历史、参与者状态等信息的上下文
            
        Returns:
            下一步对话行动
        """
        self.current_turn += 1
        if self.current_turn > self.max_turns:
            return {"action": "terminate", "reason": "达到最大对话轮数"}
            
        # 分析对话历史
        history = context.get("history", [])
        participant_state = context.get("participant_state", {})
        
        # 根据对话历史和参与者状态生成下一步行动
        if not history:
            return {"action": "initiate", "content": "开启对话"}
            
        # 分析最后一轮对话
        last_turn = history[-1]
        if "ACCEPT" in last_turn.get("response", ""):
            return {"action": "terminate", "reason": "说服成功"}
            
        return {"action": "continue", "content": "继续对话"}
    
    def evaluate(self, result):
        """评估说服策略的执行效果
        
        Args:
            result: 策略执行的结果，包含对话过程和最终状态
            
        Returns:
            float: 评估分数 (0-1)
        """
        if result.get("action") == "terminate":
            if result.get("reason") == "说服成功":
                return 1.0
            return 0.5  # 达到最大轮数但未说服成功
        
        # 根据对话进展评估中间状态
        progress = min(self.current_turn / self.max_turns, 0.8)
        return progress