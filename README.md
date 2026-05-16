# PicaBridge
[<img src="https://img.shields.io/github/v/release/reiyy/picabridge?include_prereleases">](https://github.com/Reiyy/PicaBridge/releases)
[<img src="https://img.shields.io/docker/pulls/yareiy/picabridge.svg">](https://hub.docker.com/r/yareiy/picabridge/)
[<img src="https://img.shields.io/github/downloads/reiyy/picabridge/total.svg">](https://github.com/Reiyy/PicaBridge/releases)

## 简介 

本项目模拟了 **PicACG App** 的后端 API 服务，实现了 **PicACG** 大部分功能，其中漫画数据由 **[LANraragi](https://github.com/Difegue/LANraragi)** 提供。  
哔咔桥(PicaBridge) 作为 **PicACG App** 与 **LANraragi** 之间的沟通桥梁，将 **LANraragi API** 返回的漫画数据转换为 App 可接受的格式返回。

> LANraragi 是一个开源的漫画/档案管理服务器，基于 Mojolicious 框架和 Redis 数据库构建。其提供强大的漫画归档和管理功能，支持多种格式档案，并可通过 API 交互。本项目利用 LANraragi 的 API 获取漫画数据，并对其数据进行加工使其适配 PicACG App。

## 支持的版本

**MyPica App** 2.7.1.0+

PicACG App 2.2.1.3.3.4
其他第三方Pica客户端应该也兼容(未测试)  

## 演示图
![主页和分类页](/tools/Documentation/img/主页和分类页.jpg)  
![漫画页和评论页](/tools/Documentation/img/漫画页和评论页.jpg)  
![后台主页](/tools/Documentation/img/Web后台主页.png)  

## 运行

1. [从文档获取Docker compose配置示例](/tools/Documentation/RunPicaBridge.md)  
2. 在你配置的持久化目录中创建`config.json`文件  
3. 启动容器```docker compose up```
4. 根据提示信息打开配置向导网页进行配置
8. 使用 MyPica App 连接到哔咔桥
9. Enjoy, heart❤️! =w=

关于**MyPica App**，请查看 [App文档](/tools/Documentation/App.md)

**推荐使用Docker运行**，详细步骤和使用源代码运行请 [查看运行文档](/tools/Documentation/RunPicaBridge.md)  
通过Web后台修改更多配置，手动修改请查看 [配置修改](/tools/Documentation/setconfig.md)  
正常使用还需要对LANraragi进行一些配置，请查看 [LRR配置](/tools/Documentation/lrrconfig.md)  
关于Web管理后台，请查看 [Web后台](/tools/Documentation/WebUI.md)  

默认管理员账号为：`Picabridge` | 密码：`PicaBridge233password`  
(可登录后在MyPica App设置中的"账户-变更密码"处修改，也可在Web管理后台中的用户管理处修改)  

~~你可以使用命令修改他们，请查看 [命令文档](/tools/Documentation/command.md)~~  
命令功能已被Web管理后台取代，将不再维护。  

## 升级
从已安装的旧版本Picabridge升级到新版  
(初始化程序会自动处理旧数据库和配置文件的兼容升级，)  
**(但以防万一，升级前请备份数据库和配置文件！！！)**  

### Docker 升级
1. 停止容器：```docker compose down```
2. 拉取新镜像：```docker compose pull```
3. 启动容器：```docker compose up -d```

### 源码安装升级
0. 停止服务。
1. 拉取新代码：```git pull```
2. 安装新依赖：```pip install -r requirements.txt```
3. 安装前端依赖：```npm install```
4. 构建前端：```npm run build```
5. 重启服务：```python PunchPica.py```

## 下载

- 最新版本，前往 [Github 发布页](https://github.com/Reiyy/PicaBridge/releases)  
- **MyPica App**客户端，前往 [HookMyPica 发布页](https://github.com/Reiyy/HookMyPica/releases)  
(MyPica App也会发布在本仓库Releases中，但更新检测以HookMyPica发布为准)

## 注意事项
我并非专业人士，本项目仅为我业余开发。  
开发本项目是因我使用多年的账号突然无法登录，这导致我丢失了数千收藏，  
依赖他人提供的服务总是不稳妥的。  
为此，近两年我了搭建我的家庭服务器，运行了一些服务，LANraragi便是其中之一，但我始终没有找到喜欢的客户端，  
鉴于多年来使用PicACG App习惯了，故制作了该项目。

本项目自设计之初，并没有为多人访问等高并发场景进行优化，仅适合个人使用。

## 功能
**已实现：**  
账号注册/登录  
修改密码  
忘记密码找回  
公告信息/横幅公告信息  
分类列表  
漫画列表  
漫画浏览  
漫画列表可按时间顺序排序  
收藏列表可按时间排序  
排行榜  
留言板/评论区  
漫画点赞/收藏  
随机漫画  
打哔咔签到  
用户头像上传  
漫画关联/推荐  
小程序列表  

**附加功能：**  
动态启动图  
可自定义的分类屏蔽项  
~~命令(通过发布评论来指向命令)~~ 不再维护  
Web管理后台及安装配置向导  

**待实现：**  
~~动态常用标签~~ 我更喜欢手动配置  
~~添加更多命令~~ 已被Web后台取代  
为Web后台添加更多功能   

以及：本地开发中的EH收藏全自动同步  
从EH → LRR → PicaBridge  
暂未决定是作为独立服务还是合并到哔咔桥

## 致谢

- [LANraragi](https://github.com/Difegue/LANraragi): 提供强大的漫画库功能，本项目的核心
- [HookPicACG](https://github.com/AoEiuV020/HookPicACG): 提供Xposed修改参考和去广告部分代码，MyPica App的修改基于Xposed实现

## 许可证

PicaBridge 采用 **GNU Affero General Public License v3 (AGPL-3)** 许可证 (https://www.gnu.org/licenses/agpl-3.0.html).