"""
示例数据适配器

使用示例数据生成器提供测试数据
"""
from typing import List, Dict, Any, Union, Optional
from datetime import datetime

from .base import BaseAdapter
from ..sample_data import generate_price_data, generate_fundamental_data


class SampleDataAdapter(BaseAdapter):
    """
    示例数据适配器
    
    使用生成的示例数据进行测试
    """
    
    def __init__(self):
        """初始化示例数据适配器"""
        super().__init__()
    
    def get_prices(self, ticker: str, start_date: Union[str, datetime], 
                  end_date: Union[str, datetime], interval: str = '1d') -> List[Dict[str, Any]]:
        """
        获取示例价格数据
        
        参数:
            ticker: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            interval: 数据间隔 ('1d', '1wk', '1mo')
            
        返回:
            包含价格数据的字典列表
        """
        try:
            # 格式化参数
            ticker = self.validate_ticker(ticker)
            start = self.format_date(start_date)
            end = self.format_date(end_date)
            
            # 生成示例数据
            # 根据股票代码设置不同的波动率和趋势
            volatility = 0.02
            trend = 0.0001
            
            if ticker == 'AAPL':
                volatility = 0.015
                trend = 0.0002
            elif ticker == 'MSFT':
                volatility = 0.012
                trend = 0.0003
            elif ticker == 'GOOGL':
                volatility = 0.018
                trend = 0.0001
            
            # 生成数据
            prices = generate_price_data(
                ticker=ticker,
                start_date=start,
                end_date=end,
                volatility=volatility,
                trend=trend
            )
            
            return prices
            
        except Exception as e:
            self.handle_error(e, f"SampleData.get_prices({ticker})")
            return []
    
    def get_fundamentals(self, ticker: str) -> Dict[str, Any]:
        """
        获取示例基本面数据
        
        参数:
            ticker: 股票代码
            
        返回:
            包含基本面数据的字典
        """
        try:
            ticker = self.validate_ticker(ticker)
            
            # 生成示例基本面数据
            fundamentals = generate_fundamental_data(ticker)
            
            return fundamentals
            
        except Exception as e:
            self.handle_error(e, f"SampleData.get_fundamentals({ticker})")
            return {'ticker': ticker, 'error': str(e)}
    
    def get_options_data(self, ticker: str, expiration_date: Optional[str] = None) -> Dict[str, Any]:
        """
        获取示例期权数据
        
        参数:
            ticker: 股票代码
            expiration_date: 到期日 (可选)
            
        返回:
            包含期权数据的字典
        """
        # 简单的示例期权数据
        return {
            'ticker': ticker,
            'expiration_date': expiration_date or '2025-06-20',
            'available_expirations': ['2025-06-20', '2025-09-19', '2025-12-19'],
            'calls': [
                {
                    'strike': 150.0,
                    'lastPrice': 10.5,
                    'bid': 10.4,
                    'ask': 10.6,
                    'volume': 1000,
                    'openInterest': 5000,
                    'impliedVolatility': 0.25
                }
            ],
            'puts': [
                {
                    'strike': 150.0,
                    'lastPrice': 5.2,
                    'bid': 5.1,
                    'ask': 5.3,
                    'volume': 800,
                    'openInterest': 4000,
                    'impliedVolatility': 0.28
                }
            ]
        }
    
    def get_historical_dividends(self, ticker: str, start_date: Union[str, datetime], 
                               end_date: Union[str, datetime]) -> List[Dict[str, Any]]:
        """
        获取示例历史分红数据
        
        参数:
            ticker: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        返回:
            包含分红数据的字典列表
        """
        # 简单的示例分红数据
        if ticker == 'AAPL':
            return [
                {'date': '2024-05-15', 'amount': 0.24},
                {'date': '2024-08-15', 'amount': 0.24},
                {'date': '2024-11-15', 'amount': 0.25},
                {'date': '2025-02-15', 'amount': 0.25}
            ]
        elif ticker == 'MSFT':
            return [
                {'date': '2024-05-20', 'amount': 0.68},
                {'date': '2024-08-20', 'amount': 0.68},
                {'date': '2024-11-20', 'amount': 0.70},
                {'date': '2025-02-20', 'amount': 0.70}
            ]
        else:
            return []