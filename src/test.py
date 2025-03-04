"""
Author: Wang Zhuoyang
Date: 2025-03-04
Description: 测试代码
"""

from config import Config
from data_loader import WellDataLoader
from process import LiquidLoadingDetector
from utils import plot_features

def main(file_path):
    # 配置参数
    config = Config()
    
    # 加载数据
    df_resampled = WellDataLoader.load_data(
        file_path,
        days_window=config.days_window
    )
    
    # 执行分析
    detector = LiquidLoadingDetector(config)
    results, daily_gas_production = detector.analyze(df_resampled)
    
    # 绘制图表
    plot_features(df_resampled, daily_gas_production, results)

if __name__ == "__main__":
    main(file_path='/Users/wangzhuoyang/oil/src/october_data.xlsx') 