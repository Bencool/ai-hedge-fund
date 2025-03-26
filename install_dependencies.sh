#!/bin/bash
# 安装风险管理系统所需的依赖项

echo "安装风险管理系统依赖..."

# 安装主要依赖
pip install yfinance pandas numpy matplotlib seaborn scipy diskcache

# 安装其他可能需要的依赖
pip install requests python-dotenv pydantic

echo "依赖安装完成！"