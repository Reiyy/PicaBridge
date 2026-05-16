import json
import sys
import os

from flask import Flask, jsonify, request, send_from_directory    

from lib import VER
from lib.upgrader import run_startup
from lib import Api


def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)


config = load_config()


# 精简Flask应用，仅用于配置向导                                                                                                     
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')                                                           

def _create_setup_app():
    app = Flask(__name__, static_folder=None)

    @app.route('/pbapi/init', methods=['GET'])
    def init_status():
        resp, code = Api.Config.init_status()
        return jsonify(resp), code

    @app.route('/pbapi/init', methods=['POST'])
    def init_config():
        resp, code = Api.Config.init_config(request.get_json(silent=True))
        if code == 200:
            import time, threading
            def restart():
                time.sleep(1.5)
                os.execvp(sys.executable, [sys.executable] + sys.argv)
            threading.Thread(target=restart, daemon=True).start()
        return jsonify(resp), code

    @app.route('/pbapi/init/test-db', methods=['POST'])
    def test_db():
        resp, code = Api.Config.test_db_connection(request.get_json(silent=True))
        return jsonify(resp), code

    @app.route('/ui/', defaults={'path': ''})                                                                                       
    @app.route('/ui/<path:path>')                                                                                                   
    def web_ui(path):                                                                                                               
        target = os.path.join(WEB_DIR, 'ui', path)                                                                                  
        if path and os.path.isfile(target):                                                                                         
              return send_from_directory(os.path.join(WEB_DIR, 'ui'), path)                                                           
        return send_from_directory(os.path.join(WEB_DIR, 'ui'), 'index.html')                                                       
                                                                                                                                    
    return app                                                                                                                      

def main():
    print("正在初始化...")
    if not Api.Config.is_init():
        print("配置文件还未设置，请打开配置向导进行配置！")
        listen = "0.0.0.0:7777"
        host, port = listen.rsplit(":", 1)
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except Exception:
            local_ip = "127.0.0.1"
        print(f"配置向导：http://127.0.0.1:{port}/ui")
        print(f"配置向导：http://{local_ip}:{port}/ui")

        setup_app = _create_setup_app()
        setup_app.run(host=host, port=int(port), use_reloader=False)
        return
    
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

    pid_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp')
    os.makedirs(pid_dir, exist_ok=True)
    pid_file = os.path.join(pid_dir, 'picabridge.pid')

    os.environ["LOGURU_COLORIZE"] = "true"
    os.execvp("gunicorn", [
        "gunicorn",
        "-w", "1",
        "-k", "gevent",
        "-b", listen_address,
        "--pid", pid_file,
        "--access-logfile", "-",
        "--error-logfile", "-",
        "--capture-output",
        "--access-logformat", '%({x-forwarded-for}i)s "%(r)s" %(s)s %(b)s "%(a)s"',
        "--log-level", gunicorn_level,
        "PicaBridge:PicaBridge"
    ])


if __name__ == "__main__":
    main()
