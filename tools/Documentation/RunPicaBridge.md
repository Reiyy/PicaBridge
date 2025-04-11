# 运行PicaBridge

## 环境准备
安装 LANraragi v0.9.31+，请查看 [LRR文档](https://sugoi.gitbook.io/lanraragi/dev)

安装 Python 3.8+，请查看 [python.org](https://www.python.org/downloads/)

安装数据库 MariaDB 10.6+ or MySQL 8.0+

你还需要一个Web服务器(如Nginx)来代理PicaBridge，以及负责处理静态资源，如用户头像，分类图像等。

## 开始
开始运行PicaBridge，你可以选择提供Docker或源代码运行。

###  Docker运行
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
    environment:
      - TZ=Asia/Shanghai
    networks:
      - picabridge

networks:
  picabridge:
```

你可以修改Docker的映射端口，但如果你想修改容器内端口，请在config,json中修改。  
具体查看 [配置修改](/tools/Documentation/setconfig.md)

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

下载项目根目录中的config.example.json，将其重命名为config.json  
然后配置config.json，请查看 [配置修改](/tools/Documentation/setconfig.md)

配置完成后启动Docker ```docker compose up```  
确认运行正常后使用使用ctrl+c退出，然后使用后台运行 ```docker compose up -d```  
Enjoy, heart❤️! =w=

注：使用默认密码登录后，别忘了在APP设置中修改密码！

###  源代码运行
拉取项目 ```git clone https://github.com/Reiyy/PicaBridge.git```

进入项目文件夹 ```cd PicaBridge```

安装依赖 ```pip install -r requirements.txt ```

创建配置文件 ```cp config.example.json config.json```

根据配置文档修改config.json，[配置修改](/tools/Documentation/setconfig.md)

运行启动脚本 ```python PunchPica.py ```

Enjoy, heart❤️! =w=

##  配置Web服务器(此处使用Nginx)

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

  # 用户头像图片等静态资源直接由Nginx处理，不经过Flask
  location /assets/ {
    gzip on;
    add_header X-Frame-Options "ALLOWALL";
    add_header Content-Security-Policy "frame-ancestors 'self' *";
  }

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

