import json
import random
import string
import bcrypt
import jwt

from flask import jsonify
from datetime import datetime
from datetime import timedelta
from datetime import timezone

import lib.db as db

def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()

# 生成24位随机用户id
def generate_random_id():
    letters = ''.join(random.choices(string.ascii_lowercase, k=12))  # 生成12个小写字母
    digits = ''.join(random.choices(string.digits, k=12))  # 生成12个数字
    random_id = ''.join(random.sample(letters + digits, 24))  # 混合并随机打乱
    return random_id

# 生成密码哈希
def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

# 验证密码哈希
def verify_password(password, hashpassword):
    return bcrypt.checkpw(password.encode('utf-8'), hashpassword.encode('utf-8'))

# 生成jwt token
def generate_token(user_id, email):
    JWT_KEY = config.get('JWT_KEY')
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(days=1),
        "iat": datetime.now(timezone.utc)
    }
    token = jwt.encode(payload, JWT_KEY, algorithm="HS256")
    return token

# 注册
def Register(data):
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')
    birthday = data.get('birthday')
    gender = data.get('gender')
    question1 = data.get('question1')
    answer1 = data.get('answer1')
    question2 = data.get('question2')
    answer2 = data.get('answer2')
    question3 = data.get('question3')
    answer3 = data.get('answer3')

    # 检查必填字段
    if not all([email, name, password, birthday, gender]):
        return jsonify({"code": 400, "message": "Missing required fields"}), 400

    # 连接数据库
    connection = db.get_db_connection()
    cursor = connection.cursor()

    # 检查用户名是否已存在
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        cursor.close()
        connection.close()
        return jsonify({"code": 400, "error": "1008", "message": "email is already exist"}), 400

    # 检查昵称是否已存在
    cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
    if cursor.fetchone():
        cursor.close()
        connection.close()
        return jsonify({"code": 400, "error": "1009", "message": "name is already exist"}), 400

    # 生成随机ID
    user_id = generate_random_id()
    # 生成密码哈希
    hashpassword = hash_password(password)

    # 写入用户信息至数据库
    cursor.execute("""
        INSERT INTO users (id, email, name, password, birthday, gender, 
                           question1, answer1, question2, answer2, question3, answer3, 
                           createdate, title, description, exp, level, role, avatar, 
                           verified, characters, favourite, `like`) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s)
    """, (user_id, email, name, hashpassword, birthday, gender, 
          question1, answer1, question2, answer2, question3, answer3,
          datetime.now(), "萌新", "还没有写哦~", 0, 1, "", "", 
          False, json.dumps([]), json.dumps({}), json.dumps([])))

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({"code": 200, "message": "success"}), 200

# 登录
def SignIn(data):
    email = data.get('email')
    password = data.get('password')

    # 检查必填字段
    if not all([email, password]):
        return jsonify({"code": 400, "message": "Missing required fields"}), 400

    # 连接数据库
    connection = db.get_db_connection()
    cursor = connection.cursor()

    # 检查用户名和密码是否匹配
    cursor.execute("SELECT id, password FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user is None:
        cursor.close()
        connection.close()
        return jsonify({"code": 400, "error": "1004", "message": "invalid email or password", "detail": ":("}), 400

    user_id, hashpassword = user['id'], user['password']
    # 验证用户输入的密码是否匹配数据库中的哈希密码
    if not verify_password(password, hashpassword):
        cursor.close()
        connection.close()
        return {"error": "Invalid email or password"}, 401  # 密码错误

    # 生成jwt token
    token = generate_token(user_id, email)
    
    cursor.close()
    connection.close()

# 返回登录信息
    return jsonify({
        "code": 200,
        "message": "success",
        "data": {
            "token": token
        }
    }), 200


def ChangePasswd(user_id, data):
    new_password = data.get('new_password')
    old_password = data.get('old_password')
    
    # 连接数据库
    connection = db.get_db_connection()
    cursor = connection.cursor()
    
    # 查询用户信息
    cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
    userinfo = cursor.fetchone()
    
    if userinfo is None:
        cursor.close()
        connection.close()
        return jsonify({"code": 400, "error": "1004", "message": "invalid email or password", "detail": ":("}), 400
    
    old_hashpassword = userinfo['password']
    
    # 验证旧密码
    if not verify_password(old_password, old_hashpassword):
        cursor.close()
        connection.close()
        return jsonify({"error": "Invalid email or password"}), 401
    
    # 生成新密码哈希
    new_hashpassword = hash_password(new_password)
    
    # 更新密码
    cursor.execute("UPDATE users SET password = %s WHERE id = %s", (new_hashpassword, user_id))
    connection.commit()
    
    cursor.close()
    connection.close()
    
    return jsonify({"code": 200, "message": "success"})

# 忘记密码
def forgot_password(data):
    email = data.get("email")
    
    # 查询用户对应的密保问题
    connection = db.get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT question1, question2, question3 FROM users WHERE email = %s', (email,))
    user_data = cursor.fetchone()

    if user_data:
        # 返回问题
        response = {
            "code": 200,
            "message": "success",
            "data": {
                "question1": user_data["question1"],
                "question2": user_data["question2"],
                "question3": user_data["question3"]
            }
        }
    else:
        # 用户不存在
        response = {
            "code": 404,
            "message": "User not found",
            "data": None
        }

    connection.close()

    return jsonify(response)

# 生成随机临时密码
def generate_temp_password():
    # 随机生成前四个字母（首字母大写）
    letters = random.choices(string.ascii_lowercase, k=3)  # 生成3个小写字母
    first_letter = random.choice(string.ascii_uppercase)  # 生成一个大写字母
    letters.insert(0, first_letter)  # 将大写字母放在开头

    # 随机生成后四个数字
    digits = random.choices(string.digits, k=4)

    # 将字母和数字组合成一个完整的密码
    temp_password = ''.join(letters) + ''.join(digits)
    return temp_password

# 重置密码
def reset_password(data):
    email = data.get("email")
    question_no = data.get("questionNo")
    answer = data.get("answer")

    # 查询用户的答案
    connection = db.get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT answer1, answer2, answer3 FROM users WHERE email = %s', (email,))
    user_data = cursor.fetchone()

    if user_data:
        # 根据 questionNo 获取对应的正确答案
        correct_answer = user_data.get(f"answer{question_no}")
        
        if correct_answer and answer.lower() == correct_answer.lower():
            # 答案匹配，生成临时密码
            temp_password = generate_temp_password() # 生成随机临时密码
            # 生成临时密码哈希
            temp_hashpassword = hash_password(temp_password)
            # 更新密码
            cursor.execute("UPDATE users SET password = %s WHERE email = %s", (temp_hashpassword, email))
            connection.commit()  # 提交更改
            # 返回信息
            response = {
                "code": 200,
                "message": "success",
                "data": {
                    "password": temp_password
                }
            }
        else:
            # 答案不匹配
            response = {
                "code": 401,
                "message": "Incorrect answer",
                "data": None
            }
    else:
        # 用户不存在
        response = {
            "code": 404,
            "message": "User not found",
            "data": None
        }

    connection.close()
    return jsonify(response)