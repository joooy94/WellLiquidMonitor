"""
Author: Wang Zhuoyang
Date: 2025-03-04
Description: 工具函数模块，包含数据可视化等辅助功能
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from pathlib import Path

def plot_features(df, daily_gas_production, results, output_dir='data/output'):
    """
    绘制特征随时间的变化图
    
    参数:
    df: 原始数据DataFrame
    daily_gas_production: 日产气量序列
    results: 分析结果字典
    output_dir: 图表输出目录
    """
    # 确保输出目录存在
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # Mac系统
    plt.rcParams['axes.unicode_minus'] = False
    
    # 创建子图
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(15, 12))
    fig.suptitle('Well Liquid Loading Analysis', fontsize=16)
    
    # 1. 套压变化
    daily_pressure = df[df['switch_status'] == 0]['casing_pressure'].resample('D').mean()
    ax1.plot(daily_pressure.index, daily_pressure.values, 'b-', label='Casing Pressure')
    ax1.set_ylabel('Casing Pressure (MPa)')
    ax1.set_title('Casing Pressure vs Time')
    ax1.grid(True)
    ax1.legend()
    
    # 标记方法1和方法2发现的时间段
    for method, color in [('method1', 'red'), ('method2', 'green')]:
        if results[method]['result']:
            for period in results[method]['periods']:
                start = pd.to_datetime(period['start_date'])
                end = pd.to_datetime(period['end_date'])
                ax1.axvspan(start, end, color=color, alpha=0.2)
    
    # 2. 日产气量变化
    ax2.plot(daily_gas_production.index, daily_gas_production.values, 'g-', label='Daily Gas Production')
    ax2.set_ylabel('Daily Gas Production (m³/d)')
    ax2.set_title('Daily Gas Production vs Time')
    ax2.grid(True)
    ax2.legend()
    
    # 3. 油压和套压差值
    pressure_diff = abs(df['oil_pressure'] - df['casing_pressure'])
    ax3.plot(df.index, pressure_diff, 'r-', label='Pressure Difference')
    ax3.set_ylabel('Pressure Difference (MPa)')
    ax3.set_title('Oil-Casing Pressure Difference vs Time')
    ax3.axhline(y=3.0, color='r', linestyle='--', label='3MPa Threshold')
    ax3.grid(True)
    ax3.legend()
    
    # 标记方法4发现的时间段
    if results['method4']['result']:
        for period in results['method4']['periods']:
            start = pd.to_datetime(period['start_date'])
            end = pd.to_datetime(period['end_date'])
            ax3.axvspan(start, end, color='red', alpha=0.2)
    
    # 4. 开关井状态
    ax4.plot(df.index, df['switch_status'], 'k-', label='Well Status')
    ax4.set_ylabel('Status')
    ax4.set_title('Well Status (1-Closed, 0-Open)')
    ax4.grid(True)
    ax4.legend()
    
    # 设置x轴格式
    for ax in [ax1, ax2, ax3, ax4]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))  # 每天显示一个刻度
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    # 调整布局
    plt.tight_layout()
    
    # 使用指定目录保存图片
    plt.savefig(output_path / 'feature_analysis.png', dpi=300, bbox_inches='tight')
    plt.close() 