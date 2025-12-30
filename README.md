# Python Docker 开发环境 - 规控基础算法课程

基于 Python 3.11 和 uv 包管理器的 Docker 开发环境，用于规控基础算法课程学习。

## ✨ 特性

- 🐳 **Docker 容器化**：隔离的开发环境
- 📦 **预装工具**：Jupyter Lab, NumPy, SciPy, Matplotlib, CVXPY, OpenCV
- 🚀 **快速启动**：一键构建，立即可用
- 🔤 **中文支持**：内置 Noto CJK 字体

---

## 📂 项目结构

```
.
├── Dockerfile              # Docker 镜像定义（Python + 中文字体 + 基础工具）
├── docker-compose.yml      # Docker Compose 配置
├── base_requirements.txt   # 基础 Python 包列表
├── .devcontainer/          # VS Code Dev Container 配置
└── README.md              # 本文件
```

---

## 🚀 快速开始

### 首次使用

```bash
# 1. 构建镜像（安装 Python + 工具 + 中文字体）
docker-compose build

# 2. 启动容器
docker-compose up -d

# 3. 进入容器
docker-compose exec python-dev bash

# 你现在在容器里了！
```

---

## 💡 使用场景

### 场景 1：我想启动 Jupyter Lab

```bash
# 前置条件：确保容器正在运行
docker-compose up -d

# 方法 1：从宿主机直接启动
docker-compose exec python-dev jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root

# 方法 2：进入容器后启动
docker-compose exec python-dev bash
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root

# 复制终端显示的 URL 到浏览器打开
# 例如：http://127.0.0.1:8888/lab?token=abc123...
```

**在 Jupyter 中使用中文字体**：

```python
# 第一个 cell
import sys
sys.path.append('/workspace')

import matplotlib.pyplot as plt
# 配置中文字体
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 之后就可以正常使用中文了
plt.title('中文标题')
```

---

### 场景 2：我想创建一个新项目

```bash
# 1. 进入容器
docker-compose exec python-dev bash

# 2. 创建项目目录
mkdir -p my_project/{src,data,notebooks}
cd my_project

# 3. 创建虚拟环境（可选，用于隔离依赖）
uv venv

# 4. 激活虚拟环境
source .venv/bin/activate

# 5. 创建 requirements.txt
cat > requirements.txt << 'EOF'
# 项目特定依赖
# 基础包（numpy, pandas, matplotlib, jupyter）已在系统环境
# 这里只添加项目特定的包
scikit-learn==1.5.0
plotly==5.18.0
EOF

# 6. 安装依赖
uv pip install -r requirements.txt

# 7. 开始工作！
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root
# 或
python src/main.py
```

**理解**：
- `mkdir -p`：创建目录结构（-p 允许创建多级目录）
- `uv venv`：创建 Python 虚拟环境
- `source .venv/bin/activate`：激活虚拟环境
- 虚拟环境让每个项目的依赖独立，互不影响

---

### 场景 3：我想直接在系统环境运行（不用虚拟环境）

```bash
# 进入容器
docker-compose exec python-dev bash

# 创建项目目录
mkdir my_simple_project
cd my_simple_project

# 直接使用系统环境的包（已有 numpy, pandas, matplotlib, jupyter 等）
python << 'EOF'
import numpy as np
import pandas as pd
print("✓ 可以直接使用基础包")
print(f"NumPy: {np.__version__}")
print(f"Pandas: {pd.__version__}")
EOF

# 创建一个脚本
cat > plot.py << 'EOF'
import numpy as np
import matplotlib.pyplot as plt

# 配置中文字体
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC']
plt.rcParams['axes.unicode_minus'] = False

x = np.linspace(0, 2*np.pi, 100)
y = np.sin(x)

plt.plot(x, y)
plt.title('正弦函数')
plt.xlabel('x 轴')
plt.ylabel('y 轴')
plt.savefig('sin.png')
print('图片已保存: sin.png')
EOF

# 运行
python plot.py
```

**理解**：
- Docker 已经提供隔离，系统环境就够用
- 只有需要不同版本的包时才用虚拟环境
- `base_requirements.txt` 里的包在系统环境，所有项目可用

---

### 场景 4：我想安装新的 Python 包

#### 方法 A：安装到虚拟环境（推荐）

```bash
cd my_project
source .venv/bin/activate  # 先激活虚拟环境

# 安装包
uv pip install scikit-learn

# 查看已安装的包
uv pip list

# 保存到 requirements.txt
uv pip freeze > requirements.txt
```

#### 方法 B：安装到系统环境

```bash
# 临时设置环境变量
export UV_SYSTEM_PYTHON=1

# 安装包到系统环境
uv pip install scikit-learn

# 或者直接一行
UV_SYSTEM_PYTHON=1 uv pip install scikit-learn
```

#### 方法 C：永久添加到基础环境

```bash
# 1. 退出容器
exit

# 2. 编辑 base_requirements.txt（在宿主机）
echo "scikit-learn==1.5.0" >> base_requirements.txt

# 3. 重新构建镜像
docker-compose build

# 4. 重启容器
docker-compose down
docker-compose up -d
```

**理解**：
- 方法 A：包只在当前项目可用
- 方法 B：包在所有项目可用，但重启容器会丢失
- 方法 C：包在所有项目可用，永久保存

---

### 场景 5：我想在多个项目间切换

```bash
# 进入容器
docker-compose exec python-dev bash

# 项目 A
cd /workspace/project_a
source .venv/bin/activate
python main.py
deactivate  # 退出虚拟环境

# 项目 B
cd /workspace/project_b
source .venv/bin/activate
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root
# Ctrl+C 停止
deactivate

# 查看当前使用的 Python
which python
# 虚拟环境：/workspace/project_a/.venv/bin/python
# 系统环境：/usr/local/bin/python
```

**理解**：
- `source .venv/bin/activate`：切换到项目的虚拟环境
- `deactivate`：退出虚拟环境，回到系统环境
- 每个项目可以有不同版本的包

---

### 场景 6：我想查看容器状态和日志

```bash
# 查看运行中的容器
docker-compose ps

# 查看容器日志
docker-compose logs

# 实时查看日志（Ctrl+C 退出）
docker-compose logs -f

# 查看资源使用
docker stats
```

---

### 场景 7：我想重启或停止容器

```bash
# 重启容器
docker-compose restart

# 停止容器（保留数据）
docker-compose down

# 停止并删除所有数据（包括虚拟环境）
docker-compose down -v

# 重新启动
docker-compose up -d
```

**理解**：
- `down`：停止容器，但保留 /workspace 的文件（因为挂载）
- `down -v`：停止并删除卷，但挂载的文件仍保留
- 你的代码在宿主机，不会丢失

---

### 场景 8：我想修改基础环境

```bash
# 1. 编辑 base_requirements.txt
vim base_requirements.txt
# 或在编辑器中打开

# 2. 重新构建镜像
docker-compose build

# 3. 重启容器
docker-compose down
docker-compose up -d

# 4. 验证
docker-compose exec python-dev python -c "import scikit_learn; print('✓ 安装成功')"
```

---

### 场景 9：我想使用 VS Code 连接容器

```bash
# 1. 安装 VS Code 插件：Dev Containers

# 2. 打开此目录

# 3. 按 F1，选择：
#    Dev Containers: Reopen in Container

# 4. VS Code 会自动连接到容器，可以直接编辑代码
```

---

## 📚 学习要点

### Docker 相关

```bash
# 镜像 vs 容器
docker images              # 查看镜像（模板）
docker ps                  # 查看运行中的容器（实例）

# 构建 vs 运行
docker-compose build       # 根据 Dockerfile 构建镜像
docker-compose up -d       # 从镜像创建并运行容器

# 数据持久化
# docker-compose.yml 中的 volumes:
#   - .:/workspace
# 意思是：把当前目录挂载到容器的 /workspace
# 在容器里修改文件，宿主机立即同步
```

### Python 虚拟环境

```bash
# 为什么需要虚拟环境？
# 项目 A 需要 numpy==1.24
# 项目 B 需要 numpy==2.0
# 用虚拟环境隔离，互不冲突

# 创建虚拟环境
uv venv                    # 在当前目录创建 .venv/

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# 激活后，python 指向 .venv/bin/python

# 退出虚拟环境
deactivate

# 查看当前环境
which python
pip list
```

### uv 包管理器

```bash
# uv vs pip
# uv 是 pip 的现代替代品，更快、更好的依赖解析

# 常用命令对照
pip install requests       →  uv pip install requests
pip list                   →  uv pip list
pip freeze                 →  uv pip freeze
pip uninstall requests     →  uv pip uninstall requests

# 从文件安装
uv pip install -r requirements.txt
```

---

## 🔧 常见问题

### Q: 修改代码后需要重启容器吗？

**A:** 不需要！代码通过 volumes 挂载，修改立即生效。

### Q: 虚拟环境在哪里？

**A:** 在你创建的位置，通常是 `/workspace/your_project/.venv/`

### Q: 重启电脑后容器不见了？

**A:** 容器需要重新启动：`docker-compose up -d`

### Q: 如何彻底清理？

```bash
# 停止并删除容器
docker-compose down

# 删除镜像
docker rmi python_docker_2025-12-python-dev

# 删除所有项目文件（谨慎！）
rm -rf your_project/
```

### Q: 中文显示乱码？

**A:** 在代码开头添加：
```python
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Noto Sans CJK SC']
plt.rcParams['axes.unicode_minus'] = False
```

### Q: Jupyter 运行后有残留文件夹（.ipynb_checkpoints、.Trash-0）？

**A:** 这是正常现象，已添加到 `.gitignore` 不会提交到 Git。

清理方法：
```bash
# 方法 1：删除这些文件夹（在宿主机）
sudo rm -rf .ipynb_checkpoints .Trash-*

# 方法 2：在容器内删除（避免权限问题）
docker-compose exec python-dev rm -rf /workspace/.ipynb_checkpoints /workspace/.Trash-*
```

避免 `.Trash-0` 产生的方法：
- 在 Jupyter 中删除文件时，使用右键菜单的 "Delete" 而不是移到回收站
- 或者在容器内使用命令行删除：`rm file.ipynb`

---

## 📝 常用命令速查

### 容器管理
```bash
docker-compose build        # 构建镜像
docker-compose up -d        # 启动容器
docker-compose down         # 停止容器
docker-compose restart      # 重启容器
docker-compose exec python-dev bash  # 进入容器
docker-compose logs -f      # 查看日志
```

### 包管理
```bash
uv pip install <包名>        # 安装包
uv pip list                  # 列出已安装包
uv pip freeze > requirements.txt  # 导出依赖
uv pip install -r requirements.txt  # 安装依赖
```

### 虚拟环境
```bash
uv venv                      # 创建虚拟环境
source .venv/bin/activate    # 激活
deactivate                   # 退出
which python                 # 查看当前 Python 路径
```

### Jupyter
```bash
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root
```

---

## 🎯 推荐学习路径

### 第 1 天：熟悉 Docker
```bash
# 1. 构建并启动
docker-compose build
docker-compose up -d

# 2. 进入容器看看
docker-compose exec python-dev bash
pwd                    # 当前目录
ls                     # 列出文件
python --version       # Python 版本
exit

# 3. 查看容器状态
docker-compose ps
docker-compose logs
```

### 第 2 天：创建第一个项目
```bash
# 进入容器
docker-compose exec python-dev bash

# 创建项目
mkdir test_project
cd test_project

# 写个简单脚本
cat > hello.py << 'EOF'
import numpy as np
print(f"Hello from NumPy {np.__version__}")
EOF

# 运行
python hello.py
```

### 第 3 天：学习虚拟环境
```bash
cd test_project

# 创建虚拟环境
uv venv

# 激活
source .venv/bin/activate

# 安装包
uv pip install requests

# 查看
which python
uv pip list

# 退出
deactivate
```

### 第 4 天：使用 Jupyter
```bash
# 启动 Jupyter
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root

# 在浏览器打开，创建新 notebook，开始实验
```

### 第 5 天：多项目管理
```bash
# 创建多个项目，练习切换
mkdir project_a project_b
cd project_a && uv venv && cd ..
cd project_b && uv venv && cd ..

# 切换练习
cd project_a && source .venv/bin/activate && deactivate && cd ..
cd project_b && source .venv/bin/activate && deactivate && cd ..
```

---

## 🛠️ 技术栈

- **Python**: 3.11
- **包管理器**: uv 0.9.20
- **容器**: Docker + Docker Compose
- **开发工具**: Jupyter Lab 4.3.4
- **核心算法包**: NumPy 1.24.2, Matplotlib 3.7.1, SciPy 1.10.1, CVXPY 1.3.1, OpenCV-Python
- **数据处理**: Pandas 2.2.3
- **字体**: Noto Sans CJK（支持中日韩文字）

---

## 🎉 开始探索

```bash
# 从这里开始
docker-compose build
docker-compose up -d
docker-compose exec python-dev bash

# 你现在在一个干净的 Python 环境里了！
# 创建你的第一个项目吧 🚀
```

Happy learning! 📚
