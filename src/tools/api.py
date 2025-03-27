"""
工具API模块

提供各种数据获取和处理工具函数
"""
import os
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from data.data_service import data_service
from data.models import prices_to_df as convert_prices_to_df


class FinancialLineItem:
    """财务项目类"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class FinancialMetrics:
    """财务指标类"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


def get_financial_metrics(ticker: str, end_date: Optional[str] = None, period: str = "annual", limit: int = 5) -> List[FinancialMetrics]:
    """
    获取财务指标数据
    
    参数:
        ticker: 股票代码
        end_date: 截止日期 (YYYY-MM-DD)，默认为最新日期
        period: 数据周期 ('annual'=年度, 'quarterly'=季度, 'ttm'=过去12个月)
        limit: 返回的数据点数量限制
        
    返回:
        财务指标数据对象列表
    """
    # 获取基本面数据
    fundamentals = get_fundamentals(ticker)
    
    # 创建一个包含基本财务指标的列表
    # 在实际应用中，这里应该从数据源获取历史财务数据
    # 目前我们返回一个简化的数据结构
    metrics = []
    
    # 添加当前财务指标作为第一个数据点
    current_metrics = {
        "date": end_date or datetime.now().strftime('%Y-%m-%d'),
        "pe_ratio": fundamentals.get("pe_ratio"),
        "price_to_book": fundamentals.get("price_to_book"),
        "debt_to_equity": fundamentals.get("debt_to_equity"),
        "return_on_equity": fundamentals.get("return_on_equity"),
        "profit_margins": fundamentals.get("profit_margins"),
        "revenue_growth": fundamentals.get("revenue_growth"),
        "current_ratio": fundamentals.get("current_ratio"),
        "quick_ratio": fundamentals.get("quick_ratio"),
        "earnings_growth": 0.05  # 添加默认的收益增长率
    }
    # 将字典转换为对象
    metrics.append(FinancialMetrics(**current_metrics))
    
    # 为了演示，我们生成一些模拟的历史数据
    # 在实际应用中，这些数据应该从数据源获取
    for i in range(1, limit):
        # 计算历史日期（简化处理）
        year_offset = i if period == "annual" else i // 4
        quarter_offset = 0 if period == "annual" else i % 4
        
        if end_date:
            hist_date = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            hist_date = datetime.now()
            
        if period == "annual":
            hist_date = hist_date.replace(year=hist_date.year - year_offset)
        else:
            hist_date = hist_date.replace(year=hist_date.year - year_offset,
                                         month=max(1, hist_date.month - 3 * quarter_offset))
        
        hist_date_str = hist_date.strftime('%Y-%m-%d')
        
        # 创建一些模拟的历史数据（略有变化）
        # 在实际应用中，这些应该是真实的历史数据
        hist_metrics = {
            "date": hist_date_str,
            "pe_ratio": fundamentals.get("pe_ratio", 15) * (0.9 + 0.2 * (i / limit)),
            "price_to_book": fundamentals.get("price_to_book", 3) * (0.9 + 0.2 * (i / limit)),
            "debt_to_equity": fundamentals.get("debt_to_equity", 1.2) * (0.9 + 0.2 * (i / limit)),
            "return_on_equity": fundamentals.get("return_on_equity", 0.15) * (0.9 + 0.2 * (i / limit)),
            "profit_margins": fundamentals.get("profit_margins", 0.1) * (0.9 + 0.2 * (i / limit)),
            "revenue_growth": fundamentals.get("revenue_growth", 0.05) * (0.9 + 0.2 * (i / limit)),
            "current_ratio": fundamentals.get("current_ratio", 1.5) * (0.9 + 0.2 * (i / limit)),
            "quick_ratio": fundamentals.get("quick_ratio", 1.2) * (0.9 + 0.2 * (i / limit)),
            "earnings_growth": 0.05 * (0.9 + 0.2 * (i / limit))  # 添加默认的收益增长率
        }
        # 将字典转换为对象
        metrics.append(FinancialMetrics(**hist_metrics))
    
    return metrics

def search_line_items(ticker: str, line_items: List[str], end_date: Optional[str] = None,
                     period: str = "annual", limit: int = 5) -> List[FinancialLineItem]:
    """
    搜索特定的财务项目
    
    参数:
        ticker: 股票代码
        line_items: 要搜索的财务项目列表
        end_date: 截止日期 (YYYY-MM-DD)，默认为最新日期
        period: 数据周期 ('annual'=年度, 'quarterly'=季度, 'ttm'=过去12个月)
        limit: 返回的数据点数量限制
        
    返回:
        包含请求的财务项目的数据对象列表
    """
    # 获取基本面数据
    fundamentals = get_fundamentals(ticker)
    
    # 创建一个包含请求的财务项目的列表
    result_items = []
    
    # 添加当前财务项目作为第一个数据点
    current_items = {
        "date": end_date or datetime.now().strftime('%Y-%m-%d')
    }
    
    # 从基本面数据中提取请求的项目
    for item in line_items:
        current_items[item] = fundamentals.get(item)
    
    # 将字典转换为对象
    result_items.append(FinancialLineItem(**current_items))
    
    # 为了演示，我们生成一些模拟的历史数据
    # 在实际应用中，这些数据应该从数据源获取
    for i in range(1, limit):
        # 计算历史日期（简化处理）
        year_offset = i if period == "annual" else i // 4
        quarter_offset = 0 if period == "annual" else i % 4
        
        if end_date:
            hist_date = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            hist_date = datetime.now()
            
        if period == "annual":
            hist_date = hist_date.replace(year=hist_date.year - year_offset)
        else:
            hist_date = hist_date.replace(year=hist_date.year - year_offset,
                                         month=max(1, hist_date.month - 3 * quarter_offset))
        
        hist_date_str = hist_date.strftime('%Y-%m-%d')
        
        # 创建一些模拟的历史数据（略有变化）
        hist_items = {
            "date": hist_date_str
        }
        
        # 为每个请求的项目生成模拟数据
        for item in line_items:
            base_value = fundamentals.get(item, 0)
            if isinstance(base_value, (int, float)) and base_value != 0:
                # 为数值类型生成略有变化的历史值
                hist_items[item] = base_value * (0.9 + 0.2 * (i / limit))
            else:
                # 对于非数值或零值，保持不变
                hist_items[item] = base_value
        
        # 将字典转换为对象
        result_items.append(FinancialLineItem(**hist_items))
    
    return result_items


def get_prices(ticker: str, start_date: str, end_date: str, interval: str = '1d') -> List[Dict[str, Any]]:
    """
    获取历史价格数据
    
    参数:
        ticker: 股票代码
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        interval: 数据间隔 ('1d'=日, '1wk'=周, '1mo'=月)
        
    返回:
        价格数据列表
    """
    return data_service.get_prices(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        interval=interval
    )


def get_fundamentals(ticker: str) -> Dict[str, Any]:
    """
    获取基本面数据
    
    参数:
        ticker: 股票代码
        
    返回:
        基本面数据字典
    """
    return data_service.get_fundamentals(ticker=ticker)


def get_market_cap(ticker: str, date: Optional[str] = None) -> Optional[float]:
    """
    获取特定日期的市值
    
    参数:
        ticker: 股票代码
        date: 日期 (YYYY-MM-DD)，默认为最新日期
        
    返回:
        市值（如果可用）
    """
    fundamentals = get_fundamentals(ticker)
    return fundamentals.get('market_cap')


def get_pe_ratio(ticker: str) -> Optional[float]:
    """
    获取市盈率
    
    参数:
        ticker: 股票代码
        
    返回:
        市盈率（如果可用）
    """
    fundamentals = get_fundamentals(ticker)
    return fundamentals.get('pe_ratio')


def prices_to_df(prices: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    将价格数据转换为pandas DataFrame
    
    参数:
        prices: 价格数据列表
        
    返回:
        pandas DataFrame
    """
    return convert_prices_to_df(prices)


def get_price_data(ticker: str, start_date: str, end_date: str, interval: str = '1d') -> pd.DataFrame:
    """
    获取价格数据并转换为DataFrame
    
    参数:
        ticker: 股票代码
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        interval: 数据间隔
        
    返回:
        pandas DataFrame
    """
    return data_service.get_prices_df(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        interval=interval
    )


def calculate_returns(price_df: pd.DataFrame, period: str = 'daily') -> pd.DataFrame:
    """
    计算收益率
    
    参数:
        price_df: 价格DataFrame
        period: 收益率周期 ('daily', 'weekly', 'monthly')
        
    返回:
        包含收益率的DataFrame
    """
    # 确保索引已排序
    price_df = price_df.sort_index()
    
    # 计算收益率
    if period == 'daily':
        returns = price_df['close'].pct_change()
    elif period == 'weekly':
        returns = price_df['close'].resample('W').last().pct_change()
    elif period == 'monthly':
        returns = price_df['close'].resample('M').last().pct_change()
    else:
        raise ValueError(f"Unsupported period: {period}")
    
    return returns


def calculate_volatility(price_df: pd.DataFrame, window: int = 20, annualize: bool = True) -> pd.Series:
    """
    计算波动率
    
    参数:
        price_df: 价格DataFrame
        window: 滚动窗口大小
        annualize: 是否年化
        
    返回:
        波动率Series
    """
    # 计算日收益率
    returns = price_df['close'].pct_change().dropna()
    
    # 计算滚动标准差
    volatility = returns.rolling(window=window).std()
    
    # 年化（假设252个交易日）
    if annualize:
        volatility = volatility * (252 ** 0.5)
    
    return volatility


def get_historical_data(tickers: List[str], start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
    """
    获取多个股票的历史数据
    
    参数:
        tickers: 股票代码列表
        start_date: 开始日期
        end_date: 结束日期
        
    返回:
        股票代码到DataFrame的映射
    """
    result = {}
    for ticker in tickers:
        try:
            df = get_price_data(ticker, start_date, end_date)
            if not df.empty:
                result[ticker] = df
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
    
    return result


def get_available_data_sources() -> List[str]:
    """
    获取可用的数据源列表
    
    返回:
        数据源名称列表
    """
    return data_service.get_available_sources()


def clear_data_cache(ticker: Optional[str] = None) -> int:
    """
    清除数据缓存
    
    参数:
        ticker: 股票代码（如果指定，只清除该股票的缓存）
        
    返回:
        清除的缓存条目数量
    """
    return data_service.clear_cache(ticker)


class InsiderTrade:
    """内部交易数据类"""
    def __init__(self, date, insider_name, title, transaction_type, transaction_shares, transaction_price):
        self.date = date
        self.insider_name = insider_name
        self.title = title
        self.transaction_type = transaction_type
        self.transaction_shares = transaction_shares
        self.transaction_price = transaction_price


class NewsItem:
    """新闻项目类"""
    def __init__(self, date, title, summary, source, url, sentiment):
        self.date = date
        self.title = title
        self.summary = summary
        self.source = source
        self.url = url
        self.sentiment = sentiment


def get_insider_trades(ticker: str, end_date: Optional[str] = None, start_date: Optional[str] = None, limit: int = 100) -> List[InsiderTrade]:
    """
    获取内部交易数据
    
    参数:
        ticker: 股票代码
        end_date: 截止日期 (YYYY-MM-DD)，默认为最新日期
        limit: 返回的数据点数量限制
        
    返回:
        内部交易数据列表
    """
    # 在实际应用中，这些数据应该从数据源获取
    # 这里我们生成一些模拟数据用于演示
    
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    
    # 模拟数据
    insider_names = ["John Smith", "Jane Doe", "Robert Johnson", "Emily Williams", "Michael Brown"]
    titles = ["CEO", "CFO", "CTO", "Director", "VP of Sales"]
    transaction_types = ["Buy", "Sell"]
    
    trades = []
    for i in range(limit):
        # 生成随机日期（在过去一年内）
        days_ago = np.random.randint(1, 365)
        trade_date = (end_date_obj - pd.Timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        # 随机选择内部人士和职位
        insider_idx = np.random.randint(0, len(insider_names))
        insider_name = insider_names[insider_idx]
        title = titles[insider_idx % len(titles)]
        
        # 随机选择交易类型
        transaction_type = transaction_types[np.random.randint(0, len(transaction_types))]
        
        # 生成交易股数和价格
        # 如果是卖出，交易股数为负数
        transaction_shares = np.random.randint(100, 10000)
        if transaction_type == "Sell":
            transaction_shares = -transaction_shares
            
        # 生成随机价格（假设在50-200之间）
        transaction_price = np.random.uniform(50, 200)
        
        # 创建内部交易对象
        trade = InsiderTrade(
            date=trade_date,
            insider_name=insider_name,
            title=title,
            transaction_type=transaction_type,
            transaction_shares=transaction_shares,
            transaction_price=transaction_price
        )
        
        trades.append(trade)
    
    # 按日期排序
    trades.sort(key=lambda x: x.date, reverse=True)
    
    # 如果有开始日期，过滤掉早于开始日期的交易
    if start_date:
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        trades = [trade for trade in trades
                 if datetime.strptime(trade.date, '%Y-%m-%d') >= start_date_obj]
    
    return trades


def get_company_news(ticker: str, end_date: Optional[str] = None, limit: int = 100) -> List[NewsItem]:
    """
    获取公司新闻
    
    参数:
        ticker: 股票代码
        end_date: 截止日期 (YYYY-MM-DD)，默认为最新日期
        limit: 返回的数据点数量限制
        
    返回:
        新闻项目列表
    """
    # 在实际应用中，这些数据应该从数据源获取
    # 这里我们生成一些模拟数据用于演示
    
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    
    # 模拟数据
    news_titles = [
        f"{ticker} Reports Strong Quarterly Earnings",
        f"{ticker} Announces New Product Line",
        f"{ticker} Expands into International Markets",
        f"{ticker} Faces Regulatory Challenges",
        f"{ticker} Stock Downgraded by Analysts",
        f"{ticker} CEO Resigns",
        f"{ticker} Acquires Startup for $100M",
        f"{ticker} Beats Revenue Expectations",
        f"{ticker} Misses Earnings Estimates",
        f"{ticker} Announces Stock Buyback Program"
    ]
    
    news_summaries = [
        f"{ticker} reported quarterly earnings that exceeded analyst expectations, driven by strong product sales.",
        f"{ticker} unveiled a new product line that aims to capture market share in the growing tech sector.",
        f"{ticker} announced plans to expand operations into European and Asian markets over the next year.",
        f"{ticker} is facing scrutiny from regulators over its business practices, which could impact future growth.",
        f"Several analysts have downgraded {ticker} stock citing concerns about valuation and competition.",
        f"The CEO of {ticker} has resigned, effective immediately. The board has initiated a search for a replacement.",
        f"{ticker} has acquired a promising startup to strengthen its position in the AI market.",
        f"{ticker} reported revenue that exceeded Wall Street expectations, sending the stock higher.",
        f"{ticker} reported earnings below analyst estimates, citing supply chain challenges.",
        f"{ticker} announced a $500 million stock buyback program, signaling confidence in its future prospects."
    ]
    
    news_sources = ["Bloomberg", "Reuters", "CNBC", "Wall Street Journal", "Financial Times"]
    sentiments = ["positive", "negative", "neutral"]
    sentiment_weights = [0.5, 0.3, 0.2]  # 权重，使正面新闻略多于负面新闻
    
    news_items = []
    for i in range(limit):
        # 生成随机日期（在过去一年内）
        days_ago = np.random.randint(1, 365)
        news_date = (end_date_obj - pd.Timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        # 随机选择新闻标题和摘要
        news_idx = np.random.randint(0, len(news_titles))
        title = news_titles[news_idx]
        summary = news_summaries[news_idx]
        
        # 随机选择新闻来源
        source = news_sources[np.random.randint(0, len(news_sources))]
        
        # 生成URL
        url = f"https://example.com/news/{ticker.lower()}/{news_date.replace('-', '')}-{news_idx}"
        
        # 根据新闻标题和摘要确定情感
        # 在实际应用中，这应该使用NLP模型进行分析
        if "strong" in title.lower() or "beats" in title.lower() or "exceeds" in title.lower():
            sentiment = "positive"
        elif "misses" in title.lower() or "downgraded" in title.lower() or "resigns" in title.lower() or "challenges" in title.lower():
            sentiment = "negative"
        else:
            # 随机选择情感，但使用权重使正面新闻略多
            sentiment = np.random.choice(sentiments, p=sentiment_weights)
        
        # 创建新闻项目对象
        news_item = NewsItem(
            date=news_date,
            title=title,
            summary=summary,
            source=source,
            url=url,
            sentiment=sentiment
        )
        
        news_items.append(news_item)
    
    # 按日期排序
    news_items.sort(key=lambda x: x.date, reverse=True)
    
    return news_items
