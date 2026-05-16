# 运行PicaBridge

## 环境准备
安装 LANraragi v0.9.7+，请查看 [LRR文档](https://sugoi.gitbook.io/lanraragi/dev)

安装 Docker环境

~~你还需要一个Web服务器(如Nginx)来代理PicaBridge，以及负责处理静态资源，如用户头像，分类图像等。~~  
从0.7.6开始静态资源可由哔咔桥管理和提供，你可以在diy端点中放置自己需要的静态资源而无需另行启动Web服务器。

## 开始
开始运行PicaBridge，你可以选择提供Docker或源代码运行。

###  Docker运行(**推荐**)
创建Docker Compose配置  
以下是一个示例配置：
```yaml
services:
  picabridge:
    image: yareiy/picabridge:latest
    container_name: picabridge
    restart: on-failure:3
    ports:
      - "7777:7777"
    volumes:
      - ./data/config.json:/PicaBridge/config.json 
      - ./data/logs:/PicaBridge/logs 
      - ./data/avatar:/PicaBridge/web/assets/img/avatar 
      - ./data/diy:/PicaBridge/web/diy 
    environment:
      - TZ=Asia/Shanghai
    networks:
      - picabridge

networks:
  picabridge:
```

运行Docker前，  
请手动在你设置的`/PicaBridge/config.json`映射目录内创建`config.json`文件  
可为空文件，也可从模板复制```cp config.example.json config.json```  

你可以修改Docker的映射端口，但如果你想修改容器内端口，可在Web后台修改。  
也可手动编辑配置文件，具体查看 [配置修改](/tools/Documentation/setconfig.md)

你也可以通过Docker运行Mysql数据库：
```yaml
  mysql:
    image: mysql:8.2
    container_name: mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: 123456  # 请修改密码
      MYSQL_DATABASE: picabridge
    volumes:
      - ./data/mysqldata:/var/lib/mysql
```

配置完成后启动Docker ```docker compose up```   
确认运行正常后使用使用ctrl+c退出，然后使用后台运行 ```docker compose up -d```  
Enjoy, heart❤️! =w=

注：使用默认密码登录后，别忘了在APP设置中修改密码！

关于静态资源托管，哔咔桥提供了一个 `diy` 端点，在Docker上配置为持久化存储。  
在以上配置例子中，位于 `./data/diy` 目录下。  
你可以把你要的各种静态资源，比如分类图片，公告图片等放在这，  
然后你可通过`{PicaBridge_URL}/diy/xxxx.png`来访问。  
再相应的将路径配置到你需要的位置即可。  
然后在Web管理后台`系统设置-资源映射`中，添加一条新的资源映射规则：  
`Key：diy | URL：{PicaBridge_URL}`  
(URL结尾不要加"/"")

###  源代码运行(**不推荐**)

不推荐使用源代码运行，很多功能测试都基于Docker运行，使用源代码运行可能遇到未知Bug！  

前置依赖：  
1. 安装 LANraragi v0.9.7+
2. 安装 Python 3.9+
3. 安装 MariaDB 10.6+ or MySQL 8.0+

拉取项目 ```git clone https://github.com/Reiyy/PicaBridge.git```

进入项目文件夹 ```cd PicaBridge```

安装依赖 ```pip install -r requirements.txt ```

安装前端依赖：```npm install```

构建前端：```npm run build```

创建配置文件 ```cp config.example.json config.json```

根据配置文档修改config.json，[配置修改](/tools/Documentation/setconfig.md)

运行启动脚本 ```python PunchPica.py ```

Enjoy, heart❤️! =w=

##  配置反向代理(此处使用Nginx)

请将```proxy_pass http://127.0.0.1:7777;```替换为你在配置文件中指定的地址。

以下是一个示例配置：
```nginx
server {
  listen 80;
  listen [::]:80;
  listen 443 ssl http2;
  listen [::]:443 ssl http2;
  ssl_certificate /usr/local/openresty/nginx/conf/ssl/_.233.com.crt;
  ssl_certificate_key /usr/local/openresty/nginx/conf/ssl/_.233.com.key;
  ssl_protocols TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
  ssl_ciphers TLS13-AES-256-GCM-SHA384:TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:TLS13-AES-128-CCM-8-SHA256:TLS13-AES-128-CCM-SHA256:EECDH+CHACHA20:EECDH+AES128:RSA+AES128:EECDH+AES256:RSA+AES256:EECDH+3DES:RSA+3DES:!MD5;
  ssl_prefer_server_ciphers on;
  ssl_session_timeout 10m;
  ssl_session_cache builtin:1000 shared:SSL:10m;
  ssl_buffer_size 1400;
  add_header Strict-Transport-Security max-age=31536000;
  ssl_stapling on;
  ssl_stapling_verify on;
  server_name picabridge.233.com ;
  access_log /data/wwwlogs/picabridge_nginx.log combined;
  error_log /data/wwwlogs/picabridge_error.log debug;
  index index.html index.htm index.php;
  root /data/wwwroot/picabridge;

  error_page 404 /404.html;
  error_page 502 /502.html;

  #PROXY-START/
  location ~* ^(?!/assets/).*\.(gif|png|jpg|css|js|woff|woff2)$ {
    proxy_pass http://127.0.0.1:7777;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header REMOTE-HOST $remote_addr;
    expires 12h;
  }
  
  location / {
    proxy_pass http://127.0.0.1:7777;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header REMOTE-HOST $remote_addr;
    add_header X-Cache $upstream_cache_status;
    add_header Cache-Control no-cache;
  }
  #PROXY-END/

  location ~ .*\.(gif|jpg|jpeg|png|bmp|swf|flv|mp4|ico)$ {
    expires 30d;
    access_log off;
  }
  location ~ .*\.(js|css)?$ {
    expires 7d;
    access_log off;
  }
  location ~ /(\.user\.ini|\.ht|\.git|\.svn|\.project|LICENSE|README\.md) {
    deny all;
  }
  location /.well-known {
    allow all;
  }
}
```

