# 基础镜像建议固定到 name:tag@sha256:digest；示例为了好读只写了标签。
FROM python:3.11-slim
WORKDIR /app
# 整个仓库只有几个小文件，直接全拷；放了 BREAK_HEALTH 文件时它也会进镜像（故障演练用）。
COPY . .
EXPOSE 8000
CMD ["python", "app.py"]
