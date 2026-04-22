# 选择基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /PicaBridge

# 安装系统依赖
RUN apt update && apt install -y \
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

# 复制 config.example.json 到 config.json
RUN cp /PicaBridge/config.example.json /PicaBridge/config.json

# 默认端口
EXPOSE 7777

ENV PYTHONUNBUFFERED=1

# 启动初始化
CMD ["python", "PunchPica.py"]