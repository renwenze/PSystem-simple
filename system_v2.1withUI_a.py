# empathy and adaptove persona
from hmac import new
import panel as pn
import asyncio
from datetime import datetime
from typing import Dict, List, Any, AsyncGenerator
import json
import time
from rmas.tools import record
from rmas.agent import StrategyAgent,KnowledgeAgent,UserProxy
from rmas.core import GroupChat
from rmas.config import get_strategy

# 启用Panel服务
pn.extension('tabulator', 'ace', 'bokeh')

class MultiAgentChatSystem:
    def __init__(self,topic):
        self.agents = {
            'user': {'name': '用户', 'color': '#3498db', 'avatar': '👤'},
            'strategy': {'name': '策略专家', 'color': '#e74c3c', 'avatar': '🎯'},
            'knowledge': {'name': '知识专家', 'color': '#2ecc71', 'avatar': '📚'},
            'persuader': {'name': '说服者', 'color': '#f39c12', 'avatar': '💬'},
            'empathy':{'name':'心理专家','color':'#9b59b6','avatar':'🧠'}
        }
        
        self.main_conversation_history = []  # 用户与说服者的对话
        self.expert_conversation_history = []  # 专家讨论历史
        self.current_turn = 0
        self.init_agents()
        # 创建UI组件
        self.setup_ui()
    def init_agents(self):
        """初始化智能体"""
        self.persuader = UserProxy('用户', topic,'MAS')
        self.strategy_expert = StrategyAgent(topic) 
        self.knowledge_expert = KnowledgeAgent(topic)


    def setup_ui(self):
        """设置用户界面"""
        # 标题
        self.title = pn.pane.Markdown("# 🤖 智能体对话系统1a", 
                                    styles={'text-align': 'center', 'font-size': '28px', 'margin': '20px 0'})
        
        # 主对话显示区域（用户 + 说服者）
        self.main_chat_display = pn.Column(
            height=600, 
            min_height=400,
            sizing_mode='stretch_width',
            scroll=True,
            styles={
                'border': '2px solid #ddd', 
                'padding': '20px', 
                'background': '#f8f9fa',
                'border-radius': '10px',
                'margin': '10px'
            }
        )
        
        # 专家讨论区域（策略专家 + 知识专家+ 心理专家）- 大屏幕适配
        self.expert_chat_display = pn.Column(
            height=500, 
            min_height=300,
            sizing_mode='stretch_width',
            scroll=True,
            styles={
                'border': '2px solid #ddd', 
                'padding': '20px', 
                'background': '#fafafa',
                'border-radius': '10px',
                'margin': '10px'
            }
        )
        
        # 专家讨论标题
        self.expert_title = pn.pane.Markdown("## 🧠 专家讨论区", 
                                           styles={
                                               'text-align': 'center', 
                                               'font-size': '20px',
                                               'margin': '10px 0'
                                           })
        
        # 用户输入区域 - 大屏幕适配
        self.user_input = pn.widgets.TextAreaInput(
            placeholder="请输入您的消息......(输入ACCEPT表示被说服,输入FINISH终止对话)",
            height=120,
            sizing_mode='stretch_width',
            max_length=1000,
            styles={'font-size': '18px'}
        )
        
        # 按钮样式优化
        button_style = {
            'font-size': '14px',
            'padding': '10px 20px',
            'margin': '5px'
        }
        
        # 发送按钮
        self.send_button = pn.widgets.Button(
            name="发送消息", 
            button_type="primary",
            width=120,
            height=50,
            styles=button_style
        )
        
        # 清空对话按钮
        self.clear_button = pn.widgets.Button(
            name="清空对话", 
            button_type="default",
            width=120,
            height=50,
            styles=button_style
        )
        
        # 系统状态显示 - 大屏幕适配
        self.status_indicator = pn.pane.Markdown("**系统状态:** 就绪")
        self.status_indicator.sizing_mode = 'stretch_width'
        self.status_indicator.styles = {
            'font-size': '18px',
            'padding': '15px',
            'font-weight': 'bold',
            'background': '#e8f4fd',
            'border-radius': '8px',
            'border': '1px solid #bee5eb',
            'margin': '10px 0'
        }
        
        # 对话统计
        self.stats_display = pn.pane.Markdown(self.get_stats_text())
        self.stats_display.sizing_mode = 'stretch_width'
        self.stats_display.styles = {
            'font-size': '16px',
            'padding': '10px',
            'background': '#f8f9fa',
            'border-radius': '8px',
            'border': '1px solid #dee2e6'
        }
        
        # 流式输出的消息容器
        self.current_streaming_message = None
        
        # 绑定事件
        self.send_button.on_click(self.handle_user_message)
        self.clear_button.on_click(self.clear_conversation)
        self.user_input.param.watch(self.on_input_change, 'value')
        
        # 初始化欢迎消息
        self.add_system_message(f"系统初始化完成，主题：是否{topic}")
        
        first_container = self.create_streaming_message_container('persuader')
        self.main_chat_display.append(first_container)
        self.get_first_response_stream(first_container, f'你是一个说服专家，你的目的是说服对方支持{topic}，请你先问候对方，然后生成一段话来首先开启这个话题，简单的介绍背景并引起对话者沟通的兴趣，注意：只要按要求输出内容即可，不要有多余的输出,也不要解释')        
                    
        
    def get_stats_text(self):
        """获取统计信息文本"""
        main_count = len(self.main_conversation_history)
        expert_count = len(self.expert_conversation_history)
        return f"**对话统计:** 主对话: {main_count} | 专家讨论: {expert_count}"
    
    def on_input_change(self, event):
        """输入框内容变化时的处理"""
        self.send_button.disabled = not bool(event.new.strip())
    
    def add_system_message(self, message: str):
        """添加系统消息到主对话框"""
        msg_data = {
            'agent': 'system',
            'message': message,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        }
        
        # 创建消息显示组件 - 大屏幕样式优化
        msg_pane = pn.pane.Markdown(
            f"🔔 **系统消息** `{msg_data['timestamp']}`\n\n{message}",
            styles={
                'background': '#f0f0f0', 
                'padding': '10px', 
                'margin': '5px', 
                'border-radius': '8px',
                'font-size': '18px',
                'border': '1px solid #ddd'
            },
            sizing_mode='stretch_width'
        )
        self.main_chat_display.append(msg_pane)
        
    def add_main_message(self, agent_id: str, message: str, metadata: Dict = None):
        """添加消息到主对话框（用户和说服者）"""
        if agent_id not in ['user', 'persuader']:
            return
            
        msg_data = {
            'agent': agent_id,
            'message': message,
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'metadata': metadata or {}
        }
        self.main_conversation_history.append(msg_data)
        
        # 获取智能体信息
        agent_info = self.agents[agent_id]
        
        # 创建消息显示组件 - 大屏幕样式优化
        msg_pane = pn.pane.Markdown(
            f"{agent_info['avatar']} **{agent_info['name']}** `{msg_data['timestamp']}`\n\n{message}",
            styles={
                'background': agent_info['color'] + '20',
                'border-left': f"5px solid {agent_info['color']}",
                'padding': '10px', 
                'margin': '3px',
                'border-radius': '8px',
                'font-size': '18px',
                'max-height': '400px',
                'overflow-y': 'auto',
                'white-space': 'pre-wrap',
                'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'
            },
            sizing_mode='stretch_width'
        )
        self.main_chat_display.append(msg_pane)
        
        # 更新统计信息
        self.stats_display.object = self.get_stats_text()
        
    def clear_expert_discussion(self):
        """清空专家讨论区（每轮对话前调用）"""
        self.expert_chat_display.clear()
        self.expert_conversation_history = []
        
        # 添加讨论开始标识
        header_pane = pn.pane.Markdown(
            f"--- 新一轮专家讨论 `{datetime.now().strftime('%H:%M:%S')}` ---",
            styles={
                'text-align': 'center', 
                'color': '#666', 
                'font-style': 'italic', 
                'margin': '15px',
                'font-size': '16px'
            },
            sizing_mode='stretch_width'
        )
        self.expert_chat_display.append(header_pane)
        
    def add_expert_message(self, agent_id: str, message: str, metadata: Dict = None):
        """添加消息到专家讨论区"""
        if agent_id not in ['strategy', 'knowledge', 'empathy']:
            return
            
        msg_data = {
            'agent': agent_id,
            'message': message,
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'metadata': metadata or {}
        }
        self.expert_conversation_history.append(msg_data)
        
        # 获取智能体信息
        agent_info = self.agents[agent_id]
        
        # 创建消息显示组件 - 大屏幕样式优化
        msg_pane = pn.pane.Markdown(
            f"{agent_info['avatar']} **{agent_info['name']}** `{msg_data['timestamp']}`\n\n{message}",
            styles={
                'background': agent_info['color'] + '15',
                'border-left': f"4px solid {agent_info['color']}",
                'padding': '10px', 
                'margin': '5px',
                'border-radius': '6px',
                'font-size': '18px',
                'max-height': '350px',
                'overflow-y': 'auto',
                'white-space': 'pre-wrap',
                'box-shadow': '0 1px 3px rgba(0,0,0,0.1)'
            },
            sizing_mode='stretch_width'
        )
        self.expert_chat_display.append(msg_pane)
        
        # 更新统计信息
        self.stats_display.object = self.get_stats_text()
        
    def create_streaming_message_container(self, agent_id: str) -> pn.pane.Markdown:
        """创建流式输出的消息容器"""
        agent_info = self.agents[agent_id]
        
        # 创建初始消息容器 - 大屏幕样式优化
        msg_pane = pn.pane.Markdown(
            f"{agent_info['avatar']} **{agent_info['name']}** `{datetime.now().strftime('%H:%M:%S')}`\n\n_正在思考..._",
            styles={
                'background': agent_info['color'] + '20',
                'border-left': f"5px solid {agent_info['color']}",
                'padding': '10px', 
                'margin': '3px',
                'border-radius': '8px',
                'font-size': '18px',
                'max-height': '400px',
                'overflow-y': 'auto',
                'white-space': 'pre-wrap',
                'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'
            },
            sizing_mode='stretch_width'
        )
        
        return msg_pane
        
    def stream_message_to_container(self, container: pn.pane.Markdown, agent_id: str, message_stream: AsyncGenerator[str, None]):
        """将流式消息更新到容器中"""
        agent_info = self.agents[agent_id]
        timestamp = datetime.now().strftime("%H:%M:%S")
        accumulated_text = ""
        
        for chunk in message_stream:
            accumulated_text += chunk
            # 更新容器内容
            container.object = f"{agent_info['avatar']} **{agent_info['name']}** `{timestamp}`\n\n{accumulated_text}"
            # 短暂延时以显示流式效果

            
        # 保存完整消息到历史记录
        if agent_id in ['user', 'persuader']:
            msg_data = {
                'agent': agent_id,
                'message': accumulated_text,
                'timestamp': timestamp,
                'metadata': {}
            }
            self.main_conversation_history.append(msg_data)
        elif agent_id in ['strategy', 'knowledge', 'empathy']:
            msg_data = {
                'agent': agent_id,
                'message': accumulated_text,
                'timestamp': timestamp,
                'metadata': {}
            }
            self.expert_conversation_history.append(msg_data)
            
        return accumulated_text
    def stream_real_llm_to_container_st(self, container: pn.pane.Markdown, agent_id: str, agent_instance,query,prompt="You are a helpful assistant"):
        """将真实LLM的流式输出更新到容器中"""
        agent_info = self.agents[agent_id]
        timestamp = datetime.now().strftime("%H:%M:%S")
        accumulated_text = ""
        
        try:
            # 调用真实的LLM流式API
            response = agent_instance.llm.client.chat.completions.create(
                model="deepseek-chat",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": query},
                    ],
                stream=True
            )
            
            # 实时处理流式响应
            for chunk in response:
                if chunk.choices[0].delta.content:
                    chunk_text = chunk.choices[0].delta.content
                    accumulated_text += chunk_text
                    
                    # 即时更新UI容器
                    container.object = f"{agent_info['avatar']} **{agent_info['name']}** `{timestamp}`\n\n{accumulated_text}"
                    


                    
        except Exception as e:
            error_msg = f"流式输出错误: {str(e)}"
            accumulated_text = error_msg
            container.object = f"{agent_info['avatar']} **{agent_info['name']}** `{timestamp}`\n\n{accumulated_text}"
        
        # 保存完整消息到历史记录
        if agent_id in ['user', 'persuader']:
            msg_data = {
                'agent': agent_id,
                'message': accumulated_text,
                'timestamp': timestamp,
                'metadata': {}
            }
            self.main_conversation_history.append(msg_data)
        elif agent_id in ['strategy', 'knowledge','empathy']:

            msg_data = {
                'agent': agent_id,
                'message': accumulated_text,
                'timestamp': timestamp,
                'metadata': {}
            }
            self.expert_conversation_history.append(msg_data)
            
        return accumulated_text  
    def stream_real_llm_to_container_mt(self, container: pn.pane.Markdown, agent_id: str, agent_instance, history: List[Dict]):
        """将真实LLM的流式输出更新到容器中"""
        agent_info = self.agents[agent_id]
        timestamp = datetime.now().strftime("%H:%M:%S")
        accumulated_text = ""
        
        try:
            # 调用真实的LLM流式API
            response = agent_instance.llm.client.chat.completions.create(
                model="deepseek-chat",
                messages=history,
                stream=True
            )
            
            # 实时处理流式响应
            for chunk in response:
                if chunk.choices[0].delta.content:
                    chunk_text = chunk.choices[0].delta.content
                    accumulated_text += chunk_text
                    
                    # 即时更新UI容器
                    container.object = f"{agent_info['avatar']} **{agent_info['name']}** `{timestamp}`\n\n{accumulated_text}"
                    

                    
        except Exception as e:
            error_msg = f"流式输出错误: {str(e)}"
            accumulated_text = error_msg
            container.object = f"{agent_info['avatar']} **{agent_info['name']}** `{timestamp}`\n\n{accumulated_text}"
        
        # 保存完整消息到历史记录
        if agent_id in ['user', 'persuader']:
            msg_data = {
                'agent': agent_id,
                'message': accumulated_text,
                'timestamp': timestamp,
                'metadata': {}
            }
            self.main_conversation_history.append(msg_data)
        elif agent_id in ['strategy', 'knowledge','empathy']:

            msg_data = {
                'agent': agent_id,
                'message': accumulated_text,
                'timestamp': timestamp,
                'metadata': {}
            }
            self.expert_conversation_history.append(msg_data)
            
        return accumulated_text
    def handle_user_message(self, event):
        """处理用户消息"""
        user_message = self.user_input.value.strip()
        if not user_message:
            return
            
        # 更新状态
        self.status_indicator.object = "**系统状态:** 处理中..."
        self.send_button.disabled = True
        
        # 添加用户消息到主对话框
        self.add_main_message('user', user_message)
        if user_message.upper() == "ACCEPT":
            self.persuader.history.append({"role": "user", "content": "ACCEPT"})
            self.add_system_message("用户已被说服！对话结束。")
            self.finalize_conversation()
            return       
        # 清空输入框
        self.user_input.value = ""
        if user_message.upper() == "FINISH":
            self.persuader.history.append({"role": "user", "content": "FINISH"})
            self.add_system_message("用户终止对话！对话结束。")
            self.finalize_conversation()
            return       
        # 清空输入框
        self.user_input.value = ""        
        try:
            # 调用智能体处理流程
            self.process_conversation(user_message)
        except Exception as e:
            self.add_system_message(f"处理消息时发生错误: {str(e)}")
        finally:
            # 恢复状态
            self.status_indicator.object = "**系统状态:** 就绪"
            self.send_button.disabled = False
            
    def process_conversation(self, user_message: str):
        """处理对话流程"""
        # 清空专家讨论区，开始新一轮讨论
        self.clear_expert_discussion()
        if user_message:
                self.persuader.history.append({"role": "user", "content": user_message})       
       
        self.status_indicator.object = "**系统状态:** 更新用户画像中...(心理专家)"
        #self.add_system_message("正在更新用户画像...")
        #mode = self.persuader.judeg_complex(user_message)
        #if mode == 1:
        self.persuader.set_user_profile(user_message)
        self.persuader.emo = self.persuader.emo_recgonition(user_message)
        # 1. 策略专家分析（流式输出到专家区）
        self.status_indicator.object = "**系统状态:** 策略专家分析中...选择策略注入对话"
        strategy_container = self.create_streaming_message_container('strategy')
        self.expert_chat_display.append(strategy_container)       
        strategy_response = self.get_real_strategy_response_stream(strategy_container, user_message)
        
        # 2. 知识专家提供信息（流式输出到专家区）
        self.status_indicator.object = "**系统状态:** 知识专家分析中...调用rag,web_search整理论据"
        knowledge_container = self.create_streaming_message_container('knowledge')
        self.expert_chat_display.append(knowledge_container)       
        knowledge_response = self.get_real_knowledge_response_stream(knowledge_container, user_message)
        appendix = '你需要采取下面的策略：'+strategy_response+'并结合下面的知识：'+knowledge_response
        self.persuader.history[0]['content']=f"你是一个说服专家,你需要说服对方支持{topic}"+appendix

        
        
        # 3. 说服者综合回复（流式输出到主对话框）
        self.status_indicator.object = "**系统状态:** 说服者回复中..."
        persuader_container = self.create_streaming_message_container('persuader')
        self.main_chat_display.append(persuader_container)
        
        persuader_response =  self.get_last_response_stream(persuader_container)
       
    def get_real_strategy_response_stream(self, container: pn.pane.Markdown, user_message: str) -> str:
        """获取真实的策略专家流式响应"""
        try:
            
            # 使用真实的流式LLM调用
            response = self.stream_real_llm_to_container_st(
                container, 'strategy', self.strategy_expert, user_message,local_strategy
            )
            #self.persuader.history.append({"role": "assistant", "content": response})
            return response
        except Exception as e:
            error_msg = f"策略专家响应生成失败: {str(e)}"
            container.object = f"🎯 **策略专家** `{datetime.now().strftime('%H:%M:%S')}`\n\n{error_msg}"
    def get_real_knowledge_response_stream(self, container: pn.pane.Markdown, user_message: str) -> str:
        """获取真实的知识专家流式响应"""
        try:
            
            # 使用真实的流式LLM调用
            response = self.stream_real_llm_to_container_st(
                container, 'knowledge', self.knowledge_expert, user_message,get_knowledge
            )
            #self.persuader.history.append({"role": "assistant", "content": response})
            return response
        except Exception as e:
            error_msg = f"知识专家响应生成失败: {str(e)}"
            container.object = f"📚  **知识专家** `{datetime.now().strftime('%H:%M:%S')}`\n\n{error_msg}"   
    def get_first_response_stream(self, container: pn.pane.Markdown, user_message: str) -> str:
        """获取初始询问的响应"""
        try:          
            # 使用真实的流式LLM调用
            response = self.stream_real_llm_to_container_st(
                container, 'persuader', self.persuader, user_message,"You are a helpful assistant"
            )
            self.persuader.history.append({"role": "assistant", "content": response})
            return response
        except Exception as e:
            error_msg = f"初始响应生成失败: {str(e)}"
            container.object = f"💬 **说服者** `{datetime.now().strftime('%H:%M:%S')}`\n\n{error_msg}"   

    def get_last_response_stream(self, container: pn.pane.Markdown) -> str:
        """获取最终响应"""
        init_response =  self.persuader.llm.mt_chat(self.persuader.history,out=False)
        print(init_response)
        try:
            match self.persuader.emo:
                case 1:
                    emo_infect = '你是一个语言学家，参照要求把下面的内容润色，使其变成更加贴近真实人类对话的内容，语气生动平缓，逻辑清晰，如果需要的话可以适当夹杂一些语气词，尽量减少列表等形式的输出，但是不能改变原本对话的意思，不要有多余的输出\n###注意：使用“共情”+“尊重差异”的语气，避免强硬推理'
                    emo_display = '愤怒 / 防御:使用“共情”+“尊重差异”的语气，避免强硬推理'
                case 2:
                    emo_infect = '你是一个语言学家，参照要求把下面的内容润色，使其变成更加贴近真实人类对话的内容，语气生动平缓，逻辑清晰，如果需要的话可以适当夹杂一些语气词，尽量减少列表等形式的输出，但是不能改变原本对话的意思，不要有多余的输出\n###注意：激发兴趣点，用类比/故事拉近距离'  
                    emo_display = '冷漠 / 怀疑:激发兴趣点，用类比/故事拉近距离'
                case 3:
                    emo_infect = '你是一个语言学家，参照要求把下面的内容润色，使其变成更加贴近真实人类对话的内容，语气生动平缓，逻辑清晰，如果需要的话可以适当夹杂一些语气词，尽量减少列表等形式的输出，但是不能改变原本对话的意思，不要有多余的输出\n###注意：乘胜追击，引入更多逻辑证据巩固立场'
                    emo_display = '共鸣 / 被理解:乘胜追击，引入更多逻辑证据巩固立场'
                case 4:
                    emo_infect = '你是一个语言学家，参照要求把下面的内容润色，使其变成更加贴近真实人类对话的内容，语气生动平缓，逻辑清晰，如果需要的话可以适当夹杂一些语气词，尽量减少列表等形式的输出，但是不能改变原本对话的意思，不要有多余的输出\n###注意：提供选择空间，引导用户表达理由，有助于认知调整'
                    emo_display = '矛盾 / 反思:提供选择空间，引导用户表达理由，有助于认知调整'
                case 5:
                    emo_infect = '你是一个语言学家，参照要求把下面的内容润色，使其变成更加贴近真实人类对话的内容，语气生动平缓，逻辑清晰，如果需要的话可以适当夹杂一些语气词，尽量减少列表等形式的输出，但是不能改变原本对话的意思，不要有多余的输出\n###注意：简化信息结构，使用图示或明确类比，帮助理解'
                    emo_display = '焦虑 / 困惑:简化信息结构，使用图示或明确类比，帮助理'
            self.add_expert_message('empathy', emo_display)
            # 使用真实的流式LLM调用
            response =  self.stream_real_llm_to_container_st(
                container, 'persuader', self.persuader, init_response,emo_infect
            )
            self.persuader.history.append({"role": "assistant", "content": response})
            return response
        except Exception as e:
            error_msg = f"说服者响应生成失败: {str(e)}"
            container.object = f"💬 **说服者** `{datetime.now().strftime('%H:%M:%S')}`\n\n{error_msg}"    
    # ============ 辅助方法 ============
    
    def clear_conversation(self, event):
        """清空所有对话历史"""
        self.main_conversation_history = []
        self.expert_conversation_history = []
        self.main_chat_display.clear()
        self.expert_chat_display.clear()
        self.current_turn = 0
        self.add_system_message("对话已清空，请开始新的对话。")
        self.status_indicator.object = "**系统状态:** 说服者准备中..."
        self.stats_display.object = self.get_stats_text()

        self.add_system_message(f"系统初始化完成，主题：是否{topic}")        
        new_container = self.create_streaming_message_container('persuader')
        self.main_chat_display.append(new_container)
        self.get_first_response_stream(new_container, f'你是一个说服专家，你的目的是说服对方支持{topic}，请你先问候对方，然后生成一段话来首先开启这个话题，简单的介绍背景并引起对话者沟通的兴趣，注意：只要按要求输出内容即可，不要有多余的输出,也不要解释')      
        self.status_indicator.object = "**系统状态:** 就绪"
  
    def get_conversation_context(self, last_n: int = 5) -> Dict[str, List[Dict]]:
        """获取最近的对话上下文"""
        return {
            'main': self.main_conversation_history[-last_n:] if len(self.main_conversation_history) > last_n else self.main_conversation_history,
            'expert': self.expert_conversation_history[-last_n:] if len(self.expert_conversation_history) > last_n else self.expert_conversation_history
        }
    
    def export_conversation(self) -> str:
        """导出对话历史为JSON格式"""
        return json.dumps({
            'main_conversation': self.main_conversation_history,
            'expert_discussion': self.expert_conversation_history
        }, ensure_ascii=False, indent=2)
    def finalize_conversation(self):
        """结束对话并保存记录"""
        try:
            if self.persuader:
                # 显示用户代理信息
                self.add_system_message("正在保存对话记录...")
                
                # 调用原始的record函数保存历史
                record(self.persuader.history)
                
                self.add_system_message("对话记录已保存。")
            
            # 禁用输入
            self.send_button.disabled = True
            self.user_input.disabled = True
            
        except Exception as e:
            self.add_system_message(f"保存对话记录时发生错误: {str(e)}")    
    def create_layout(self):
        """创建应用布局 - 大屏幕适配版本"""
        # 左侧面板 - 主对话区域（适配大屏幕）
        left_panel = pn.Column(
            pn.pane.Markdown("## 💬 主对话区（用户 ↔ 说服者）", 
                           styles={
                               'text-align': 'center', 
                               'font-size': '22px',
                               'margin': '15px 0',
                               'color': '#2c3e50'
                           }),
            self.main_chat_display,
            pn.Row(
                self.user_input,
                pn.Column(
                    self.send_button, 
                    #self.clear_button,
                    styles={'margin': '0 10px'}
                ),
                sizing_mode='stretch_width',
                styles={'margin': '10px 0'}
            ),
            sizing_mode='stretch_width',
            min_width=600,
            styles={'padding': '10px'}
        )
        
        # 右侧上方面板 - 专家讨论区域（适配大屏幕）
        expert_panel = pn.Column(
            self.expert_title,
            self.expert_chat_display,
            sizing_mode='stretch_width',
            min_width=400,
            styles={'padding': '10px'}
        )
        
        # 右侧下方面板 - 状态和统计（适配大屏幕）
        info_panel = pn.Column(
            self.status_indicator,
            pn.Spacer(height=10),
            pn.pane.Markdown("## 📋 智能体说明"),
            pn.pane.Markdown("""**专家讨论区：**
            🎯 策略专家：分析策略 📚 知识专家：提供信息 🧠心理专家:情感支持           
            **主对话区：**
            👤 用户：提出问题  💬 说服者：综合回复
            """, styles={
                'font-size': '15px',
                'background': '#f8f9fa',
                'padding': '15px',
                'border-radius': '8px',
                'border': '1px solid #dee2e6'
            }),
            pn.pane.Markdown("## 📊 系统信息"),
            self.stats_display,
            sizing_mode='stretch_width',
            min_width=400,
            height=350,
            styles={'padding': '10px'}
        )
        
        # 右侧整体布局（适配大屏幕）
        right_panel = pn.Column(
            expert_panel,
            info_panel,
            sizing_mode='stretch_both',
            min_width=400
        )
        
        # 整体布局 - 响应式设计
        main_row = pn.Row(
            left_panel, 
            right_panel, 
            sizing_mode='stretch_width',
            min_height=800,
            styles={'padding': '20px'}
        )
        
        # 使用MaterialTemplate，适配大屏幕
        return pn.template.MaterialTemplate(
            title='🤖 智能体对话系统1a',
            main=[main_row],
            header_background='#2F4F4F',
            sidebar_width=0,  # 移除侧边栏
            main_max_width="",  # 移除最大宽度限制
        )

# 创建应用实例
def create_app(topic):
    """创建Panel应用"""
    chat_system = MultiAgentChatSystem(topic)
    return chat_system.create_layout()


# 如果直接运行此文件，启动应用
if __name__ == "__main__":
    # 使用基础版本
    #top = input("topic-1,2,3,4\n")
    top = "1"
    match top:
        case '1':
            topic = "对公众开放校园"
        case "2":
            topic = "博物馆免费开放"
        case "3":
            topic ="单位停车场对外开放"
        case "4" :
            topic ="图书馆24小时开放"
    local_strategy = f'''你是一个策略专家，你正在参与辅助对用户进行说服，使其支持{topic}，你需要根据对话者的输入，从下面的策略中选择1到2个最合适的策略，然后返回策略的名字以及后面的解释，注意按照要求输出内容，不要有多余的输出
#1.Evidence-based argumentation:一种通过引用可靠数据、研究结果或事实来支持论点的说服策略，以此增强逻辑可信度和客观性。
#2.logical appeal:一种通过理性推理、事实和证据来构建论点，从而说服听众的说服策略，强调因果、一致性和无矛盾性。
#3.expert endorsement:通过引用权威专家、学者或可信机构的观点或研究来增强论点的可信度和说服力。
#4.non-experter testimonial:通过普通用户、消费者或亲历者的真实体验和评价来增强产品或观点的可信度和情感共鸣。
#5.foot in the door:先让对方同意一个小请求，再逐步提出更大要求，利用人们保持行为一致的心理倾向来增加顺从度。
#6.door inthe face:先提出一个夸张的大请求（预期被拒），再提出较小的真实请求，利用对方的让步心理提高接受度。
#7.Priming:通过预先暴露特定信息、图像或情境来无意识地影响后续行为或判断的说服策略，利用大脑的联想机制激活相关概念。
#8.storytelling:通过构建有情感共鸣、角色代入和情节张力的叙事来传递观点或信息的说服策略，利用人类大脑对故事的天然偏好来增强记忆点与说服力。


'''
    get_knowledge = f'你是一个知识专家，你正帮助说服专家进行说服，目标是使对话者支持{topic}，你需要针对对话者的内容提供相关的知识给对方，你需要提供的知识应当与用户谈到的内容密切相关，尽量简洁精炼，同时你需要避免重复提供相同的知识,如果对话者的内容比较空，没什么可以总结的，那就返回“没有需要补充的”。注意：你只需要提供知识，不要有多余的输出，也不要发表自己的意见或评论.'
    
    app = create_app(topic)
    
    pn.serve(app, port=5007, show=True, title="智能体说服对话系统")
    #pn.serve(app, port=5007,  address='0.0.0.0',show=True, title="多智能体说服对话系统",allow_websocket_origin=["8.155.25.163:5007"])