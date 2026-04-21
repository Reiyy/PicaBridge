# PicaBridge
[<img src="https://img.shields.io/github/v/release/reiyy/picabridge?include_prereleases">](https://github.com/Reiyy/PicaBridge/releases)
[<img src="https://img.shields.io/docker/pulls/yareiy/picabridge.svg">](https://hub.docker.com/r/yareiy/picabridge/)
[<img src="https://img.shields.io/github/downloads/reiyy/picabridge/total.svg">](https://github.com/Reiyy/PicaBridge/releases)

## 简介 

本项目模拟了 **PicACG App** 的后端 API 服务，实现了 **PicACG** 大部分功能，其中漫画数据由 **[LANraragi](https://github.com/Difegue/LANraragi)** 提供。  
哔咔桥(PicaBridge) 作为 **PicACG App** 与 **LANraragi** 之间的沟通桥梁，将 **LANraragi API** 返回的漫画数据转换为 App 可接受的格式返回。

> LANraragi 是一个开源的漫画/档案管理服务器，基于 Mojolicious 框架和 Redis 数据库构建。其提供强大的漫画归档和管理功能，支持多种格式档案，并可通过 API 交互。本项目利用 LANraragi 的 API 获取漫画数据，并对其数据进行加工使其适配 PicACG App。

## 支持的版本

PicACG App 2.2.1.3.3.4  

其他第三方Pica客户端应该也兼容(未测试)  

## 演示图
![主页和分类页](/tools/Documentation/img/主页和分类页.jpg)
![漫画页和评论页](/tools/Documentation/img/漫画页和评论页.jpg)

## 运行

1. 安装 LANraragi v0.9.7+
2. 安装 Python 3.8+
3. 安装 MariaDB 10.6+ or MySQL 8.0+
4. 安装依赖 ```pip install -r requirements.txt ```
5. 修改配置文件，请查看 [配置修改](/tools/Documentation/setconfig.md)  
6. 运行启动脚本 ```python PunchPica.py ```
7. 配置Web服务器，如 Nginx
8. 配置并使用 MyPica App连接
9. Enjoy, heart❤️! =w=

或使用Docker运行，更多详细步骤请 [查看文档](/tools/Documentation/RunPicaBridge.md)  
根据配置文档修改config.json，[配置修改](/tools/Documentation/setconfig.md)  
正常使用还需要对LANraragi进行一些配置，请查看 [LRR配置](/tools/Documentation/lrrconfig.md)  
默认管理员账号为：`Picabridge`，密码：`PicaBridge233password`  
你可以使用命令修改他们，请查看 [命令文档](/tools/Documentation/command.md)

关于**MyPica App**，请查看 [App文档](/tools/Documentation/App.md)

## 下载

- 最新版本，前往 [Github 发布页](https://github.com/Reiyy/PicaBridge/releases)
- **MyPica App**客户端，前往 [HookMyPica 发布页](https://github.com/Reiyy/HookMyPica/releases)

## 注意事项
我并非专业人士，本项目仅为我业余开发。  
开发本项目是因我使用多年的账号突然无法登录，这导致我丢失了数千收藏，  
依赖他人提供的服务总是不稳妥的。  
为此，近两年我了搭建我的家庭服务器，运行了一些服务，LANraragi便是其中之一，但我始终没有找到喜欢的客户端，  
鉴于多年来使用PicACG App习惯了，故制作了该项目。

本项目自设计之初，并没有为多人访问等高并发场景进行优化，仅适合个人使用。

## 功能
已实现：  
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

附加功能：  
动态启动图  
可自定义的分类屏蔽项  
命令(通过发布评论来指向命令)

待实现：  
小程序  
动态常用标签  
添加更多命令

## 致谢

- [LANraragi](https://github.com/Difegue/LANraragi): 提供强大的漫画库功能，本项目的核心
- [HookPicACG](https://github.com/AoEiuV020/HookPicACG): 提供Xposed修改参考和去广告部分代码，本项目的附加功能基于Xposed实现

## 许可证

PicaBridge 采用 **GNU Affero General Public License v3 (AGPL-3)** 许可证 (https://www.gnu.org/licenses/agpl-3.0.html).