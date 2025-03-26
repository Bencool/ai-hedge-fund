"""
数据缓存系统

提供高效的数据缓存机制，减少对外部API的请求
"""
import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union
import diskcache
from pathlib import Path
from .models import PriceData, FundamentalData


class DataCache:
    """
    数据缓存管理器
    
    提供缓存机制，减少对外部API的请求频率
    """
    
    def __init__(self, cache_dir: str = './.datacache', expire_hours: int = 6):
        """
        初始化缓存管理器
        
        参数:
            cache_dir: 缓存目录
            expire_hours: 缓存过期时间（小时）
        """
        # 确保缓存目录存在
        os.makedirs(cache_dir, exist_ok=True)
        
        # 初始化磁盘缓存
        self.cache = diskcache.Cache(cache_dir)
        self.expire_time = timedelta(hours=expire_hours)
    
    def _generate_key(self, source: str, data_type: str, **params) -> str:
        """
        生成缓存键
        
        参数:
            source: 数据源名称
            data_type: 数据类型
            **params: 其他参数
            
        返回:
            缓存键
        """
        # 创建一个包含所有参数的字典
        key_dict = {
            'source': source,
            'type': data_type,
            **params
        }
        
        # 将字典转换为JSON字符串
        key_str = json.dumps(key_dict, sort_keys=True)
        
        # 使用MD5生成哈希值作为键
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get_prices(self, source: str, ticker: str, start_date: str, 
                  end_date: str, interval: str = '1d') -> Optional[List[Dict[str, Any]]]:
        """
        获取缓存的价格数据
        
        参数:
            source: 数据源名称
            ticker: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            interval: 数据间隔
            
        返回:
            价格数据列表，如果缓存未命中则返回None
        """
        key = self._generate_key(
            source=source,
            data_type='prices',
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )
        
        return self.cache.get(key)
    
    def set_prices(self, source: str, ticker: str, start_date: str, 
                  end_date: str, data: List[Dict[str, Any]], 
                  interval: str = '1d') -> None:
        """
        缓存价格数据
        
        参数:
            source: 数据源名称
            ticker: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            data: 价格数据列表
            interval: 数据间隔
        """
        key = self._generate_key(
            source=source,
            data_type='prices',
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            interval=interval
        )
        
        # 设置缓存，带过期时间
        self.cache.set(key, data, expire=self.expire_time.total_seconds())
    
    def get_fundamentals(self, source: str, ticker: str) -> Optional[Dict[str, Any]]:
        """
        获取缓存的基本面数据
        
        参数:
            source: 数据源名称
            ticker: 股票代码
            
        返回:
            基本面数据字典，如果缓存未命中则返回None
        """
        key = self._generate_key(
            source=source,
            data_type='fundamentals',
            ticker=ticker
        )
        
        return self.cache.get(key)
    
    def set_fundamentals(self, source: str, ticker: str, data: Dict[str, Any]) -> None:
        """
        缓存基本面数据
        
        参数:
            source: 数据源名称
            ticker: 股票代码
            data: 基本面数据字典
        """
        key = self._generate_key(
            source=source,
            data_type='fundamentals',
            ticker=ticker
        )
        
        # 基本面数据缓存时间较短，因为它可能变化更频繁
        expire_time = timedelta(hours=2).total_seconds()
        self.cache.set(key, data, expire=expire_time)
    
    def get_options_data(self, source: str, ticker: str, 
                        expiration_date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        获取缓存的期权数据
        
        参数:
            source: 数据源名称
            ticker: 股票代码
            expiration_date: 到期日
            
        返回:
            期权数据字典，如果缓存未命中则返回None
        """
        key = self._generate_key(
            source=source,
            data_type='options',
            ticker=ticker,
            expiration_date=expiration_date
        )
        
        return self.cache.get(key)
    
    def set_options_data(self, source: str, ticker: str, data: Dict[str, Any],
                        expiration_date: Optional[str] = None) -> None:
        """
        缓存期权数据
        
        参数:
            source: 数据源名称
            ticker: 股票代码
            data: 期权数据字典
            expiration_date: 到期日
        """
        key = self._generate_key(
            source=source,
            data_type='options',
            ticker=ticker,
            expiration_date=expiration_date
        )
        
        # 期权数据变化较快，缓存时间较短
        expire_time = timedelta(hours=1).total_seconds()
        self.cache.set(key, data, expire=expire_time)
    
    def clear_ticker_cache(self, ticker: str) -> int:
        """
        清除特定股票的所有缓存
        
        参数:
            ticker: 股票代码
            
        返回:
            清除的缓存条目数量
        """
        count = 0
        for key in self.cache:
            key_str = str(key)
            if f'"ticker": "{ticker}"' in key_str:
                self.cache.delete(key)
                count += 1
        return count
    
    def clear_expired(self) -> int:
        """
        清除所有过期缓存
        
        返回:
            清除的缓存条目数量
        """
        return self.cache.expire()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息
        
        返回:
            包含缓存统计信息的字典
        """
        return {
            'size': len(self.cache),
            'volume': self.cache.volume(),
            'directory': self.cache.directory,
            'expire_time': self.expire_time.total_seconds() / 3600  # 转换为小时
        }
    
    def close(self) -> None:
        """关闭缓存，确保数据写入磁盘"""
        self.cache.close()


# 创建全局缓存实例
data_cache = DataCache()
