"""
示例数据生成器

生成用于测试的示例价格和基本面数据
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Union, Optional


def generate_price_data(ticker: str, start_date: str, end_date: str, 
                       volatility: float = 0.02, trend: float = 0.0001) -> List[Dict[str, Any]]:
    """
    生成示例价格数据
    
    参数:
        ticker: 股票代码
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        volatility: 波动率
        trend: 趋势因子 (正值表示上升趋势，负值表示下降趋势)
        
    返回:
        价格数据列表
    """
    # 转换日期
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    # 生成日期范围
    date_range = pd.date_range(start=start, end=end, freq='B')  # 'B'表示工作日
    
    # 设置初始价格
    initial_price = 100.0
    if ticker == 'AAPL':
        initial_price = 150.0
    elif ticker == 'MSFT':
        initial_price = 300.0
    elif ticker == 'GOOGL':
        initial_price = 120.0
    
    # 生成随机价格
    np.random.seed(hash(ticker) % 10000)  # 使用股票代码作为随机种子
    
    # 生成随机走势
    returns = np.random.normal(trend, volatility, size=len(date_range))
    
    # 添加一些跳跃
    jumps = np.random.choice([0, 1], size=len(date_range), p=[0.98, 0.02])
    jump_size = np.random.normal(0, volatility * 5, size=len(date_range))
    returns = returns + jumps * jump_size
    
    # 计算价格
    prices = initial_price * (1 + returns).cumprod()
    
    # 生成OHLC数据
    result = []
    for i, date in enumerate(date_range):
        price = prices[i]
        daily_volatility = volatility * price
        
        # 生成日内价格
        open_price = price * (1 + np.random.normal(0, 0.2 * volatility))
        high_price = max(open_price, price) * (1 + abs(np.random.normal(0, 0.5 * volatility)))
        low_price = min(open_price, price) * (1 - abs(np.random.normal(0, 0.5 * volatility)))
        close_price = price
        
        # 生成成交量
        volume = int(np.random.normal(1000000, 500000))
        if volume < 0:
            volume = 100000
        
        # 添加到结果
        result.append({
            'date': date.strftime('%Y-%m-%d'),
            'open': float(open_price),
            'high': float(high_price),
            'low': float(low_price),
            'close': float(close_price),
            'volume': volume,
            'adjusted_close': float(close_price)
        })
    
    return result


def generate_fundamental_data(ticker: str) -> Dict[str, Any]:
    """
    生成示例基本面数据
    
    参数:
        ticker: 股票代码
        
    返回:
        基本面数据字典
    """
    # 基于股票代码设置不同的基本面数据
    if ticker == 'AAPL':
        return {
            'ticker': ticker,
            'name': 'Apple Inc.',
            'sector': 'Technology',
            'industry': 'Consumer Electronics',
            'market_cap': 3000000000000,
            'pe_ratio': 35.0,
            'forward_pe': 30.0,
            'dividend_yield': 0.005,
            'beta': 1.2,
            'eps': 4.5,
            'price_to_book': 40.0,
            'debt_to_equity': 1.5,
            'return_on_equity': 0.35,
            'profit_margins': 0.25,
            'revenue_growth': 0.15,
            'current_ratio': 1.5,
            'quick_ratio': 1.2,
            'target_price': 180.0,
            'analyst_rating': 2.0,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    elif ticker == 'MSFT':
        return {
            'ticker': ticker,
            'name': 'Microsoft Corporation',
            'sector': 'Technology',
            'industry': 'Software',
            'market_cap': 2500000000000,
            'pe_ratio': 32.0,
            'forward_pe': 28.0,
            'dividend_yield': 0.008,
            'beta': 0.9,
            'eps': 9.0,
            'price_to_book': 15.0,
            'debt_to_equity': 0.5,
            'return_on_equity': 0.4,
            'profit_margins': 0.35,
            'revenue_growth': 0.18,
            'current_ratio': 2.0,
            'quick_ratio': 1.8,
            'target_price': 350.0,
            'analyst_rating': 1.5,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    elif ticker == 'GOOGL':
        return {
            'ticker': ticker,
            'name': 'Alphabet Inc.',
            'sector': 'Technology',
            'industry': 'Internet Content & Information',
            'market_cap': 2000000000000,
            'pe_ratio': 25.0,
            'forward_pe': 22.0,
            'dividend_yield': 0.0,
            'beta': 1.1,
            'eps': 5.0,
            'price_to_book': 6.0,
            'debt_to_equity': 0.2,
            'return_on_equity': 0.25,
            'profit_margins': 0.3,
            'revenue_growth': 0.2,
            'current_ratio': 3.0,
            'quick_ratio': 2.8,
            'target_price': 150.0,
            'analyst_rating': 1.8,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    else:
        # 默认数据
        return {
            'ticker': ticker,
            'name': f'{ticker} Inc.',
            'sector': 'Unknown',
            'industry': 'Unknown',
            'market_cap': 1000000000,
            'pe_ratio': 20.0,
            'forward_pe': 18.0,
            'dividend_yield': 0.01,
            'beta': 1.0,
            'eps': 2.0,
            'price_to_book': 5.0,
            'debt_to_equity': 1.0,
            'return_on_equity': 0.2,
            'profit_margins': 0.15,
            'revenue_growth': 0.1,
            'current_ratio': 1.5,
            'quick_ratio': 1.2,
            'target_price': 100.0,
            'analyst_rating': 2.5,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


def prices_to_df(prices: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    将价格数据转换为pandas DataFrame
    
    参数:
        prices: 价格数据列表
        
    返回:
        pandas DataFrame
    """
    if not prices:
        return pd.DataFrame()
    
    df = pd.DataFrame(prices)
    
    # 将日期列转换为datetime类型并设为索引
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    return df


# 示例使用
if __name__ == "__main__":
    # 生成示例价格数据
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')
    
    prices = generate_price_data('AAPL', start_date, end_date)
    print(f"生成了 {len(prices)} 条价格记录")
    
    # 转换为DataFrame
    df = prices_to_df(prices)
    print(f"DataFrame 形状: {df.shape}")
    
    # 生成示例基本面数据
    fundamentals = generate_fundamental_data('AAPL')
    print(f"基本面数据: {fundamentals['name']}, PE={fundamentals['pe_ratio']}")