# ============================================================
# Python Docker 环境配置文件
# ============================================================
# 用途：定义如何构建 Docker 镜像（类似"软件安装包"）
# ============================================================

# FROM - 指定基础镜像（选择操作系统）
# python:3.11-slim - 使用官方 Python 3.11 精简版（课程要求）
# slim - 轻量级版本，体积小，只包含必要组件
FROM python:3.11-slim

# RUN - 安装中文字体和系统工具
# fonts-noto-cjk - Noto CJK 字体系列（支持中日韩文字）
# fontconfig - 字体配置工具
# libgl1 - OpenGL 库（OpenCV 需要）
# libglib2.0-0 - GLib 库（OpenCV 需要）
# fc-cache -fv - 刷新字体缓存
# rm -rf /var/lib/apt/lists/* - 清理 apt 缓存，减小镜像体积
RUN apt-get update && apt-get install -y \
    fonts-noto-cjk \
    fonts-noto-cjk-extra \
    fontconfig \
    libgl1 \
    libglib2.0-0 \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*

# COPY --from - 从另一个镜像复制文件（多阶段构建）
# ghcr.io/astral-sh/uv:latest - 从 GitHub 容器仓库获取最新的 uv
# /uv - 源文件路径（uv 程序在源镜像的位置）
# /usr/local/bin/uv - 目标路径（复制到当前镜像的位置）
# 好处：不用手动下载安装 uv，直接从官方镜像复制
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# WORKDIR - 设置工作目录
# 类似于 cd /workspace，进入容器后默认在这个目录
# 如果目录不存在会自动创建
WORKDIR /workspace

# COPY - 复制基础依赖配置文件到容器
# base_requirements.txt - 所有项目通用的依赖（jupyter, numpy, pandas 等）
# /tmp/base_requirements.txt - 临时路径，避免与挂载的文件冲突
COPY base_requirements.txt /tmp/base_requirements.txt

# RUN - 在构建时安装基础依赖到系统环境
# 这些依赖会被所有项目共享，无需在每个项目中重复安装
# 使用 UV_SYSTEM_PYTHON=1 确保安装到系统 Python
RUN UV_SYSTEM_PYTHON=1 uv pip install -r /tmp/base_requirements.txt

# ENV - 设置环境变量
# UV_SYSTEM_PYTHON=0 - 允许使用虚拟环境
# 每个项目可以在自己的虚拟环境中安装特定依赖，实现隔离
ENV UV_SYSTEM_PYTHON=0

# CMD - 容器启动时执行的默认命令
# sleep infinity - 让容器一直运行不退出
# 如果不加这个，容器启动后会立即退出
CMD ["sleep", "infinity"]
