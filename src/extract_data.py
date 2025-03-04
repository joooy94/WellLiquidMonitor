import pandas as pd
from datetime import datetime
from data_loader import WellDataLoader

COLUMNS_MAP = {
    2: 'time',              # 时间
    3: 'oil_pressure',      # 油压
    7: 'casing_pressure',   # 套压
    11: 'tubing_pressure',  # 管压
    15: 'gas_flow_rate',    # 瞬时气体流量
    19: 'total_gas_flow',   # 累计气体流量
    23: 'temperature',      # 温度
    27: 'switch_status'     # 开关状态
}

def extract_date_range_data(
    input_file: str,
    sheet_name: str,
    output_file: str,
    start_date: str,
    end_date: str
) -> None:
    """
    提取指定日期范围的原始数据并保存为新的Excel文件
    
    参数:
    input_file: 输入文件路径
    sheet_name: 工作表名称
    output_file: 输出文件路径
    start_date: 开始日期 (格式: 'YYYY-MM-DD')
    end_date: 结束日期 (格式: 'YYYY-MM-DD')
    """
    # 读取原始数据
    df = pd.read_excel(
        input_file,
        sheet_name=sheet_name,
        usecols=list(COLUMNS_MAP.keys()),
        names=list(COLUMNS_MAP.values())
    )
    
    # 将time列转换为datetime格式
    df['time'] = pd.to_datetime(df['time'])
    
    # 筛选日期范围
    mask = (df['time'] >= start_date) & (df['time'] <= end_date)
    df_filtered = df[mask]
    
    # 保存到新文件
    df_filtered.to_excel(output_file, index=False)
    
    # 打印信息
    print(f"数据提取完成:")
    print(f"开始时间: {df_filtered['time'].min()}")
    print(f"结束时间: {df_filtered['time'].max()}")
    print(f"数据点数: {len(df_filtered)}")

if __name__ == "__main__":
    # 配置参数
    input_file = '/Users/wangzhuoyang/oil/history_oil.xlsx'
    sheet_name = '佳16-3C1'
    output_file = 'october_data.xlsx'
    start_date = '2024-10-10'
    end_date = '2024-10-30'
    
    # 执行数据提取
    extract_date_range_data(
        input_file=input_file,
        sheet_name=sheet_name,
        output_file=output_file,
        start_date=start_date,
        end_date=end_date
    ) 