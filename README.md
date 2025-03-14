# PicaBridge

这是一个可以将Lanraragi作为哔咔APP服务端的桥接器。

漫画数据通过Lanraragi API获取，再转化为哔咔APP可以理解的格式。

当前支持LRR版本：v0.9.22 or later
当前支持哔咔APP版本：2.2.1.3.3.4
（哔咔2.5大部分兼容，少部分暂不可用）

-------------------
你需要使用诸如：修改hosts、dns重定向、代理、修改app，等方式将客户端请求地址指向PicaBridge
本项目不提供以上方式的教程，请自行解决。

# PicaBridge
[<img src="https://img.shields.io/github/release/reiyy/picabridge.svg?label=latest%20release">](https://github.com/Reiyy/PicaBridge/releases/latest)
[<img src="https://img.shields.io/docker/pulls/yareiy/picabridge.svg">](https://hub.docker.com/r/yareiy/picabridge/)
[<img src="https://img.shields.io/github/downloads/reiyy/picabridge/total.svg">](https://github.com/Reiyy/PicaBridge/releases)

## 简介 

本项目模拟了 **PicaACG APP** 的后端 API 服务，实现了 **PicaACG** 大部分功能，其中漫画数据由 **LANraragi** 提供。
哔咔桥(PicaBridge) 作为 **PicaACG APP** 与 **LANraragi** 之间的沟通桥梁，将 **LANraragi API** 返回的漫画数据转换为 APP 可接受的格式返回。

> LANraragi 是一个开源的漫画/档案管理服务器，基于 Mojolicious 框架和 Redis 数据库构建。其提供强大的漫画归档和管理功能，支持多种格式档案，并可通过 API 交互。本项目利用 LANraragi 的 API 获取漫画数据，并对其数据进行加工使其适配 PicaACG APP。

## 支持的版本

PicaACG APP 2.2.1.3.3.4
LANraragi v0.9.31+

## 运行

1. 安装 LANraragi v0.9.31+
2. 安装 Python 3.8+
3. 安装依赖 ```bash pip install -r requirements.txt ```
4. 修改配置文件 查看文档
5. 运行启动脚本 ```bash python PunchPica.py ```
6. Enjoy, heart❤️! =w=

更多详细步骤请 查看文档

## 下载

- 最新版本，前往 [Github Releases page](https://github.com/LSPosed/LSPosed/releases)

## 注意
本项目自设计之初，并没有为多人访问等高并发场景进行优化，仅适合个人使用。

## 致谢

- [LANraragi](https://github.com/Difegue/LANraragi): 提供强大的漫画库功能，本项目的核心
- [DeepSeek AI](https://github.com/deepseek-ai): 性能强大的语言模型，为项目提供帮助
- [XposedBridge](https://github.com/TheZoraiz/ascii-image-converter): 可将图像转换为ASCII艺术画，启动脚本中的ASCII画用其创建

## 许可证

PicaBridge 采用 **GNU Affero General Public License v3 (AGPL-3)** 许可证 (https://www.gnu.org/licenses/agpl-3.0.html).