# -*- coding: utf-8 -*-
# 这是一个用来查找指定用户在哔咔中发布的评论的脚本，目前的设定为找到一条后就退出
import requests
import json
import time
import uuid
import hmac
import hashlib

import random
import string

BASE_URL = "https://picaapi.picacomic.com/comics/5822a6e3ad7ede654696e482/comments"

def generate_headers(path: str, data: dict = None, token: str = None, type: str = "GET"):
    api_key = "C69BAF41DA5ABD1FFEDC6D2FEA56B"
    api_secret = "~d}$Q7$eIni=V)9\\RK/P.RM4;9[7|@/CA}b~OW!3?EV`:<>M7pddUBL5n|0/*Cn"
    headers = {
        "api-key": api_key,
        "accept": "application/vnd.picacomic.com.v1+json",
        "app-channel": "2",
        "app-version": "2.2.1.2.3.4",
        "app-uuid": "defaultUuid",
        "app-platform": "android",
        "app-build-version": "45",
        "User-Agent": "okhttp/3.8.1",
        "image-quality": "original",
    }
    current_time = str(int(time.time()))
    nonce = "".join(random.choices(string.ascii_lowercase + string.digits, k=32)) 
    raw = path + current_time + nonce + type + api_key
    raw = raw.lower()
    h = hmac.new(api_secret.encode(), digestmod=hashlib.sha256)
    h.update(raw.encode())
    signature = h.hexdigest()
    headers["time"] = current_time
    headers["nonce"] = nonce
    headers["signature"] = signature
    if data is not None:
        headers["Content-Type"] = "application/json; charset=UTF-8"
    if token is not None:
        headers["authorization"] = token
    return headers


def sign(email, password):
    data = {"email": email, "password": password}
    sign_headers = generate_headers(path="auth/sign-in", data=data, type = "POST")
    sign_response = requests.post(
        url="https://picaapi.picacomic.com/auth/sign-in",
        data=json.dumps({"email": email, "password": password}),
        headers=sign_headers,
        timeout=60,
    ).json()
    mytoken = sign_response.get("data", {}).get("token")
    print(f"登录返回数据: {sign_response}")
    return mytoken

# 日志写入函数
def log_message(message):
    with open("success.log", "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")


# 主程序
if __name__ == "__main__":
    email = "yareiy722"
    password = "kldzzh0722"
    print(f"正在登录...")

    mytoken = sign(email, password)

    start_page = int(input("请输入从第几页开始："))
    #search_name = input("请输入要查找的用户名: ")
    search_name = "夜棂依"
    
    for page in range(start_page, 42640):
        time.sleep(1)

        url_end = f"comics/5822a6e3ad7ede654696e482/comments?page={page}"

        headers = generate_headers(path=url_end, token=mytoken, type = "GET")

        #print(f"请求头：{headers}")
        # 请求 URL
        url = f"{BASE_URL}?page={page}"
        print(f"请求的URL: {url}")
        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()  # 如果响应状态码不是 200，将引发异常
                break  # 请求成功，退出重试循环
            except requests.exceptions.RequestException as e:
                print(f"请求错误: {e}, 尝试 {attempt + 1}/{max_retries} 重新请求...")
                time.sleep(2)  # 等待 2 秒后重试
                if attempt == max_retries - 1:
                    print(f"重试失败，跳过第{page}页")
                    continue

        # 打印请求的完整数据
        #print(f"请求第{page}页的数据: {response.text}")

        # 处理返回的数据
        data = response.json()
        if data.get("code") != 200 or not data.get("data", {}).get("comments", {}).get("docs"):
            print(f"请求失败：第{page}页")
            break

        found = False
        for comment in data["data"]["comments"]["docs"]:
            user_name = comment["_user"]["name"]  # 正确访问名称
            print(f"检查用户名称: {user_name}")  # 调试输出
            if search_name in comment["_user"]["name"]:
                found = True
                created_at = comment["created_at"]
                content = comment["content"]
                success_message = f"第{page}页 ： 匹配成功！，评论时间：{created_at}。评论内容：{content}"
                print(success_message)
                log_message(success_message)
                break

        if found:
            break  # 退出外层循环

        if not found:
            print(f"匹配失败：第{page}页 ： 没找到")

        # 每10页请求间隔5秒
        if (page - start_page + 1) % 30 == 0:
            time.sleep(5)
