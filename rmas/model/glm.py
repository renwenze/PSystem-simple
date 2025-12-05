from zhipuai import ZhipuAI
class glm_api():
    def __init__(self):
        self.client = ZhipuAI(api_key="b4f532e3368d4e5c9117f913d39319bf.PAPMiAwAdMAdgwY9")
    def web_search(self,query):
        response = self.client.web_search.web_search(
            search_engine="search-pro",
            search_query=query
            )
        result = response.search_result
        res = []
        for c in result:
            res.append(c.content)
        print(res)
        return res
        
if __name__ == '__main__':
    glm = glm_api()
    glm.web_search('关于世界知名大学对公众开放校园获得好处的论据')