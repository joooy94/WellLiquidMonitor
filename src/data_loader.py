"""
Author: Wang Zhuoyang
Date: 2025-03-04
Description: 数据加载模块，负责从Excel文件或JSON数据中加载和预处理气井数据
"""

import pandas as pd

class WellDataLoader:
    """气井数据加载器"""
    
    @staticmethod
    def load_data(file_path: str, data_days: int) -> pd.DataFrame:
        """
        加载并预处理气井数据
        
        参数:
        file_path: Excel文件路径
        data_days: 要分析的数据天数
        
        返回:
        DataFrame: 处理后的数据
        """
        # 直接读取Excel文件，因为列名已经正确设置
        df = pd.read_excel(file_path)
        
        return WellDataLoader._preprocess_data(df, data_days)
    
    @staticmethod
    def _preprocess_data(df: pd.DataFrame, data_days: int) -> pd.DataFrame:
        """
        预处理数据
        
        参数:
        df: 原始数据框
        data_days: 要分析的数据天数
        """
        # 设置时间索引
        df.set_index('time', inplace=True)
        if not pd.api.types.is_datetime64_any_dtype(df.index):
            df.index = pd.to_datetime(df.index, format='%Y-%m-%d %H:%M:%S')
        
        # 获取时间范围
        latest_date = df.index.max().normalize()
        start_date = latest_date - pd.Timedelta(days=data_days)
        
        # 筛选数据
        mask = (df.index >= start_date) & (df.index <= latest_date)
        df = df[mask]
        
        # 重采样
        return df.resample('h').first() 