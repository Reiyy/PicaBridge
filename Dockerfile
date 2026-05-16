# 前端
FROM node:20-slim AS frontend-builder

WORKDIR /build

COPY web/src/package.json web/src/package-lock.json* ./
RUN npm install

COPY web/src/ ./
RUN npm run build

# 哔咔桥
FROM python:3.12-slim

# 设置工作目录
WORKDIR /PicaBridge

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libffi-dev \
    libev-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt /PicaBridge/

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件到容器
COPY . /PicaBridge

# 从构建阶段复制前端产物
COPY --from=frontend-builder /ui /PicaBridge/web/ui

# 创建头像上传目录
RUN mkdir -p /PicaBridge/web/assets/img/avatar
# 创建自定义目录
RUN mkdir -p /PicaBridge/web/diy

# 复制 config.example.json 到 config.json
RUN cp /PicaBridge/config.example.json /PicaBridge/config.json

# 默认端口
EXPOSE 7777

ENV PYTHONUNBUFFERED=1

# 启动初始化
CMD ["python", "PunchPica.py"]