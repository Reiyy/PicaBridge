import json
import sys
import os

from lib import VER
from lib.upgrader import run_startup


def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)


config = load_config()


def main():
    print("正在初始化...")
    try:
        run_startup(config)
    except Exception as e:
        print(f"初始化/升级失败: {e}")
        sys.exit(1)
    print("初始化完成！")
    
    print("###############################")
    print("正在启动 哔咔桥PicaBridge ！")
    print(f"PicaBridge 版本: {VER}")

    listen_address = config.get("Listen", "0.0.0.0:7777")
    is_debug = config.get("SysConfig", {}).get("Debug", False)
    gunicorn_level = "debug" if is_debug else "info"

    os.environ["LOGURU_COLORIZE"] = "true"
    os.execvp("gunicorn", [
        "gunicorn",
        "-w", "1",
        "-k", "gevent",
        "-b", listen_address,
        "--access-logfile", "-",
        "--error-logfile", "-",
        "--capture-output",
        "--access-logformat", '%({x-forwarded-for}i)s "%(r)s" %(s)s %(b)s "%(a)s"',
        "--log-level", gunicorn_level,
        "PicaBridge:PicaBridge"
    ])


if __name__ == "__main__":
    main()
