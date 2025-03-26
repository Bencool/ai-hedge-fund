"""
数据源适配器包

包含各种数据源的适配器实现
"""
from .base import BaseAdapter
from .yahoo import YahooFinanceAdapter
from .sample import SampleDataAdapter

__all__ = ['BaseAdapter', 'YahooFinanceAdapter', 'SampleDataAdapter']