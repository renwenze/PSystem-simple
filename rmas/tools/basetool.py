from typing import Any, Dict, List, Optional
class BaseTool:
    """Base class for all tools in RMAS."""
    def __init__(self,tool_name:str,tool_description:str=None,input_parameter:Dict[str,Any]=None,result_parameter:Dict[str,Any]=None):
        self.name = tool_name
        self.description = tool_description
        #self.usage_condition = usage_condition  
        self.input_parameter = input_parameter  
        self.result_parameter = result_parameter
        