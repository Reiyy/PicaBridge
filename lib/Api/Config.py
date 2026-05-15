import json
import os
import tempfile
import threading
from collections import OrderedDict
from loguru import logger

# 配置文件
CONFIG_PATH = 'config.json'

# 脱敏字段
SENSITIVE_FIELDS = {"JWT_KEY", "lrr_Api_Key", "db.password"}

# 线程锁
_config_lock = threading.Lock()

# 读取配置
def load_config():
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f, object_pairs_hook=OrderedDict)

# 保存配置
def save_config(config_data):
    config_path = os.path.abspath(CONFIG_PATH)
    dir_name = os.path.dirname(config_path)
    with _config_lock:
        fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix='.tmp')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)
            os.replace(tmp_path, config_path)
            logger.info("配置文件已保存！")
            return True
        except Exception as e:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            logger.error("保存配置文件失败: {e}".format(e=e))
            raise

# 脱敏处理
def _mask_sensitive_fields(config, fields, prefix=""):
    masked = {}
    for key, value in config.items():
        full_path = "{prefix}.{key}".format(prefix=prefix, key=key) if prefix else key
        if full_path in fields:
            masked[key] = "******"
        elif isinstance(value, dict):
            masked[key] = _mask_sensitive_fields(value, fields, full_path)
        else:
            masked[key] = value
    return masked

# 初始化状态检测
def is_init():
    if not os.path.exists(CONFIG_PATH):
        return False
    try:
        config = load_config()
        if config.get("is_init") is True:
            return True
        # 兼容旧版：配置中已包含所有必需字段时视为已初始化
        required = ["PicaBridge_URL", "JWT_KEY", "lrr_Api", "lrr_Api_Key", "db"]
        if all(config.get(f) for f in required):
            save_config({"is_init": True, **config})
            return True
        return False
    except Exception:
        return False

# 传入数据校验
def validate_config(data):
    errors = []

    if "JWT_KEY" in data:
        if not isinstance(data["JWT_KEY"], str) or not data["JWT_KEY"]:
            errors.append({"field": "JWT_KEY", "message": "必填项"})

    if "Listen" in data:
        if not isinstance(data["Listen"], str) or ":" not in data["Listen"]:
            errors.append({"field": "Listen", "message": "格式应为 host:port"})

    if "PicaBridge_URL" in data:
        url = data["PicaBridge_URL"]
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            errors.append({"field": "PicaBridge_URL", "message": "必须是有效的 http/https URL"})

    if "lrr_Api" in data:
        url = data["lrr_Api"]
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            errors.append({"field": "lrr_Api", "message": "必须是有效的 http/https URL"})

    if "lrr_Api_Key" in data:
        if not isinstance(data["lrr_Api_Key"], str) or not data["lrr_Api_Key"]:
            errors.append({"field": "lrr_Api_Key", "message": "必填项"})

    if "db" in data and isinstance(data["db"], dict):
        db_data = data["db"]
        for f in ["host", "user", "password", "name"]:
            if f in db_data and not isinstance(db_data[f], str):
                errors.append({"field": "db.{f}".format(f=f), "message": "必须是字符串"})
        if "pool" in db_data and isinstance(db_data["pool"], dict):
            pool = db_data["pool"]
            for f in ["maxconnections", "mincached", "ping"]:
                if f in pool and not isinstance(pool[f], int):
                    errors.append({"field": "db.pool.{f}".format(f=f), "message": "必须是整数"})
            for f in ["blocking", "reset"]:
                if f in pool and not isinstance(pool[f], bool):
                    errors.append({"field": "db.pool.{f}".format(f=f), "message": "必须是布尔值"})

    if "SysConfig" in data and isinstance(data["SysConfig"], dict):
        if "Debug" in data["SysConfig"] and not isinstance(data["SysConfig"]["Debug"], bool):
            errors.append({"field": "SysConfig.Debug", "message": "必须是布尔值"})

    return errors

# 获取初始化状态
def init_status():
    try:
        return {"code": 200, "message": "success", "data": is_init()}, 200
    except Exception as e:
        logger.error("检测初始化状态失败: {e}".format(e=e))
        return {"code": 500, "message": "检测初始化状态失败"}, 500

# 写入初始化配置
def init_config(data):
    if is_init():
        return {"code": 403, "message": "初始化已完成，该API已禁用"}, 403

    if not data:
        return {"code": 400, "message": "请求数据不存在"}, 400

    required_fields = ["PicaBridge_URL", "JWT_KEY", "lrr_Api", "lrr_Api_Key", "db"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return {"code": 400, "message": "缺少必填字段: {fields}".format(fields=", ".join(missing))}, 400

    errors = validate_config(data)
    if errors:
        return {"code": 400, "message": "校验失败", "data": {"errors": errors}}, 400

    try:
        existing = load_config()
    except Exception:
        existing = {}

    # 保持原有key顺序
    for key in list(existing.keys()):
        if key in data:
            existing[key] = data.pop(key)
    existing.update(data)
    existing["URL_Mappings"] = existing.get("URL_Mappings") or {}
    existing["URL_Mappings"]["lrr_img"] = existing["lrr_Api"]
    existing["URL_Mappings"]["assets"] = existing["PicaBridge_URL"]
    save_config({"is_init": True, **existing})

    return {"code": 200, "message": "success", "data": {"message": "初始化已完成", "restart_required": True}}, 200

# 获取配置
def get_config(mask):
    try:
        if mask:
            config = load_config()
            config = _mask_sensitive_fields(config, SENSITIVE_FIELDS)
        return {"code": 200, "message": "success", "data": {"config": config, "sensitive_fields": list(SENSITIVE_FIELDS)}}, 200
    except Exception as e:
        logger.error("读取配置失败: {e}".format(e=e))
        return {"code": 500, "message": "读取配置失败"}, 500

# 写入配置
def set_config(data):
    if not data:
        return {"code": 400, "message": "请求数据为空"}, 400

    errors = validate_config(data)
    if errors:
        return {"code": 400, "message": "验证失败", "data": {"errors": errors}}, 400

    try:
        config = load_config()
        old_config = json.dumps(config, sort_keys=True)
        if "db" in data and isinstance(data["db"], dict) and isinstance(config.get("db"), dict):
            config["db"].update(data.pop("db"))
        # 保持原有key顺序，更新已有key的值，新key追加到末尾
        for key in list(config.keys()):
            if key in data:
                config[key] = data.pop(key)
        config.update(data)
        save_config(config)
        new_config = json.dumps(config, sort_keys=True)
        restart_required = old_config != new_config
        return {"code": 200, "message": "success", "data": {"message": "配置已更新", "restart_required": restart_required}}, 200
    except Exception as e:
        logger.error("更新配置失败: {e}".format(e=e))
        return {"code": 500, "message": "更新配置失败"}, 500

# 备份配置
def backup():
    try:
        config = load_config()
        return {"code": 200, "message": "success", "data": config}, 200
    except Exception as e:
        logger.error("创建配置备份失败: {e}".format(e=e))
        return {"code": 500, "message": "创建配置备份失败"}, 500

# 恢复配置
def restore(data):
    if not data or "config" not in data:
        return {"code": 400, "message": "未提供有效的备份数据"}, 400

    config_data = data["config"]
    if not isinstance(config_data, dict):
        return {"code": 400, "message": "配置数据格式错误"}, 400

    try:
        save_config(config_data)
        logger.info("配置已从备份恢复")
        return {"code": 200, "message": "success", "data": {"message": "配置已从备份恢复", "restart_required": True}}, 200
    except Exception as e:
        logger.error("恢复配置失败: {e}".format(e=e))
        return {"code": 500, "message": "服务器内部错误"}, 500
