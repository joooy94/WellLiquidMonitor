"""
Author: Wang Zhuoyang
Date: 2025-03-04
Description: 工具函数模块，包含数据可视化等辅助功能
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_features(df, daily_gas_production, results):
    """
    绘制特征随时间的变化图
    
    参数:
    df: 原始数据DataFrame
    daily_gas_production: 日产气量序列
    results: 分析结果字典
    """
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # Mac系统
    plt.rcParams['axes.unicode_minus'] = False
    
    # 创建子图
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(15, 12))
    fig.suptitle('气井运行特征分析', fontsize=16)
    
    # 1. 套压变化
    daily_pressure = df[df['switch_status'] == 0]['casing_pressure'].resample('D').mean()
    ax1.plot(daily_pressure.index, daily_pressure.values, 'b-', label='套压')
    ax1.set_ylabel('套压 (MPa)')
    ax1.set_title('套压随时间变化')
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
    ax2.plot(daily_gas_production.index, daily_gas_production.values, 'g-', label='日产气量')
    ax2.set_ylabel('日产气量')
    ax2.set_title('日产气量随时间变化')
    ax2.grid(True)
    ax2.legend()
    
    # 3. 油压和套压差值
    pressure_diff = abs(df['oil_pressure'] - df['casing_pressure'])
    ax3.plot(df.index, pressure_diff, 'r-', label='油套压差')
    ax3.set_ylabel('压差 (MPa)')
    ax3.set_title('油套压差随时间变化')
    ax3.axhline(y=3.0, color='r', linestyle='--', label='3MPa阈值')
    ax3.grid(True)
    ax3.legend()
    
    # 标记方法4发现的时间段
    if results['method4']['result']:
        for period in results['method4']['periods']:
            start = pd.to_datetime(period['start_date'])
            end = pd.to_datetime(period['end_date'])
            ax3.axvspan(start, end, color='red', alpha=0.2)
    
    # 4. 开关井状态
    ax4.plot(df.index, df['switch_status'], 'k-', label='开关井状态')
    ax4.set_ylabel('状态')
    ax4.set_title('开关井状态 (1-关井，0-开井)')
    ax4.grid(True)
    ax4.legend()
    
    # 设置x轴格式
    for ax in [ax1, ax2, ax3, ax4]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))  # 每天显示一个刻度
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig('feature_analysis.png', dpi=300, bbox_inches='tight')
    plt.close() 