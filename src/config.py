"""
Author: Wang Zhuoyang
Date: 2025-03-04
Description: 配置管理模块，负责加载和管理气井积液分析的配置参数
"""

import yaml
from pathlib import Path
from typing import Dict

class Config:
    """积液判断配置参数"""
    def __init__(self, config_path: str = None):
        """
        初始化配置
        
        参数:
        config_path: YAML配置文件路径，如果为None则使用默认值
        """
        # 默认配置
        self.data_days = 20        # 要分析的数据天数
        self.days_window = 10      # 积液判断的滑动窗口大小
        self.change_threshold = 20
        self.stable_pressure_threshold = 5
        self.zigzag_threshold = 20
        self.zigzag_window = 3
        self.pressure_diff_threshold = 3.0
        self.closed_hours = 48
        
        # 如果提供了配置文件路径，则加载配置
        if config_path:
            self._load_config(config_path)
    
    def _load_config(self, config_path: str) -> None:
        """从YAML文件加载配置"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config: Dict = yaml.safe_load(f)
            
            # 更新配置参数
            for key, value in config.items():
                if hasattr(self, key):
                    setattr(self, key, value)
                    
        except Exception as e:
            raise ValueError(f"加载配置文件失败: {str(e)}")