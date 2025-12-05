from openai import OpenAI
import json
from .config import API

class deepseek_api():
    '''
    deepseek api 调用
    '''
    # role: one of `system`, `user`, `assistant`, `tool`

    def __init__(self):

        self.client = OpenAI(api_key=API, base_url="https://api.deepseek.com")
        

    

    def __call__(self,query,prompt="You are a helpful assistant",out=True):
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": query},
                    ],
        stream = out
        )
        
        if out:
            fullresponse = ""
            for chunk in response:
                if chunk.choices[0].delta.content:  # 检查是否有新内容
                    print(chunk.choices[0].delta.content, end="", flush=True)
                    fullresponse += chunk.choices[0].delta.content
            return fullresponse
        else:
            return response.choices[0].message.content  
        # return response.choices[0].message.content  # if stream=True
        

    def model_list(self):
        print(self.client.models.list())

    def mt_chat_auto(self,query,history,out=True):
        history.append({"role": "user", "content": query})
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=history,
            stream=out
        )
        if out:
            print('\nMAS:')
            fullresponse = ""
            for chunk in response:
                if chunk.choices[0].delta.content:  # 检查是否有新内容
                    print(chunk.choices[0].delta.content, end="", flush=True)
                    fullresponse += chunk.choices[0].delta.content
            return fullresponse
        else:
            return response.choices[0].message.content
        #history.append({"role":"assistant","content":response.choices[0].message.content})
        #return response.choices[0].message.content
    def mt_chat(self,history,out=True):
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=history,
            stream=out
        )
        if out :
            print('\nMAS:')
            fullresponse = ""
            for chunk in response:
                if chunk.choices[0].delta.content:  # 检查是否有新内容
                    print(chunk.choices[0].delta.content, end="", flush=True)
                    fullresponse += chunk.choices[0].delta.content
            return fullresponse
        else:
            return response.choices[0].message.content
        #return response.choices[0].message.content
    
    def search_surplus(this):
        url = "https://api.deepseek.com/user/balance"
        import requests,json
        payload={}
        headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {API}'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        data = json.loads(response.text)

        print("余额："+data["balance_infos"][0]["total_balance"]+"元") 
    
    def prefix(self,query):
        self.base_url = "https://api.deepseek.com/beta"
        messages = [
            {"role": "user", "content": "Please write quick sort code"},
            {"role": "assistant", "content": "```python\n", "prefix": True}
        ]
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stop=["```"],
        )
        print(response.choices[0].message.content)

    def fim(self):
        response = self.client.completions.create(
            model="deepseek-chat",
            prompt="def fib(a):",
            suffix="    return fib(a-1) + fib(a-2)",
            max_tokens=128
        )
        print(response.choices[0].text)

    def json_output(self,query,JSON_OUTPUT):
        messages = [{"role": "system", "content": JSON_OUTPUT},{"role": "user", "content": query}]
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            response_format={
                'type': 'json_object'
            }
            )
        return json.loads(response.choices[0].message.content)



if __name__ == "__main__":
    history=history1=[]
    llm=deepseek_api()
    #A= llm("我认为我们应该反对开放校园，这样会影响学生的学习，加大学校安保的压力",'你是一个语言学家,现在你正在参加一场辩论会,你需要记录对话者反对开放校园的具体原因,并以列表（无需符号）的形式返回观点,例如 论点a,论点b ,注意不要有多余的字符',out=False)
    #A=llm('对公众开放校园会影响到学生的学习环境','你是一个语言学家,现在你正在参加一场辩论会,你需要记录对话者对开放校园的态度,并以数字（0-10）的形式返回态度,0为反对,10为支持,注意不要有多余的字符',out=False)
    #A=int(A)
    #print(type(A))
    #print(A)
    llm('你是一个说服专家，你的目的是说服对方支持对公众开放校园，请你生成一段话来首先开启这个话题，简单的介绍背景并引起对话者沟通的兴趣，注意不要有多余的输出')
    #llm.model_list()
'''
    ls =["苹果什么颜色","它是水果吗"]
    for q in ls:
        print(llm.mt_chat_auto(q,history))
    llm.search_surplus()
    print(history)
    history1.append({"role": "user", "content": "香蕉是什么颜色的"})
    llm.mt_chat(history1)
    print(history1)
'''