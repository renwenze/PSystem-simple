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
import requests
import json
import time

# 启用Panel服务
pn.extension('tabulator', 'ace', 'bokeh')

class MultiAgentChatSystem:
    def __init__(self,topic):
        self.agents = {
            'user': {'name': '用户', 'color': '#3498db', 'avatar': '👤'},
            'persuader': {'name': '说服者', 'color': '#f39c12', 'avatar': '💬'},
            'empathy':{'name':'心理专家','color':'#9b59b6','avatar':'🧠'},
            'knowledge': {'name': '知识专家', 'color': '#2ecc71', 'avatar': '📚'}
        }
        
        self.main_conversation_history = []  # 用户与说服者的对话
        self.knowledge_history = []  # 专家讨论历史
        self.empathy_history = []  # 专家讨论历史
        self.current_turn = 0
        self.init_agents()
        # 创建UI组件
        self.setup_ui()
    def init_agents(self):
        """初始化智能体"""
        self.persuader = UserProxy('用户', topic,'MAS')
        self.empathy_expert = StrategyAgent(topic) 
        self.knowledge_expert = KnowledgeAgent(topic)


    def setup_ui(self):
        """设置用户界面 - 紧凑版本"""
        # 标题 - 更小的边距
        #self.title = pn.pane.Markdown("# 🤖 知识型对话生成系统", styles={'text-align': 'center', 'font-size': '24px', 'margin': '10px 0'})
        
        # 主对话显示区域（用户 + 说服者） - 增大高度
        self.main_chat_display = pn.Column(
            height=650, 
            sizing_mode='stretch_width',
            scroll=True,
            styles={
                'border': '2px solid #ddd', 
                'padding': '15px', 
                'background': '#f8f9fa',
                'border-radius': '8px',
                'margin': '5px'
            }
        )
        
        # 专家讨论区域 - 减小高度，更紧凑
        self.expert_chat_display1 = pn.Column(
            height=180, 
            sizing_mode='stretch_width',
            scroll=True,
            styles={
                'border': '2px solid #ddd', 
                'padding': '10px', 
                'background': '#fafafa',
                'border-radius': '8px',
                'margin': '5px'
            }
        )

        self.expert_chat_display2 = pn.Column(
            height=400, 
            sizing_mode='stretch_width',
            scroll=True,
            styles={
                'border': '2px solid #ddd', 
                'padding': '10px', 
                'background': '#fafafa',
                'border-radius': '8px',
                'margin': '5px'
            }
        )
        
        # 专家讨论标题 - 更小字体和边距
        self.expert_title1 = pn.pane.Markdown("## 复杂自然语言理解", 
                                           styles={
                                               'text-align': 'center', 
                                               'font-size': '16px',
                                               'margin': '5px 0',
                                               'font-weight': 'bold'
                                           })
        self.expert_title2 = pn.pane.Markdown("## 外源知识引用", 
                                           styles={
                                               'text-align': 'center', 
                                               'font-size': '16px',
                                               'margin': '5px 0',
                                               'font-weight': 'bold'
                                           })       
        # 用户输入区域 - 减小高度
        self.user_input = pn.widgets.TextAreaInput(
            placeholder="请输入您的消息......",
            height=80,
            sizing_mode='stretch_width',
            max_length=1000,
            styles={'font-size': '16px'}
        )
        
        # 按钮样式优化 - 更紧凑
        button_style = {
            'font-size': '13px',
            'padding': '8px 15px',
            'margin': '3px'
        }
        
        # 发送按钮
        self.send_button = pn.widgets.Button(
            name="发送消息", 
            button_type="primary",
            width=100,
            height=80,
            styles=button_style
        )
        
        # 清空对话按钮
        self.clear_button = pn.widgets.Button(
            name="清空对话", 
            button_type="default",
            width=100,
            height=40,
            styles=button_style
        )
        
        # 系统状态显示 - 更紧凑
        self.status_indicator = pn.pane.Markdown("**系统状态:** 就绪")
        self.status_indicator.sizing_mode = 'stretch_width'
        self.status_indicator.styles = {
            'font-size': '14px',
            'padding': '8px',
            'font-weight': 'bold',
            'background': '#e8f4fd',
            'border-radius': '6px',
            'border': '1px solid #bee5eb',
            'margin': '5px 0'
        }
        
        # 流式输出的消息容器
        self.current_streaming_message = None
        
        # 绑定事件
        self.send_button.on_click(self.handle_user_message)
        self.clear_button.on_click(self.clear_conversation)
        self.user_input.param.watch(self.on_input_change, 'value')
        
        # 初始化欢迎消息
        self.add_system_message(f"系统初始化完成，主题：巴以冲突")
        
        first_container = self.create_streaming_message_container('persuader')
        self.main_chat_display.append(first_container)
        self.get_first_response_stream(first_container, f'你是一个说服专家，你的目的是说服对方支持{topic}，请你先问候对方，然后生成一段话来首先开启这个话题，简单的介绍背景并引起对话者沟通的兴趣，注意：只要按要求输出内容即可，不要有多余的输出,也不要解释')        
                    
        
    
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
        
        # 创建消息显示组件 - 更紧凑
        msg_pane = pn.pane.Markdown(
            f"🔔 **系统消息** `{msg_data['timestamp']}`\n\n{message}",
            styles={
                'background': '#f0f0f0', 
                'padding': '8px', 
                'margin': '3px', 
                'border-radius': '6px',
                'font-size': '15px',
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
        
        # 创建消息显示组件 - 更紧凑
        msg_pane = pn.pane.Markdown(
            f"{agent_info['avatar']} **{agent_info['name']}** `{msg_data['timestamp']}`\n\n{message}",
            styles={
                'background': agent_info['color'] + '20',
                'border-left': f"4px solid {agent_info['color']}",
                'padding': '8px', 
                'margin': '3px',
                'border-radius': '6px',
                'font-size': '15px',
                'max-height': '350px',
                'overflow-y': 'auto',
                'white-space': 'pre-wrap',
                'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'
            },
            sizing_mode='stretch_width'
        )
        self.main_chat_display.append(msg_pane)
        
    def clear_expert_discussion(self):
        """清空专家讨论区（每轮对话前调用）"""
        self.expert_chat_display1.clear()
        self.expert_chat_display2.clear()
        self.knowledge_history = []
        self.empathy_history = []
        
    def add_expert_message1(self, agent_id: str, message: str, metadata: Dict = None):
        """添加消息到专家讨论区"""
        msg_data = {
            'message': message,
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'metadata': metadata or {}
        }
        self.empathy_history.append(msg_data)
        
        # 获取智能体信息
        agent_info = self.agents[agent_id]
        
        # 创建消息显示组件 - 更紧凑
        msg_pane = pn.pane.Markdown(
            f"{message}",
            styles={
                'background': agent_info['color'] + '15',
                'border-left': f"3px solid {agent_info['color']}",
                'padding': '8px', 
                'margin': '3px',
                'border-radius': '5px',
                'font-size': '14px',
                'max-height': '200px',
                'overflow-y': 'auto',
                'white-space': 'pre-wrap',
                'box-shadow': '0 1px 3px rgba(0,0,0,0.1)'
            },
            sizing_mode='stretch_width'
        )
        self.expert_chat_display1.append(msg_pane)

    def add_expert_message2(self, agent_id: str, message: str, metadata: Dict = None):
        """添加消息到专家讨论区"""
        msg_data = {
            'message': message,
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'metadata': metadata or {}
        }
        self.knowledge_history.append(msg_data)
        
        # 获取智能体信息
        agent_info = self.agents[agent_id]
        
        # 创建消息显示组件 - 更紧凑
        msg_pane = pn.pane.Markdown(
            f"{agent_info['avatar']} **{agent_info['name']}** `{msg_data['timestamp']}`\n\n{message}",
            styles={
                'background': agent_info['color'] + '15',
                'border-left': f"3px solid {agent_info['color']}",
                'padding': '8px', 
                'margin': '3px',
                'border-radius': '5px',
                'font-size': '14px',
                'max-height': '200px',
                'overflow-y': 'auto',
                'white-space': 'pre-wrap',
                'box-shadow': '0 1px 3px rgba(0,0,0,0.1)'
            },
            sizing_mode='stretch_width'
        )
        self.expert_chat_display2.append(msg_pane)       
 
    def create_streaming_message_container(self, agent_id: str) -> pn.pane.Markdown:
        """创建流式输出的消息容器"""
        agent_info = self.agents[agent_id]
        
        # 创建初始消息容器 - 更紧凑
        msg_pane = pn.pane.Markdown(
            "_正在思考..._",
            styles={
                'background': agent_info['color'] + '20',
                'border-left': f"4px solid {agent_info['color']}",
                'padding': '8px', 
                'margin': '3px',
                'border-radius': '6px',
                'font-size': '15px',
                'max-height': '350px',
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

            
        # 保存完整消息到历史记录
        if agent_id in ['user', 'persuader']:
            msg_data = {
                'agent': agent_id,
                'message': accumulated_text,
                'timestamp': timestamp,
                'metadata': {}
            }
            self.main_conversation_history.append(msg_data)
        elif agent_id in ['empathy']:
            msg_data = {
                'message': accumulated_text,
                'timestamp': timestamp,
                'metadata': {}
            }
            self.empatht_history.append(msg_data)
        elif agent_id in ['knowledge']:
            msg_data = {
                'message': accumulated_text,
                'timestamp': timestamp,
                'metadata': {}
            }
            self.knowledge_history.append(msg_data)   
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
                    if  agent_info['name'] == '说服者':
                         container.object = f"{agent_info['avatar']} **{agent_info['name']}** `{timestamp}`\n\n{accumulated_text}"
                    else:
                        container.object = f"{accumulated_text}"

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
        elif agent_id in ['empathy']:
            msg_data = {
                'message': accumulated_text,
                'timestamp': timestamp,
                'metadata': {}
            }
            self.empathy_history.append(msg_data)
        elif agent_id in ['knowledge']:
            msg_data = {
                'agent': agent_id,
                'message': accumulated_text,
                'timestamp': timestamp,
                'metadata': {}
            }
            self.knowledge_history.append(msg_data)    
        return accumulated_text  
    


    def stream_rag_to_container_st(self, container: pn.pane.Markdown, agent_id: str, query, prompt="You are a helpful assistant"):
        """将RAG API的流式输出更新到容器中"""
        agent_info = self.agents[agent_id]
        timestamp = datetime.now().strftime("%H:%M:%S")
        accumulated_text = ""
        accumulated_context = ""
        context = ""
        answer=""
        
        # API配置
        api_url = 'http://114.55.231.13:8088/v1/workflows/run'
        api_key = 'app-1XjEoCKcbj5KEdgBKrXyfuTa'
        
        try:
            # 请求数据
            data = {
                "inputs": {
                    "query": query
                },
                "response_mode": "streaming",
                "user": "difyuser"
            }
            
            # 请求头
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # 发送POST请求
            response = requests.post(api_url, headers=headers, data=json.dumps(data), stream=True)
            
            if response.status_code == 200:
                # 实时处理流式响应
                for line in response.iter_lines(decode_unicode=True):
                    if line:
                        try:
                            # 去除"data: "前缀
                            if line.startswith("data: "):
                                line = line[6:]
                            
                            event_data = json.loads(line)
                            
                            # 提取context（检索结果）
                            try:
                                contexts = event_data['data']['outputs']['result']
                                for item in contexts:
                                    accumulated_context += item['content']
                                
                                # 即时更新UI容器（显示context）
                                container.object = f"{accumulated_context}"
                            except:
                                pass
                            
                            # 提取answer（虽然不显示，但可以保存）
                            try:
                                text = event_data['data']['text']
                                answer += text
                            except:
                                pass
                                
                        except json.JSONDecodeError:
                            # 跳过非JSON格式的行
                            pass
            else:
                error_msg = f"RAG API请求失败: 状态码 {response.status_code}"
                accumulated_context = error_msg
                container.object = f"{agent_info['avatar']} **{agent_info['name']}** `{timestamp}`\n\n{accumulated_context}"
                
        except Exception as e:
            error_msg = f"流式输出错误: {str(e)}"
            accumulated_context = error_msg
            container.object = f"{agent_info['avatar']} **{agent_info['name']}** `{timestamp}`\n\n{accumulated_context}"
        
        # 保存完整消息到历史记录（保存context）
        if agent_id in ['user', 'persuader']:
            msg_data = {
                'agent': agent_id,
                'message': accumulated_context,  # 保存context而不是answer
                'timestamp': timestamp,
                'metadata': {'answer': answer}  # 可选：将answer保存到metadata
            }
            self.main_conversation_history.append(msg_data)
        elif agent_id in ['empathy']:
            msg_data = {
                'message': accumulated_context,
                'timestamp': timestamp,
                'metadata': {'answer': answer}
            }
            self.empathy_history.append(msg_data)
        elif agent_id in ['knowledge']:
            msg_data = {
                'agent': agent_id,
                'message': accumulated_context,
                'timestamp': timestamp,
                'metadata': {'answer': answer}
            }
            self.knowledge_history.append(msg_data)
        
        return accumulated_context  # 返回context而不是answer

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
                    container.object = f"{accumulated_text}"

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
        elif agent_id in ['empathy']:
            msg_data = {
                'agent': agent_id,
                'message': accumulated_text,
                'timestamp': timestamp,
                'metadata': {}
            }
            self.empathy_history.append(msg_data)
        elif agent_id in ['knowledge']:
            msg_data = {
                'agent': agent_id,
                'message': accumulated_text,
                'timestamp': timestamp,
                'metadata': {}
            }
            self.knowledge_history.append(msg_data)    
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
        print("clear")  
       
        # 1. 策略专家分析（流式输出到专家区）
        self.status_indicator.object = "**系统状态:** 情感专家分析中...调用复杂自然语言理解"
        empathy_container = self.create_streaming_message_container('empathy')
        self.expert_chat_display1.append(empathy_container)       
        empathy_response = self.get_real_empathy_response_stream(empathy_container, user_message)
        
        # 2. 知识专家提供信息（流式输出到专家区）
        self.status_indicator.object = "**系统状态:** 知识专家分析中...调用外源知识引用"
        knowledge_container = self.create_streaming_message_container('knowledge')
        self.expert_chat_display2.append(knowledge_container)       
        knowledge_response = self.get_real_knowledge_response_stream(knowledge_container, user_message)
        appendix = '这是对话者的态度：'+empathy_response+'这是你需要结合的数据：'+knowledge_response+f"你的目的是说服对方支持{topic}"
        self.persuader.history[0]['content']=f"你是一个说服专家,你需要说服对方支持{topic}"+appendix
        
        # 3. 说服者综合回复（流式输出到主对话框）
        self.status_indicator.object = "**系统状态:** 说服者回复中..."
        persuader_container = self.create_streaming_message_container('persuader')
        self.main_chat_display.append(persuader_container)
        
        persuader_response = self.get_last_response_stream(persuader_container)
       
    def get_real_empathy_response_stream(self, container: pn.pane.Markdown, user_message: str) -> str:
        """获取真实的策略专家流式响应"""
        try:
            # 使用真实的流式LLM调用
            response = self.stream_real_llm_to_container_st(
                container, 'empathy', self.empathy_expert, user_message, local_strategy
            )
            return response
        except Exception as e:
            error_msg = f"策略专家响应生成失败: {str(e)}"
            container.object = f"🎯 **策略专家** `{datetime.now().strftime('%H:%M:%S')}`\n\n{error_msg}"
    
    def get_real_knowledge_response_stream(self, container: pn.pane.Markdown, user_message: str) -> str:
        """获取真实的知识专家流式响应"""
        try:
            # 使用真实的流式LLM调用
            #response = self.stream_real_llm_to_container_st(
            response = self.stream_rag_to_container_st(
                container, 'knowledge', user_message, get_knowledge
            )
            return response
        except Exception as e:
            error_msg = f"知识专家响应生成失败: {str(e)}"
            container.object = f"📚  **知识专家** `{datetime.now().strftime('%H:%M:%S')}`\n\n{error_msg}"   
    
    def get_first_response_stream(self, container: pn.pane.Markdown, user_message: str) -> str:
        """获取初始询问的响应"""
        try:          
            # 使用真实的流式LLM调用
            response = self.stream_real_llm_to_container_st(
                container, 'persuader', self.persuader, user_message, "You are a helpful assistant"
            )
            self.persuader.history.append({"role": "assistant", "content": response})
            return response
        except Exception as e:
            error_msg = f"初始响应生成失败: {str(e)}"
            container.object = f"💬 **说服者** `{datetime.now().strftime('%H:%M:%S')}`\n\n{error_msg}"   

    def get_last_response_stream(self, container: pn.pane.Markdown) -> str:
        """获取最终响应"""
        init_response = self.persuader.llm.mt_chat(self.persuader.history, out=False)
        print(init_response)
        emo_infect = '你是一个语言学家，参照要求把下面的内容润色，使其变成更加贴近真实人类对话的内容，语气生动平缓，逻辑清晰，如果需要的话可以适当夹杂一些语气词，尽量减少列表等形式的输出，但是不能改变原本对话的意思，不要有多余的输出\n###注意：使用"共情"+"尊重差异"的语气，避免强硬推理'
        try:
            # 使用真实的流式LLM调用
            response = self.stream_real_llm_to_container_st(
                container, 'persuader', self.persuader, init_response, emo_infect
            )
            self.persuader.history.append({"role": "assistant", "content": response})
            return response
        except Exception as e:
            error_msg = f"说服者响应生成失败: {str(e)}"
            container.object = f"💬 **说服者** `{datetime.now().strftime('%H:%M:%S')}`\n\n{error_msg}"    
    
    def clear_conversation(self, event):
        """清空所有对话历史"""
        self.main_conversation_history = []
        self.empathy_history = []
        self.knowledge_history = []
        self.main_chat_display.clear()
        self.expert_chat_display1.clear()
        self.expert_chat_display2.clear()
        self.current_turn = 0
        self.add_system_message("对话已清空，请开始新的对话。")
        self.status_indicator.object = "**系统状态:** 说服者准备中..."

        self.add_system_message(f"系统初始化完成，主题：巴以冲突")        
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
        """创建应用布局 - 紧凑版本，左侧主对话框更大"""
        # 左侧面板 - 主对话区域（占据更大空间）
        left_panel = pn.Column(
            pn.pane.Markdown("## 💬 主对话区", 
                           styles={
                               'text-align': 'center', 
                               'font-size': '18px',
                               'margin': '5px 0',
                               'color': '#2c3e50'
                           }),
            self.main_chat_display,
            pn.Row(
                self.user_input,
                pn.Column(
                    self.send_button, 
                    styles={'margin': '0 5px'}
                ),
                sizing_mode='stretch_width',
                styles={'margin': '5px 0'}
            ),
            sizing_mode='stretch_width',
            styles={'padding': '5px'}
        )
        stance  = "反对"
        emotion = "消极"
        scene   = "政治"
        stance_pane  = pn.pane.Markdown(
            f"**立场分类：** **{stance}**",
            styles={
                "background": "#FFE5E5",   # 淡红
                "padding": "8px 12px",
                "border-radius": "6px",
                "font-size": "16px",
                "margin": "0"
            },
            sizing_mode='stretch_width'
        )
        emotion_pane = pn.pane.Markdown(
            f"**情感分类：** **{emotion}**",
            styles={
                "background": "#E5F2FF",   # 淡蓝
                "padding": "8px 12px",
                "border-radius": "6px",
                "font-size": "16px",
                "margin": "0"
            },
            sizing_mode='stretch_width'
        )
        scene_pane = pn.pane.Markdown(
            f"**场景分类：** **{scene}**",
            styles={
                "background": "#E5FFE5",   # 淡绿
                "padding": "8px 12px",
                "border-radius": "6px",
                "font-size": "16px",
                "margin": "0"
            },
            sizing_mode='stretch_width'
        )
        # 右侧上方面板 - 专家讨论区域1
        expert_panel1 = pn.Column(
            self.expert_title1,
            #self.expert_chat_display1,
            emotion_pane,
            stance_pane,
            scene_pane,
            sizing_mode='stretch_width',
            styles={'padding': '5px'}
        )
        
        # 右侧下方面板 - 专家讨论区域2
        expert_panel2 = pn.Column(
            self.expert_title2,
            self.expert_chat_display2,
            sizing_mode='stretch_width',
            styles={'padding': '5px'}
        )
        
        # 状态信息面板
        info_panel = pn.Column(
            self.status_indicator,
            sizing_mode='stretch_width',
            styles={'padding': '5px'}
        )
        
        # 右侧整体布局（专家区域 + 状态）
        right_panel = pn.Column(
            expert_panel1,
            expert_panel2,
            info_panel,
            sizing_mode='stretch_width',
            styles={'padding': '5px'}
        )
        
        # 整体布局 - 左右分栏，使用GridSpec实现比例布局
        main_layout = pn.GridSpec(sizing_mode='stretch_both', height=800)
        
        # 左侧占8列，右侧占4列（约2:1比例）
        main_layout[0:1, 0:8] = left_panel
        main_layout[0:1, 8:14] = right_panel
        
        # 使用BootstrapTemplate，更简洁紧凑
        template = pn.template.BootstrapTemplate(
            title='🤖 知识型对话生成系统',
            header_background='#34495e',
            sidebar_width=0,
        )
        
        template.main.append(
            pn.Column(
                #self.title,
                main_layout,
                sizing_mode='stretch_both'
            )
        )
        
        return template

# 创建应用实例
def create_app(topic):
    """创建Panel应用"""
    chat_system = MultiAgentChatSystem(topic)
    return chat_system.create_layout()


# 如果直接运行此文件，启动应用
if __name__ == "__main__":
    # 使用基础版本

    topic = "巴勒斯坦在巴以冲突中的立场"

    
    local_strategy = f'''你是一个心理专家，你正在参与辅助对用户进行说服，使其支持{topic}，你需要根据对话者的输入做判断，输出以下内容：
    1.立场：判断用户对巴以冲突中的巴勒斯坦方是支持还是反对（无法判断就默认是反对）
    2.情感：判断用户的情感是积极，消极，或者是中性（无法判断就默认是中性）
    3.场景：判断谈话的场景属于政治，伦理，科技等类别中的一个类别（无法判断就默认是政治）
    ###例子
    输入：我觉得我们应该支持以色列
    输出： 立场：反对
          情感：中性
          场景：政治 
'''
    
    get_knowledge = f'你是一个知识专家，你正帮助说服专家进行说服，目标是使对话者支持{topic}，你需要针对对话者的内容提供相关的知识给说服专家，你需要提供的知识应当与用户谈到的内容密切相关，尽量内容丰富,注意：你只需要提供知识，不要有多余的输出，也不要发表自己的意见或评论.'
    
    app = create_app(topic)
    
    pn.serve(app, port=5007, show=True, title="知识型对话生成系统")