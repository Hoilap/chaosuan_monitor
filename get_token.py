import requests
import base64
import json

def get_bihu_token():
    url = "https://starlight.nscc-gz.cn/api/keystone/short_term_token/name"
    
    # 你的原始信息
    username = "inplusgtml@gmail.com"
    password_plain = ""
    
    # 1. 将密码进行 Base64 编码 (对应抓包到的 aW5wbHVzTUwxMjM=)
    password_encoded = base64.b64encode(password_plain.encode('utf-8')).decode('utf-8')
    
    # 2. 构建抓包到的完整 Payload
    payload = {
        "cookie_exp": None,
        "password": password_encoded,
        "redirect_url": None,
        "token_type": None,
        "username": username
    }
    
    # 3. 构建 Header (模拟浏览器，防止被拦截)
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://starlight.nscc-gz.cn",
        "Referer": "https://starlight.nscc-gz.cn/"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        
        # 调试信息
        # print(f"Status Code: {response.status_code}")
        # print(f"Response Text: {response.text}")

        if response.status_code == 200:
            # 天河系统通常直接在 JSON 的某个字段返回 token，或者直接返回 token 字符串
            # 假设返回的是 JSON: {"token": "xxxx"} 或 {"spec": {"token": "xxxx"}}
            try:
                res_data = response.json()
                # 这里的提取逻辑需要根据你 Response 里的实际字段名修改
                # 如果返回的是 {"token": "..."}，就用 
                token = res_data.get("spec")
                # 如果返回的是 {"spec": {"token": "..."}}，就用下面的：
                #token = res_data.get("spec", {}).get("token") or res_data.get("token")
                return token
            except:
                # 如果返回的是纯字符串而不是 JSON
                return response.text.strip().strip('"')
        else:
            print(f"登录失败，状态码：{response.status_code}")
            return None
            
    except Exception as e:
        print(f"请求发生异常: {e}")
        return None

# 执行并打印结果
token = get_bihu_token()
if token:
    print(f"成功获取 BIHU_TOKEN: {token}")
else:
    print("未能获取 Token，请检查用户名密码或 Response 结构")