"""
数据服务协调器

协调不同数据源和缓存系统，提供统一的数据访问接口
"""
import os
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import logging
from dotenv import load_dotenv

from .api.yahoo import YahooFinanceAdapter
from .api.sample import SampleDataAdapter
from .cache import data_cache
from .models import PriceData, FundamentalData, convert_to_price_data, prices_to_df

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('data_service')


class DataService:
    """
    数据服务协调器
    
    管理多个数据源适配器，提供统一的数据访问接口
    """
    
    def __init__(self):
        """初始化数据服务"""
        # 初始化数据源适配器
        self.sources = ['yahoo', 'sample']
        # 环境变量配置
        self.default_source = os.getenv('DEFAULT_DATA_SOURCE', 'sample')
        # 专业版API配置
        if os.getenv('YAHOO_API_KEY'):
            self.sources.append('yahoo_pro')
        
        # 初始化数据源适配器
        self.adapters = {
            'yahoo': YahooFinanceAdapter(),
            'sample': SampleDataAdapter()  # 添加示例数据适配器
        }
        
        # 如果有Alpha Vantage API密钥，添加Alpha Vantage适配器
        alpha_key = os.getenv('ALPHA_VANTAGE_KEY')
        if alpha_key:
            try:
                # 动态导入，避免在没有密钥时出错
                from .api.alpha import AlphaVantageAdapter
                self.adapters['alpha'] = AlphaVantageAdapter(api_key=alpha_key)
            except ImportError:
                logger.warning("AlphaVantageAdapter not available. Skipping.")
        
        logger.info(f"DataService initialized with sources: {list(self.adapters.keys())}")
    
    def get_prices(self, ticker: str, start_date: Union[str, datetime], 
                  end_date: Union[str, datetime], source: Optional[str] = None,
                  interval: str = '1d', use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        获取历史价格数据
        
        参数:
            ticker: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            source: 数据源名称（默认使用配置的默认源）
            interval: 数据间隔
            use_cache: 是否使用缓存
            
        返回:
            价格数据列表
        """
        # 格式化日期
        if isinstance(start_date, datetime):
            start_date = start_date.strftime('%Y-%m-%d')
        if isinstance(end_date, datetime):
            end_date = end_date.strftime('%Y-%m-%d')
        
        # 使用指定的数据源或默认源
        source = source or self.default_source
        
        # 检查数据源是否可用
        if source not in self.adapters:
            available_sources = list(self.adapters.keys())
            logger.error(f"Data source '{source}' not available. Available sources: {available_sources}")
            if not available_sources:
                return []
            source = available_sources[0]
            logger.info(f"Falling back to '{source}' data source")
        
        # 尝试从缓存获取数据
        if use_cache:
            cached_data = data_cache.get_prices(
                source=source,
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                interval=interval
            )
            if cached_data:
                logger.debug(f"Cache hit for {ticker} prices from {source}")
                return cached_data
        
        # 从数据源获取数据
        logger.info(f"Fetching {ticker} prices from {source} ({start_date} to {end_date})")
        adapter = self.adapters[source]
        data = adapter.get_prices(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )
        
        # 缓存数据
        if use_cache and data:
            data_cache.set_prices(
                source=source,
                ticker=ticker,
                start_date=start_date,
                end_date=end_date,
                data=data,
                interval=interval
            )
        
        return data
    
    def get_fundamentals(self, ticker: str, source: Optional[str] = None,
                        use_cache: bool = True) -> Dict[str, Any]:
        """
        获取基本面数据
        
        参数:
            ticker: 股票代码
            source: 数据源名称（默认使用配置的默认源）
            use_cache: 是否使用缓存
            
        返回:
            基本面数据字典
        """
        # 使用指定的数据源或默认源
        source = source or self.default_source
        
        # 检查数据源是否可用
        if source not in self.adapters:
            available_sources = list(self.adapters.keys())
            logger.error(f"Data source '{source}' not available. Available sources: {available_sources}")
            if not available_sources:
                return {'ticker': ticker, 'error': 'No data source available'}
            source = available_sources[0]
            logger.info(f"Falling back to '{source}' data source")
        
        # 尝试从缓存获取数据
        if use_cache:
            cached_data = data_cache.get_fundamentals(
                source=source,
                ticker=ticker
            )
            if cached_data:
                logger.debug(f"Cache hit for {ticker} fundamentals from {source}")
                return cached_data
        
        # 从数据源获取数据
        logger.info(f"Fetching {ticker} fundamentals from {source}")
        adapter = self.adapters[source]
        data = adapter.get_fundamentals(ticker=ticker)
        
        # 缓存数据
        if use_cache and data:
            data_cache.set_fundamentals(
                source=source,
                ticker=ticker,
                data=data
            )
        
        return data
    
    def get_options_data(self, ticker: str, expiration_date: Optional[str] = None,
                        source: Optional[str] = None, use_cache: bool = True) -> Dict[str, Any]:
        """
        获取期权数据
        
        参数:
            ticker: 股票代码
            expiration_date: 到期日
            source: 数据源名称（默认使用配置的默认源）
            use_cache: 是否使用缓存
            
        返回:
            期权数据字典
        """
        # 使用指定的数据源或默认源
        source = source or self.default_source
        
        # 检查数据源是否可用
        if source not in self.adapters:
            available_sources = list(self.adapters.keys())
            logger.error(f"Data source '{source}' not available. Available sources: {available_sources}")
            if not available_sources:
                return {'ticker': ticker, 'error': 'No data source available'}
            source = available_sources[0]
            logger.info(f"Falling back to '{source}' data source")
        
        # 检查适配器是否支持期权数据
        adapter = self.adapters[source]
        if not hasattr(adapter, 'get_options_data'):
            logger.error(f"Data source '{source}' does not support options data")
            return {'ticker': ticker, 'error': 'Options data not supported by this data source'}
        
        # 尝试从缓存获取数据
        if use_cache:
            cached_data = data_cache.get_options_data(
                source=source,
                ticker=ticker,
                expiration_date=expiration_date
            )
            if cached_data:
                logger.debug(f"Cache hit for {ticker} options from {source}")
                return cached_data
        
        # 从数据源获取数据
        logger.info(f"Fetching {ticker} options from {source}")
        data = adapter.get_options_data(
            ticker=ticker,
            expiration_date=expiration_date
        )
        
        # 缓存数据
        if use_cache and data:
            data_cache.set_options_data(
                source=source,
                ticker=ticker,
                data=data,
                expiration_date=expiration_date
            )
        
        return data
    
    def get_prices_df(self, ticker: str, start_date: Union[str, datetime], 
                     end_date: Union[str, datetime], source: Optional[str] = None,
                     interval: str = '1d', use_cache: bool = True):
        """
        获取价格数据并转换为pandas DataFrame
        
        参数:
            ticker: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            source: 数据源名称
            interval: 数据间隔
            use_cache: 是否使用缓存
            
        返回:
            pandas DataFrame
        """
        prices = self.get_prices(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            source=source,
            interval=interval,
            use_cache=use_cache
        )
        
        return prices_to_df(prices)
    
    def clear_cache(self, ticker: Optional[str] = None) -> int:
        """
        清除缓存
        
        参数:
            ticker: 股票代码（如果指定，只清除该股票的缓存）
            
        返回:
            清除的缓存条目数量
        """
        if ticker:
            return data_cache.clear_ticker_cache(ticker)
        else:
            return data_cache.clear_expired()
    
    def get_available_sources(self) -> List[str]:
        """
        获取可用的数据源列表
        
        返回:
            数据源名称列表
        """
        return list(self.adapters.keys())
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        返回:
            缓存统计信息字典
        """
        return data_cache.get_cache_stats()


# 创建全局数据服务实例
data_service = DataService()