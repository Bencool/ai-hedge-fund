"""
Yahoo Finance 数据源适配器

使用yfinance库获取股票数据
"""
import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Union, Optional

from .base import BaseAdapter


class YahooFinanceAdapter(BaseAdapter):
    """
    Yahoo Finance API适配器
    
    使用yfinance库获取股票价格和基本面数据
    """
    
    def __init__(self):
        """初始化Yahoo Finance适配器"""
        super().__init__()
        # Yahoo Finance不需要API密钥
    
    def get_prices(self, ticker: str, start_date: Union[str, datetime], 
                  end_date: Union[str, datetime], interval: str = '1d') -> List[Dict[str, Any]]:
        """
        从Yahoo Finance获取历史价格数据
        
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
            
            # 获取数据
            data = yf.download(
                ticker,
                start=start,
                end=end,
                interval=interval,
                progress=False
            )
            
            # 如果数据为空，返回空列表
            if data.empty:
                return []
            
            # 重置索引，将日期转换为列
            data = data.reset_index()
            
            # 将DataFrame转换为字典列表
            result = []
            for _, row in data.iterrows():
                # 处理日期格式 - 确保Date是datetime对象
                if isinstance(row['Date'], pd.Timestamp):
                    date_str = row['Date'].strftime('%Y-%m-%d')
                else:
                    # 如果不是Timestamp，尝试转换
                    date_str = pd.to_datetime(row['Date']).strftime('%Y-%m-%d')
                
                price_data = {
                    'date': date_str,
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume']),
                    'adjusted_close': float(row['Adj Close']) if 'Adj Close' in row else None
                }
                result.append(price_data)
            
            return result
            
        except Exception as e:
            self.handle_error(e, f"YahooFinance.get_prices({ticker})")
            return []
    
    def get_fundamentals(self, ticker: str) -> Dict[str, Any]:
        """
        获取股票基本面数据
        
        参数:
            ticker: 股票代码
            
        返回:
            包含基本面数据的字典
        """
        try:
            ticker = self.validate_ticker(ticker)
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # 提取关键基本面数据
            fundamentals = {
                'ticker': ticker,
                'name': info.get('shortName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap', None),
                'pe_ratio': info.get('trailingPE', None),
                'forward_pe': info.get('forwardPE', None),
                'dividend_yield': info.get('dividendYield', None),
                'beta': info.get('beta', None),
                'eps': info.get('trailingEps', None),
                'price_to_book': info.get('priceToBook', None),
                'debt_to_equity': info.get('debtToEquity', None),
                'return_on_equity': info.get('returnOnEquity', None),
                'profit_margins': info.get('profitMargins', None),
                'revenue_growth': info.get('revenueGrowth', None),
                'current_ratio': info.get('currentRatio', None),
                'quick_ratio': info.get('quickRatio', None),
                'target_price': info.get('targetMeanPrice', None),
                'analyst_rating': info.get('recommendationMean', None),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return fundamentals
            
        except Exception as e:
            self.handle_error(e, f"YahooFinance.get_fundamentals({ticker})")
            return {'ticker': ticker, 'error': str(e)}
    
    def get_options_data(self, ticker: str, expiration_date: Optional[str] = None) -> Dict[str, Any]:
        """
        获取期权数据（附加功能）
        
        参数:
            ticker: 股票代码
            expiration_date: 到期日 (可选)
            
        返回:
            包含期权数据的字典
        """
        try:
            ticker = self.validate_ticker(ticker)
            stock = yf.Ticker(ticker)
            
            # 获取可用的到期日
            expirations = stock.options
            
            if not expirations:
                return {'ticker': ticker, 'options': [], 'expirations': []}
            
            # 如果未指定到期日，使用第一个可用的
            if expiration_date is None:
                expiration_date = expirations[0]
            elif expiration_date not in expirations:
                return {'ticker': ticker, 'error': f"Invalid expiration date. Available dates: {expirations}"}
            
            # 获取期权链
            options = stock.option_chain(expiration_date)
            
            # 转换为字典
            calls = options.calls.to_dict('records')
            puts = options.puts.to_dict('records')
            
            return {
                'ticker': ticker,
                'expiration_date': expiration_date,
                'available_expirations': expirations,
                'calls': calls,
                'puts': puts
            }
            
        except Exception as e:
            self.handle_error(e, f"YahooFinance.get_options_data({ticker})")
            return {'ticker': ticker, 'error': str(e)}
    
    def get_historical_dividends(self, ticker: str, start_date: Union[str, datetime], 
                               end_date: Union[str, datetime]) -> List[Dict[str, Any]]:
        """
        获取历史分红数据
        
        参数:
            ticker: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            
        返回:
            包含分红数据的字典列表
        """
        try:
            ticker = self.validate_ticker(ticker)
            start = self.format_date(start_date)
            end = self.format_date(end_date)
            
            stock = yf.Ticker(ticker)
            dividends = stock.dividends
            
            # 过滤日期范围
            if not dividends.empty:
                dividends = dividends[(dividends.index >= start) & (dividends.index <= end)]
            
            result = []
            for date, amount in dividends.items():
                if isinstance(date, pd.Timestamp):
                    date_str = date.strftime('%Y-%m-%d')
                else:
                    date_str = pd.to_datetime(date).strftime('%Y-%m-%d')
                
                result.append({
                    'date': date_str,
                    'amount': float(amount)
                })
            
            return result
            
        except Exception as e:
            self.handle_error(e, f"YahooFinance.get_historical_dividends({ticker})")
            return []