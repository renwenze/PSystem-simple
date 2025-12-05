import requests,json
from .config import API
def api_availability():
    url = "https://api.deepseek.com/user/balance"
    payload={}
    headers = {
    'Accept': 'application/json',
    'Authorization': f'Bearer {API}'
            }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = json.loads(response.text)
    if data["is_available"]:
        data = json.loads(response.text)
        print("deepseek_is_available:"+"True"+"\n"+"余额："+data["balance_infos"][0]["total_balance"]+"元") 
if __name__ == "__main__":
    api_availability()# print(response.text)
   

