import json
import jwt

from flask import Flask
from flask import jsonify
from flask import request
from flask import redirect
from flask import make_response
from functools import wraps

from lib import initdb
from lib import account
from lib import announcements
from lib import banners
from lib import categories
from lib import comiclist
from lib import comicinfo
from lib import eps
from lib import comicorder
from lib import userinfo
from lib import leaderboard
from lib import initplatform
from lib import search
from lib import keywords
from lib import comment
from lib import PicaCommand
from lib import LaunchImage
from lib import ModeSwitch

PicaBridge = Flask(__name__, static_folder=None)

# 读取 JSON 配置文件
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()

LRR_URL = config.get('lrr_Api')
PICABRIDGE_URL = config.get('PicaBridge_URL')
URL_MAPPINGS = config.get("URL_Mappings", {})
DEFAULT_FILE_SERVER = next(iter(URL_MAPPINGS.values()), None)

# JWT校验
def verify_token(token):
    JWT_KEY = load_config().get('JWT_KEY')
    try:
        payload = jwt.decode(token, JWT_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError as e:
        print(f"Token expired: {e}")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token: {e}")
        return None

# JWT验证装饰器
def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("authorization")

        if not auth_header or not auth_header.strip():
            return jsonify({"code": 401, "error": "1005", "message": "unauthorized"}), 401
        
        token = auth_header.strip()
        jwt_payload = verify_token(token)
        if not jwt_payload:
            return jsonify({"code": 401, "error": "1005", "message": "invalid or expired"}), 401
        
        # 把用户数据传递给被装饰的函数
        return f(*args, **kwargs, jwt_payload=jwt_payload)
    
    return decorated_function

# 获取动态启动图
@PicaBridge.route('/GetLaunchImage', methods=['GET'])
def get_launch_image():
    user_name = request.args.get('user', default="")
    return LaunchImage.Get(user_name)

# 图片资源重定向
@PicaBridge.route('/static/<path:filepath>', methods=['GET'])
def static_redirect(filepath):
    query_string = request.query_string.decode("utf-8")
    prefix = filepath.split("/")[0]  # 获取路径前缀
    # 查找是否有相应映射，如果没有使用默认域
    fileserver = URL_MAPPINGS.get(prefix, DEFAULT_FILE_SERVER)
    # 如果默认值也为空，返回错误
    if not fileserver:
        return "No fileServer", 500
    # 如果存在查询参数，带上查询参数
    if query_string:
        return redirect(f"{fileserver}/{filepath}?{query_string}", code=302)

    return redirect(f"{fileserver}/{filepath}", code=302)

# LRR档案图像重定向
@PicaBridge.route('/static/lrr_img/<path:filepath>', methods=['GET'])
def comic_redirect_route(filepath):
    query_string = request.query_string.decode("utf-8")
    target_url = f"{LRR_URL}/{filepath}"
    if query_string:
        target_url = f"{target_url}?{query_string}"
    return redirect(target_url, code=302)

# 监听
# 监听init
@PicaBridge.route('/init', methods=['GET'])
def init_route():
    platform = request.args.get('platform')
    user_id = request.args.get('authorization') # 此处仅作为占位兼容原函数，不起实际作用
    # 如果platform为空，不需要JWT验证
    if platform is None:
        return initplatform.init(platform, user_id)
    return init_route_auth()

# 如果platform不为空，需要JWT验证
@jwt_required
def init_route_auth(jwt_payload):
    platform = request.args.get('platform')
    user_id = jwt_payload.get("user_id")

    return initplatform.init(platform, user_id)

# 监听点击救哔咔广告
@PicaBridge.route('/ad/android/cat', methods=['GET'])
def android_cat_route():
    response = make_response('<!DOCTYPE html><html><head><meta charSet="utf-8" class="next-head"/><title class="next-head">嗶咔廣告</title><meta name="viewport" content="initial-scale=1.0, width=device-width" class="next-head"/><style class="next-head">body {margin: 0}</style><link rel="preload" href="/assets/ad/clicktohelppica/js/pages/show.js" as="script"/><link rel="preload" href="/assets/ad/clicktohelppica/js/pages/_app.js" as="script"/><link rel="preload" href="/assets/ad/clicktohelppica/js/pages/_error.js" as="script"/><link rel="preload" href="/assets/ad/clicktohelppica/js/runtime/webpack-42652fa8b82c329c0559.js" as="script"/><link rel="preload" href="/assets/ad/clicktohelppica/js/chunks/commons.31d10eeff7ba6e9319c7.js" as="script"/><link rel="preload" href="/assets/ad/clicktohelppica/js/runtime/main-1b037b55b33d0a347283.js" as="script"/></head><body><div id="__next"><div data-reactroot=""><div style="width:100%"></div></div></div><script>__NEXT_DATA__ = {"props":{"pageProps":{}},"page":"/show","query":{"zoneId":"zone_233","location":"wakamoment"},"buildId":"nXBZRN9Bnol3egSoxUs8s"};__NEXT_LOADED_PAGES__=[];__NEXT_REGISTER_PAGE=function(r,f){__NEXT_LOADED_PAGES__.push([r, f])}</script><script async="" id="__NEXT_PAGE__/show" src="/assets/ad/clicktohelppica/js/pages/show.js"></script><script async="" id="__NEXT_PAGE__/_app" src="/assets/ad/clicktohelppica/js/pages/_app.js"></script><script async="" id="__NEXT_PAGE__/_error" src="/assets/ad/clicktohelppica/js/pages/_error.js"></script><script src="/assets/ad/clicktohelppica/js/runtime/webpack-42652fa8b82c329c0559.js" async=""></script><script src="/assets/ad/clicktohelppica/js/chunks/commons.31d10eeff7ba6e9319c7.js" async=""></script><script src="/assets/ad/clicktohelppica/js/runtime/main-1b037b55b33d0a347283.js" async=""></script></body></html>', 200)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

# 监听广告信息
@PicaBridge.route('/get-ad-zones', methods=['GET'])
def android_cat2_route():
    image = config.get('AD_Help_Pica', {}).get('image', '')
    response_data = {
        "ads": [
            {
                "zoneId": "zone_233",
                "title": "LANraragi",
                "link": LRR_URL,
                "rawLink": LRR_URL,
                "image": image
            }
        ],
        "code": 200
    }
    return jsonify(response_data), 200

# 监听注册请求
@PicaBridge.route('/auth/register', methods=['POST'])
def register_route():
    return account.Register(request.json)

# 监听登录请求
@PicaBridge.route('/auth/sign-in', methods=['POST'])
def sign_in_route():
    return account.SignIn(request.json)

# 监听获取漫画封面请求
@PicaBridge.route('/static/thumbnail/<arcid>', methods=['GET'])
def handle_thumbnail_route(arcid):
    return comiclist.redirect_thumbnail(arcid)

# 监听获取漫画列表请求
@PicaBridge.route('/comics', methods=['GET'])
@jwt_required
def handle_comics_route(jwt_payload):
    user_id = jwt_payload.get("user_id")
    page = request.args.get('page', default=1, type=int)
    s = request.args.get('s', default=None, type=str)  # 排序标记
    c = request.args.get('c', default=None, type=str)  # 获取分类
    t = request.args.get('t', default=None, type=str)  # 获取标签
    a = request.args.get('a', default=None, type=str)  # 获取作者

    return comiclist.get_comics_data(user_id, page, s, c, t, a)

# 监听获取随机漫画请求
@PicaBridge.route('/comics/random', methods=['GET'])
@jwt_required
def handle_random_comics_route(jwt_payload):
    user_id = jwt_payload.get("user_id")

    return comiclist.get_random_comics(user_id)

# 监听公告消息请求
@PicaBridge.route('/announcements', methods=['GET'])
def announcements_route():
    page = request.args.get('page', default=1, type=int)
    return announcements.get_announcements(page)

# 监听横幅公告请求
@PicaBridge.route('/banners', methods=['GET'])
def banners_route():
    return banners.get_banners()

# 监听获取分类请求
@PicaBridge.route('/categories', methods=['GET'])
@jwt_required
def categories_route(jwt_payload):
    user_id = jwt_payload.get("user_id")
    return categories.get_categories(user_id)

# 监听获取漫画信息请求
@PicaBridge.route('/comics/<comic_id>', methods=['GET'])
@jwt_required
def comic_detail_route(comic_id, jwt_payload):
    user_id = jwt_payload.get("user_id")
    comic_info = comicinfo.get_comic_info(comic_id, user_id)
    if comic_info is None:
        return jsonify({"code": 404, "message": "Comic not found"}), 404
    return jsonify(dict(comic_info)), 200

# 监听获取漫画章节请求
@PicaBridge.route('/comics/<comic_id>/eps')
def eps_route(comic_id):
    page = request.args.get('page', 1, type=int)
    return eps.get_eps(comic_id, page)

# 监听获取漫画图片请求
@PicaBridge.route('/comics/<comic_id>/order/<int:order>/pages', methods=['GET'])
def comic_pages_route(comic_id, order):
    page = request.args.get('page', default=1, type=int)
    response = comicorder.get_pages(comic_id, page)
    return jsonify(response)

# 监听漫画收藏
@PicaBridge.route('/comics/<comic_id>/favourite', methods=['POST'])
@jwt_required
def favourite_comic_route(comic_id, jwt_payload):
    user_id = jwt_payload.get("user_id")
    if not user_id:
        return jsonify({"code": 400, "message": "Missing user ID"}), 400

    return comicinfo.comic_favourite(user_id, comic_id)

# 监听漫画点赞
@PicaBridge.route('/comics/<comic_id>/like', methods=['POST'])
@jwt_required
def like_comic_route(comic_id, jwt_payload):
    user_id = jwt_payload.get("user_id")
    if not user_id:
        return jsonify({"code": 400, "message": "Missing user ID"}), 400

    return comicinfo.comic_like(user_id, comic_id)

# 监听漫画排行榜
@PicaBridge.route('/comics/leaderboard', methods=['GET'])
def get_leaderboard_route():
    tt = request.args.get('tt')
    return leaderboard.get_comic_leaderboard(tt)

# 监听骑士排行榜
@PicaBridge.route('/comics/knight-leaderboard', methods=['GET'])
def knight_leaderboard_route():
    return leaderboard.get_knight_leaderboard()

# 监听个人中心
@PicaBridge.route('/users/profile', methods=['GET'])
@jwt_required
def user_profile_route(jwt_payload):
    user_id = jwt_payload.get("user_id")
    if not user_id:
        return jsonify({"code": 400, "message": "Authorization required."}), 400
    return userinfo.user_info(user_id)

# 监听收藏列表
@PicaBridge.route('/users/favourite', methods=['GET'])
@jwt_required
def favourite_comics_route(jwt_payload):
    user_id = jwt_payload.get("user_id")
    page = request.args.get('page', default=1, type=int)
    if not user_id:
        return jsonify({"code": 401, "message": "Unauthorized"}), 401
    return userinfo.get_favourite_comics(user_id, page)

# 监听用户资料
@PicaBridge.route('/users/<user_id>/profile', methods=['GET'])
def get_user_profile_route(user_id):
    return userinfo.get_user_profile(user_id)

# 监听用户简介修改
@PicaBridge.route('/users/profile', methods=['PUT'])
@jwt_required
def user_profile_put_route(jwt_payload):
    user_id = jwt_payload.get("user_id")
    if not user_id:
        return jsonify({"code": 400, "message": "Authorization required."}), 400
    json_data = request.get_json()
    if json_data and "slogan" in json_data:
        return userinfo.set_user_description(user_id, json_data)
    return jsonify({"code": 400, "message": "Invalid data."}), 400

# 监听签到
@PicaBridge.route('/users/punch-in', methods=['POST'])
@jwt_required
def punch_in_route(jwt_payload):
    user_id = jwt_payload.get("user_id")
    return userinfo.punch_in(user_id)

# 监听头像上传
@PicaBridge.route('/users/avatar', methods=['PUT'])
@jwt_required
def upload_user_avatar_route(jwt_payload):
    user_id = jwt_payload.get("user_id")
    if not user_id:
        return jsonify({"code": 400, "message": "Authorization required."}), 400
    picdata = request.json.get('avatar')
    if not picdata:
        return jsonify({"code": 400, "message": "Avatar data is required."}), 400
    result = userinfo.upload_avatar(user_id, picdata)
    return result

# 监听搜索
@PicaBridge.route('/comics/advanced-search', methods=['POST'])
def handle_advanced_search_route():
    data = request.get_json()
    keyword = data.get('keyword', '')
    page = request.args.get('page', default=1, type=int)
    return search.search_comic(keyword, page)

# 监听获取常用标签
@PicaBridge.route('/keywords', methods=['GET'])
@jwt_required
def keywords_route(jwt_payload):
    user_id = jwt_payload.get("user_id")
    return keywords.get_keywords(user_id)

# 监听发布主评论
@PicaBridge.route('/comics/<comic_id>/comments', methods=['POST'])
@jwt_required
def new_comment(comic_id, jwt_payload):
    user_id = jwt_payload.get("user_id")
    contentdata = request.get_json()
    content = contentdata["content"]
    # 检查是否是命令
    if content.startswith("/"):
        # 调用命令处理函数
        print(f"命令评论")
        return PicaCommand.run(comic_id, user_id, contentdata)
    # 普通评论处理
    return comment.post_comment(comic_id, user_id, contentdata)

# 监听获取主评论列表
@PicaBridge.route('/comics/<comic_id>/comments', methods=['GET'])
@jwt_required
def get_comment_list(comic_id, jwt_payload):
    user_id = jwt_payload.get("user_id")
    page = request.args.get('page', default=1, type=int)
    return comment.load_comments(comic_id, page, user_id)

# 监听发布子评论
@PicaBridge.route('/comments/<parent_comment_id>', methods=['POST'])
@jwt_required
def new_child_comment(parent_comment_id, jwt_payload):
    user_id = jwt_payload.get("user_id")
    childcontentdata = request.get_json()
    return comment.post_child_comment(parent_comment_id, user_id, childcontentdata)

# 监听获取子评论列表
@PicaBridge.route('/comments/<parent_comment_id>/childrens', methods=['GET'])
@jwt_required
def get_child_comments_list(parent_comment_id, jwt_payload):
    user_id = jwt_payload.get("user_id")
    page = int(request.args.get('page', 1))
    return comment.load_child_comments(parent_comment_id, page, user_id)
                             
# 监听漫画点赞
@PicaBridge.route('/comments/<comment_id>/like', methods=['POST'])
@jwt_required
def like_comment_route(comment_id, jwt_payload):
    user_id = jwt_payload.get("user_id")
    if not user_id:
        return jsonify({"code": 400, "message": "Missing user ID"}), 400
    return comment.like_comment(user_id, comment_id)

# 监听模式切换
@PicaBridge.route('/modeswitch', methods=['POST'])
@jwt_required
def modeswitch_route(jwt_payload):
    user_id = jwt_payload.get("user_id")
    mode = request.args.get('mode')
    return ModeSwitch.switch(user_id, mode)

def main():
    print("你正在运行调试模式！")
    print("如果这不是你想要的，请通过PunchPica.py运行！")
    # 启动 Flask
    print("正在启动Flask！")
    PicaBridge.run(debug=True, host='0.0.0.0', port=7777)

if __name__ == "__main__":
    main()
