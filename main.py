"""
Author: Wang Zhuoyang
Date: 2025-03-04
Description: 应用程序入口，启动FastAPI服务
"""

import uvicorn
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / 'src'))

def main():
    """启动FastAPI服务"""
    uvicorn.run(
        "api:app", 
        host="0.0.0.0",
        port=7999,
        reload=True
    )

if __name__ == "__main__":
    main() 