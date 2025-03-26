"""
基础数据源适配器

提供所有数据源适配器的基类和通用接口
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Any, Optional, Union


class BaseAdapter(ABC):
    """
    数据源适配器基类
    
    所有特定数据源适配器必须继承此类并实现其抽象方法
    """
    
    @abstractmethod
    def get_prices(self, ticker: str, start_date: Union[str, datetime], 
                  end_date: Union[str, datetime], interval: str = '1d') -> List[Dict[str, Any]]:
        """
        获取历史价格数据
        
        参数:
            ticker: 股票代码
            start_date: 开始日期 (YYYY-MM-DD格式的字符串或datetime对象)
            end_date: 结束日期 (YYYY-MM-DD格式的字符串或datetime对象)
            interval: 数据间隔 ('1d'=日, '1h'=小时, '1m'=分钟)
            
        返回:
            包含价格数据的字典列表
        """
        pass
    
    @abstractmethod
    def get_fundamentals(self, ticker: str) -> Dict[str, Any]:
        """
        获取基本面数据
        
        参数:
            ticker: 股票代码
            
        返回:
            包含基本面数据的字典
        """
        pass
    
    def format_date(self, date: Union[str, datetime]) -> str:
        """
        将日期格式化为标准字符串格式
        
        参数:
            date: 日期字符串或datetime对象
            
        返回:
            YYYY-MM-DD格式的日期字符串
        """
        if isinstance(date, datetime):
            return date.strftime('%Y-%m-%d')
        return date
    
    def validate_ticker(self, ticker: str) -> str:
        """
        验证并格式化股票代码
        
        参数:
            ticker: 原始股票代码
            
        返回:
            格式化后的股票代码
        """
        return ticker.strip().upper()
    
    def handle_error(self, error: Exception, context: str) -> None:
        """
        处理API错误
        
        参数:
            error: 捕获的异常
            context: 错误上下文描述
        """
        # 默认实现只是记录错误
        print(f"Error in {context}: {str(error)}")
        # 在实际实现中，这里应该使用适当的日志记录