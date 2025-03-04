"""
Author: Wang Zhuoyang
Date: 2025-03-04
Description: 气井积液检测的核心处理逻辑，包含多种积液判断方法
"""

from typing import Tuple, Dict, List
import pandas as pd
import numpy as np
from datetime import datetime
from utils import plot_features
from config import Config
from data_loader import WellDataLoader

class LiquidLoadingDetector:
    """积液检测器"""
    
    def __init__(self, config: Config):
        self.config = config
        self.results = self._init_results()
        self.daily_gas_production = None
        self.daily_total = None
    
    @staticmethod
    def _init_results() -> Dict:
        """初始化结果字典"""
        return {
            'method1': {'result': False, 'periods': []},
            'method2': {'result': False, 'periods': []},
            'method3': {'result': False, 'periods': []},
            'method4': {'result': False, 'periods': []}
        }
    
    def analyze(self, df: pd.DataFrame) -> Tuple[Dict, pd.Series]:
        """执行完整的积液分析"""
        self._calculate_daily_production(df)
        self._run_all_checks(df)
        self._determine_treatment_stage()
        self.print_results()
        return self.results, self.daily_gas_production
    
    def _calculate_daily_production(self, df: pd.DataFrame) -> None:
        """计算日产气量"""
        open_well_data = df[df['switch_status'] == 0]
        self.daily_total = open_well_data['total_gas_flow'].resample('D').last()
        self.daily_gas_production = self.daily_total.diff()
    
    def _run_all_checks(self, df: pd.DataFrame) -> None:
        """运行所有检查方法"""
        check_methods = {
            'method1': self.check_pressure_up_flow_down,
            'method2': self.check_stable_pressure_flow_down,
            'method3': self.check_sawtooth_pattern,
            'method4': self.check_pressure_difference
        }
        
        for method_name, check_method in check_methods.items():
            self.results[method_name]['result'], self.results[method_name]['periods'] = check_method(df)
    
    def check_pressure_up_flow_down(self, df):
        """方法1：检查套压上升，产气量下降"""
        found_periods = []
        open_well_data = df[df['switch_status'] == 0]
        daily_pressure = open_well_data['casing_pressure'].resample('D').mean()
        
        common_dates = daily_pressure.index.intersection(self.daily_gas_production.index)
        daily_pressure = daily_pressure[common_dates]
        daily_prod = self.daily_gas_production[common_dates]
        
        for i in range(len(daily_prod) - self.config.days_window):
            start_pressure = daily_pressure.iloc[i]
            end_pressure = daily_pressure.iloc[i+self.config.days_window-1]
            start_prod = daily_prod.iloc[i]
            end_prod = daily_prod.iloc[i+self.config.days_window-1]
            
            pressure_change = (end_pressure - start_pressure) / start_pressure * 100
            flow_change = (end_prod - start_prod) / start_prod * 100 if start_prod != 0 else 0
            
            if pressure_change > self.config.change_threshold and flow_change < -self.config.change_threshold:
                period = {
                    'start_date': daily_pressure.index[i].strftime('%Y-%m-%d'),
                    'end_date': daily_pressure.index[i+self.config.days_window-1].strftime('%Y-%m-%d'),
                    'pressure_change': f"{pressure_change:.1f}%",
                    'flow_change': f"{flow_change:.1f}%"
                }
                found_periods.append(period)
        
        return bool(found_periods), found_periods
    
    def check_stable_pressure_flow_down(self, df):
        """方法2：检查套压稳定，产气量下降"""
        found_periods = []
        open_well_data = df[df['switch_status'] == 0]
        daily_pressure = open_well_data['casing_pressure'].resample('D').mean()
        
        common_dates = daily_pressure.index.intersection(self.daily_gas_production.index)
        daily_pressure = daily_pressure[common_dates]
        daily_prod = self.daily_gas_production[common_dates]
        
        for i in range(len(daily_prod) - self.config.days_window):
            start_pressure = daily_pressure.iloc[i]
            end_pressure = daily_pressure.iloc[i+self.config.days_window-1]
            start_prod = daily_prod.iloc[i]
            end_prod = daily_prod.iloc[i+self.config.days_window-1]
            
            pressure_change = abs((end_pressure - start_pressure) / start_pressure * 100)
            flow_change = (end_prod - start_prod) / start_prod * 100 if start_prod != 0 else 0
            
            if pressure_change < self.config.stable_pressure_threshold and flow_change < -self.config.change_threshold:
                period = {
                    'start_date': daily_pressure.index[i].strftime('%Y-%m-%d'),
                    'end_date': daily_pressure.index[i+self.config.days_window-1].strftime('%Y-%m-%d'),
                    'pressure_change': f"{pressure_change:.1f}%",
                    'flow_change': f"{flow_change:.1f}%"
                }
                found_periods.append(period)
        
        return bool(found_periods), found_periods
    
    def check_sawtooth_pattern(self, df):
        """方法3：检查套压和产气量的锯齿波动"""
        found_periods = []
        open_well_data = df[df['switch_status'] == 0]
        daily_pressure = open_well_data['casing_pressure'].resample('D').mean()
        
        common_dates = daily_pressure.index.intersection(self.daily_gas_production.index)
        daily_pressure = daily_pressure[common_dates]
        daily_prod = self.daily_gas_production[common_dates]
        
        # 使用配置的窗口大小
        for i in range(len(daily_pressure) - self.config.zigzag_window):
            pressure_window = daily_pressure.iloc[i:i+self.config.zigzag_window]
            flow_window = daily_prod.iloc[i:i+self.config.zigzag_window]
            
            # 计算波动幅度
            pressure_fluctuation = (pressure_window.max() - pressure_window.min()) / pressure_window.mean() * 100
            flow_fluctuation = (flow_window.max() - flow_window.min()) / flow_window.mean() * 100 if flow_window.mean() != 0 else 0
            
            if pressure_fluctuation > self.config.zigzag_threshold and flow_fluctuation > self.config.zigzag_threshold:
                period = {
                    'start_date': pressure_window.index[0].strftime('%Y-%m-%d'),
                    'end_date': pressure_window.index[-1].strftime('%Y-%m-%d'),
                    'pressure_fluctuation': f"{pressure_fluctuation:.1f}%",
                    'flow_fluctuation': f"{flow_fluctuation:.1f}%"
                }
                found_periods.append(period)
        
        return bool(found_periods), found_periods
    
    def check_pressure_difference(self, df):
        """方法4：检查关井压差"""
        found_periods = []
        closed_periods = df[df['switch_status'] == 1]
        
        if len(closed_periods) >= self.config.closed_hours:
            for i in range(len(closed_periods) - self.config.closed_hours):
                window = closed_periods.iloc[i:i+self.config.closed_hours]
                time_diff = (window.index[-1] - window.index[0]).total_seconds() / 3600
                
                if time_diff == self.config.closed_hours - 1:  # 确保是连续的时间段
                    pressure_diff = abs(window['oil_pressure'] - window['casing_pressure'])
                    if (pressure_diff > self.config.pressure_diff_threshold).any():
                        period = {
                            'start_date': window.index[0].strftime('%Y-%m-%d %H:%M'),
                            'end_date': window.index[-1].strftime('%Y-%m-%d %H:%M'),
                            'max_pressure_diff': f"{pressure_diff.max():.2f} MPa"
                        }
                        found_periods.append(period)
        
        return bool(found_periods), found_periods
    
    def _determine_treatment_stage(self):
        """
        根据日产气量判断所处阶段
        只有在检测到积液时才返回阶段，否则返回正常生产
        """
        # 检查是否存在积液
        has_liquid_loading = any(self.results[method]['result'] for method in ['method1', 'method2', 'method3', 'method4'])
        
        if not has_liquid_loading:
            self.results['stage'] = '正常生产阶段'
            return
        
        # 获取最后一次积液发生的日期
        last_liquid_loading_date = None
        for method in ['method1', 'method2', 'method3', 'method4']:
            if self.results[method]['result'] and self.results[method]['periods']:
                # 获取每个方法检测到的最后一个积液期间的结束日期
                method_last_date = pd.to_datetime(self.results[method]['periods'][-1]['end_date'])
                if last_liquid_loading_date is None or method_last_date > last_liquid_loading_date:
                    last_liquid_loading_date = method_last_date
        
        # 获取积液发生时的日产气量
        if last_liquid_loading_date:
            production = self.daily_gas_production[self.daily_gas_production.index <= last_liquid_loading_date].iloc[-1]
        else:
            # 如果没有找到具体日期（理论上不会发生），使用最近的产量
            production = self.daily_gas_production.iloc[-1]
        
        # 转换为10^4立方米/天
        production_10k = production / 1e4
        
        # 根据积液发生时的产量判断阶段
        if production_10k >= 1.0:
            self.results['stage'] = '支柱携带阶段'
        elif 0.8 <= production_10k < 1.0:
            self.results['stage'] = '过渡阶段'
        elif 0.5 <= production_10k < 0.8:
            self.results['stage'] = '泡沫助排阶段'
        elif 0.3 <= production_10k < 0.5:
            self.results['stage'] = '柱塞气举阶段'
        else:
            self.results['stage'] = '间歇生产阶段'
    
    def print_results(self):
        """打印检查结果"""
        print("\n积液判断结果:")
        
        methods = {
            'method1': ('1. 套压上升产气量下降',
                       lambda p: f"时间段: {p['start_date']} 至 {p['end_date']}\n"
                               f"套压上升: {p['pressure_change']}\n"
                               f"产量下降: {p['flow_change']}"),
            'method2': ('2. 套压稳定产气量下降',
                       lambda p: f"时间段: {p['start_date']} 至 {p['end_date']}\n"
                               f"套压变化: {p['pressure_change']}\n"
                               f"产量下降: {p['flow_change']}"),
            'method3': ('3. 套压产气量锯齿波动',
                       lambda p: f"时间段: {p['start_date']} 至 {p['end_date']}\n"
                               f"套压波动: {p['pressure_fluctuation']}\n"
                               f"产量波动: {p['flow_fluctuation']}"),
            'method4': ('4. 关井压差大于3MPa',
                       lambda p: f"时间段: {p['start_date']} 至 {p['end_date']}\n"
                               f"最大压差: {p['max_pressure_diff']}")
        }
        
        for method, (title, formatter) in methods.items():
            print(f"\n{title}: {'是' if self.results[method]['result'] else '否'}")
            if self.results[method]['result']:
                for period in self.results[method]['periods']:
                    print(formatter(period))

def load_well_data(file_path, sheet_name, days_window):
    """
    加载气井数据
    
    参数:
    file_path: Excel文件路径
    sheet_name: 工作表名称
    days_window: 要分析的天数（从当前往前推）
    
    返回:
    df_resampled: 重采样后的数据框
    """
    # 定义要读取的列名和新的列名映射
    columns_map = {
        2: 'time',              # 时间
        3: 'oil_pressure',      # 油压
        7: 'casing_pressure',   # 套压
        11: 'tubing_pressure',  # 管压
        15: 'gas_flow_rate',    # 瞬时气体流量
        19: 'total_gas_flow',   # 累计气体流量
        23: 'temperature',      # 温度
        27: 'switch_status'     # 开关状态
    }
    
    # 读取特定sheet，重命名列
    df = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        usecols=list(columns_map.keys()),
        names=list(columns_map.values())
    )
    
    # 将time列设置为索引并确保是datetime格式
    df.set_index('time', inplace=True)
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        df.index = pd.to_datetime(df.index, format='%Y-%m-%d %H:%M:%S')
    
    # 获取数据中最新的时间点
    latest_date = df.index.max().normalize()  # 使用数据中最新的日期
    start_date = latest_date - pd.Timedelta(days=days_window-1)  # 减去days_window-1天
    
    # 按日期范围筛选数据
    mask = (df.index >= start_date) & (df.index <= latest_date)
    df = df[mask]
    
    # 按小时重采样并获取每小时第一条数据
    df_resampled = df.resample('h').first()
    
    # 打印数据范围信息
    print("\n数据时间范围:")
    print("开始时间:", df.index.min())
    print("结束时间:", df.index.max())
    print("数据天数:", days_window, "天")  # 直接使用days_window
    
    return df_resampled

# 修改示例代码
if __name__ == "__main__":
    # 配置参数
    config = Config()
    
    # 加载数据
    df_resampled = load_well_data(
        file_path='/Users/wangzhuoyang/oil/history_oil.xlsx',
        sheet_name='佳16-3C1',
        days_window=config.days_window
    )
    
    # 创建检测器实例
    detector = LiquidLoadingDetector(config)
    
    # 执行分析
    results, daily_gas_production = detector.analyze(df_resampled)
    
    # 绘制特征图
    plot_features(df_resampled, daily_gas_production, results)