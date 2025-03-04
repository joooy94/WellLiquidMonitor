# 使用Python 3.12作为基础镜像
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY ../requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制源代码和配置
COPY ../src ./src
COPY ../config ./config
COPY ../main.py .

# 暴露端口
EXPOSE 7999

# 启动命令
CMD ["python", "main.py"] 