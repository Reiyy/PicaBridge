# 配置修改

本项目的所有配置都在config,json中完成
本节将说明如何配置config.json，以及其中各项参数的含义

## 监听地址
**必填项**
```json
"Listen": "0.0.0.0:7777",
```
该参数用于指定Flask的监听地址和端口，默认为7777，  
如果你西欧你源代码运行并想修改默认监听端口，可在此修改。  
如果你使用Docker运行，可以直接修改Docker映射端口，但如果你想使用host网络模式，也可在此修改。

## PicaBridge URL
**必填项**
```json
"PicaBridge_URL": "https://picaapi.example.com:2333",
```
用于设置PicaBridge的URL，APP通过此URL访问哔咔桥
注意：url后面不要添加`/`

## JWT Token密钥
**必填项**
```json
"JWT_KEY": "efvsp8iwo4tn0bh9a83rs45u8bqhy939",
```
随机字符串，生成及验证JWT Token时需要使用此密钥

## LANraragi API
**必填项**
```json
"lrr_Api": "https://lrr.example.com:2333",
"lrr_Api_Key": "CQk0yXHxivXo7IlPuSQ74S2TETM8XIWj",
```
填写LANraragi的URL及API密钥

## 头像上传路径
```json
"avatarfilepath": "/data/wwwroot/picabridge/assets/img/avatar",
```
用户上传头像的保存路径，如果你不需要头像，可不填。

## 数据库配置
**必填项**
```json
"db": {
    "host": "192.168.7.42",
    "user": "picabridge",
    "password": "picabridge",
    "name": "picabridge",
    "pool": {
        "maxconnections": 9,
        "mincached": 3,
        "blocking": true,
        "ping": 1,
        "reset": true
    }
}
```
请填写你的数据库连接信息，并根据你的需要设置数据库连接池参数

## URL映射
**必填项**
```json
"URL_Mappings": {
    "lrr_img": "https://lrr.example.com:2333",
    "img": "https://cdn.example.com",
    "assets": "https://picaapi.example.com:2333"
}
```
由于哔咔APP在加载图片资源时，会在路径中固定加入`/static/`，固需要让所有资源指向哔咔桥，如何由Flask通过302跳转到实际URL。  
固需要通过URL映射规则来指定302跳转目的地。  
哔咔桥默认通过`PicaBridge_URL`指定的URL前缀访问资源。  
在配置公告，分类的`thumb`参数时，不需要加域名，仅填写后面的URL路径即可。

以下是例子：  
假设某图片资源的实际URL是：`https://cdn.example.com/img/2025/03/03/4ca579d5a93ca.jpg`  
需要取该渠道资源url中固定不变的部分，比如这是我的图床资源，其固定以`img`开头。  
那么设置映射规则`"img": "https://cdn.example.com"`  
`thumb`参数设置为`img/2025/03/03/4ca579d5a93ca.jpg`  
`PicaBridge_URL`为`https://picaapi.example.com:2333`  

效果：  
客户端访问`https://picaapi.example.com:2333/static/img/2025/03/03/4ca579d5a93ca.jpg`  
Flask根据映射规则`"img": "https://cdn.example.com"`，  
302跳转到实际URL：`https://cdn.example.com/img/2025/03/03/4ca579d5a93ca.jpg`  

需要注意，第一条映射规则`"lrr_img": "https://lrr.example.com:2333"`  
不能删除，请将URL设置为你的LANraragi地址，结尾不要加`/`。

## 救哔咔告图片资源
```json
"AD_Help_Pica": {
    "image": "https://picaapi.example.com:2333/assets/img/ezgif-1-83147a2658.gif"
},
```
用于设置客户端中`点击救哔咔`的图片资源，需要修改相应js文件并放到Web服务器网站数据目录下才能使用。  
需要替换js文件中的URL为你的哔咔桥URL。  
如果你不需要设置这些，此项可不填。

## APP版本更新信息
```json
"initPlatform": {
    "imageServer": "https://picaapi.example.com:2333/static/",
    "latestApplication": {
        "_id": "3ed58b151e103c60e7663b19",
        "downloadUrl": "https://picaapi.example.com:2333/assets/app_updates/2.7.0.1.2.2-398-lspatched_sign.apk",
        "updateContent": "【一般更新】",
        "version": "2.2.1.3.3.4",
        "updated_at": "2025-03-10T01:39:07.363Z",
        "created_at": "2025-03-10T01:39:07.363Z",
        "apk": {
            "originalName": "2.7.0.1.2.2-398-lspatched_sign.apk",
            "path": "assets/app_updates/2.7.0.1.2.2-398-lspatched_sign.apk",
            "fileServer": "https://picaapi.example.com:2333"
        }
    }
},
```
用于设置更新信息，如果你自行修改了客户端并想要将其推送更新，请修改此处。  
如果你并非通过逆向工程客户端那么请不要修改此处信息，保持默认，否则APP可能会始终提示强制更新无法使用。

## 分类配置
```json
"categories": {
    "分类一": {
        "lrr_id": "lanraragi的分类ID，比如：SET_1727680889",
        "rule": [0,"语言:汉语","language:中国翻訳"],
        "id": "5821859b5f6b9a4f93d12345",
        "title": "分类一",
        "description": "分类一简介",
        "thumb": "assets/img/categories/shurou.png"

    },
    "分类2": {
        "lrr_id": "SET_1728329300",
        "rule": [0,"语言:日语","语言:英语"],
        "id": "5821859b5f6b9a4f93d12347",
        "title": "生肉",
        "description": "生肉，指代未翻译的作品",
        "thumb": "assets/img/categories/shurou.png"

    }
},
"SFW_categories": {
    "SFW分类一": {
        "lrr_id": "SET_1728329318",
        "rule": [1,"重新分类:无H"],
        "id": "583ac59b5f7n456f7uyt6789",
        "title": "SFW分类一",
        "description": "SFW分类一",
        "thumb": "assets/img/categories/default.png"
    }
}
```
分类配置，你可以在此处设置在哔咔APP内显示的分类。  
由于哔咔桥支持`SFW/NSFW`模式切换，  
categories`指定`NSFW`模式下的分类，`SFW_categories`指定`SFW`模式下的分类。  

此处设置的分类必须存在于LANraragi中，当你点击分类后，会通过`lrr_id`获取分类中的漫画。  
具体的分类配置请查看LANraragi文档。

参数`lrr_id`指定LANraragi中的分类ID  
参数`rule`指定分类规则，如果你使用LANraragi的动态分类，需设置成一致的规则，目前只支持标签规则。  
`[0,"语言:日语","语言:英语"]`，中第一个参数指定完全匹配或部分匹配，`0`为部分匹配，`1`为完全匹配。

由于LANraragi API性能的问题，哔咔桥返回的漫画元数据是从自身的数据库中读取，所以需要使用`/initcmc`命令定期同步LANraragi元数据。  
由于LANraragi API的问题，当使用动态分类时，无法通过API获取相应漫画的分类，只能获取分类下的所有漫画。  
故在同步数据时，必须额外指定和动态分类一致的匹配规则来为漫画附加分类。

参数`id`为哔咔中分类的id，可随意设置  
`title` 分类的名称  
`description` 分类的简介  
`thumb` 分类图片

## 公告配置
```json
"announcements": {
    "公告1": {
        "id": "66eeec47c765ef0843f44812",
        "title": "欢迎来到 哔咔桥PicaBridge",
        "content": "领养一只属于你的哔咔娘吧！",
        "thumb": "img/2024/10/08/48d9b9a733185.png"
    },
    "公告2": {
        "id": "78eeec47c765ef0843f44964",
        "title": "PicaBridge Wiki🦉",
        "content": "PicaBridge 说明\n命令：\n命令通过发表评论的方式执行。\n分为全局命令和普通命令，全局命令只能在首页留言板中执行。\n普通命令可以在漫画评论区内执行。在哪本漫画的评论区执行，则该命令操作的就是哪本漫画。\n\n命令列表：\n1.切换模式命令\n用法：\n/模式切换 <sfw/nsfw>\n/modesw <sfw/nsfw>\n\n更多命令待补充。",
        "thumb": "img/2025/03/08/9a9b968b95b74.png"
    }
},
"banners": {
    "横幅公告1": {
        "id": "toBe1",
        "title": "Open Lanraragi",
        "shortDescription": "PicaBridge",
        "type": "web",
        "link": "https://lrr.example.com:2333/",
        "thumb": "img/2022/08/31/b44125355d4c5.png"
    }
},
```

## 常用关键字
```json
"keywords": {
    "NSFW": ["熟肉","生肉","长篇","短篇","单行本"],
    "SFW": ["无H"]
    }
```
用于设置`绅士都在搜的关键字`，目前暂未实现动态返回。

## 动态启动图
```json
"LaunchImage": {
    "GeneralDay": {
        "1": ["https://cdn.example.com/img/2025/02/13/763053dc0dd86.jpg","https://cdn.example.com/img/2025/02/14/fbf645c7b500b.jpg"],
        "2": ["https://cdn.example.com/img/2025/03/03/4ca579d5a93ca.jpg","https://cdn.example.com/img/2025/03/03/50f4c1e57d89a.jpg"]
    },
    "NSFW": {
        "n1": ["https://cdn.example.com/img/2025/03/03/6b83f9e75762d.jpg","https://cdn.example.com/img/2025/03/03/f2d3700ab7a6b.jpg"],
        "n2": ["https://cdn.example.com/img/2025/03/03/924f1a78c6e84.jpg","https://cdn.example.com/img/2025/03/03/e78666e4f4be7.jpg"]
    },
    "SpeciallDay": {
        "烧烤节": ["0215","https://cdn.example.com/img/2025/02/13/4954cb7d59db7.jpg","https://cdn.example.com/img/2025/02/13/4954cb7d59db7.jpg"]
    }
},
```
哔咔桥额外实现了动态启动图功能，需要配合Xposed模块使用，模块仍处于测试阶段，此配置可暂时忽略。