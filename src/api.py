"""
Author: Wang Zhuoyang
Date: 2025-03-04
Description: FastAPI接口定义，处理气井积液分析的HTTP请求
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Union, Dict
from process import Config, LiquidLoadingDetector
from data_loader import WellDataLoader
from utils import plot_features
import pandas as pd

app = FastAPI(
    title="液体积液分析API",
    description="用于分析气井液体积液情况的REST API",
    version="1.0.0"
)

# 定义数据模型
class TableData(BaseModel):
    time: List[str]
    oil_pressure: List[float]
    casing_pressure: List[float]
    tubing_pressure: List[float]
    gas_flow_rate: List[float]
    total_gas_flow: List[float]
    switch_status: List[int]

# 定义配置模型
class ConfigParams(BaseModel):
    data_days: Optional[int] = 20       # 要分析的数据天数
    days_window: Optional[int] = 10     # 积液判断的滑动窗口大小
    change_threshold: Optional[float] = 20
    stable_pressure_threshold: Optional[float] = 5
    zigzag_threshold: Optional[float] = 20
    zigzag_window: Optional[int] = 3
    pressure_diff_threshold: Optional[float] = 3.0
    closed_hours: Optional[int] = 48

# 定义请求模型
class AnalysisRequest(BaseModel):
    data_source: Union[str, TableData]  # 可以是文件路径或表格数据
    config_params: Optional[ConfigParams] = None  # 可选的配置参数

def process_data_source(data_source: Union[str, Dict], data_days: int) -> pd.DataFrame:
    """
    处理数据源，支持Excel文件路径或JSON数据
    
    参数:
    data_source: Excel文件路径或表格数据字典
    data_days: 要分析的数据天数
    
    返回:
    DataFrame: 处理后的数据
    """
    if isinstance(data_source, str):
        # 处理Excel文件
        return WellDataLoader.load_data(
            file_path=data_source,
            data_days=data_days  # 修改参数名
        )
    else:
        # 处理JSON数据
        try:
            # 创建DataFrame
            df = pd.DataFrame(data_source)
            # 设置时间索引
            df['time'] = pd.to_datetime(df['time'])
            df.set_index('time', inplace=True)
            
            # 获取时间范围
            latest_date = df.index.max().normalize()
            start_date = latest_date - pd.Timedelta(days=data_days)  # 使用data_days
            
            # 筛选数据
            mask = (df.index >= start_date) & (df.index <= latest_date)
            df = df[mask]
            # 重采样
            return df.resample('h').first()
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"数据处理失败: {str(e)}")

@app.post("/analyze")
async def analyze_well(request: AnalysisRequest):
    """执行气井积液分析"""
    try:
        # 创建配置
        config = Config()
        
        # 获取配置参数
        config_params = request.config_params or ConfigParams()
        
        # 更新配置
        for key, value in config_params.model_dump().items():
            if value is not None:
                setattr(config, key, value)
        
        # 处理数据源
        if isinstance(request.data_source, str):
            # Excel文件路径
            df_resampled = process_data_source(
                request.data_source,
                config.data_days
            )
        else:
            # JSON数据
            df_resampled = process_data_source(
                request.data_source.model_dump(),
                config.data_days
            )
        
        # 创建检测器并执行分析
        detector = LiquidLoadingDetector(config)
        results, daily_gas_production = detector.analyze(df_resampled)
        
        # 生成图表
        # plot_features(df_resampled, daily_gas_production, results)
        
        # 返回结果
        return {
            "status": "success",
            "data_info": {
                "start_time": df_resampled.index.min().strftime('%Y-%m-%d %H:%M:%S'),
                "end_time": df_resampled.index.max().strftime('%Y-%m-%d %H:%M:%S'),
                "config": config_params.model_dump(),
                "data_points": len(df_resampled)
            },
            "analysis_results": results,
            "treatment_stage": results.get('stage', '未知')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"} 