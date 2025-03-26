"""
数据模型

定义统一的数据结构，用于在系统中表示金融数据
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class PriceData(BaseModel):
    """价格数据模型"""
    date: str = Field(..., description="交易日期 (YYYY-MM-DD)")
    open: float = Field(..., description="开盘价")
    high: float = Field(..., description="最高价")
    low: float = Field(..., description="最低价")
    close: float = Field(..., description="收盘价")
    volume: int = Field(..., description="成交量")
    adjusted_close: Optional[float] = Field(None, description="调整后收盘价")
    
    class Config:
        schema_extra = {
            "example": {
                "date": "2025-03-25",
                "open": 150.25,
                "high": 152.75,
                "low": 149.50,
                "close": 151.80,
                "volume": 5432100,
                "adjusted_close": 151.80
            }
        }


class FundamentalData(BaseModel):
    """基本面数据模型"""
    ticker: str = Field(..., description="股票代码")
    name: Optional[str] = Field(None, description="公司名称")
    sector: Optional[str] = Field(None, description="行业部门")
    industry: Optional[str] = Field(None, description="具体行业")
    market_cap: Optional[float] = Field(None, description="市值")
    pe_ratio: Optional[float] = Field(None, description="市盈率")
    forward_pe: Optional[float] = Field(None, description="预期市盈率")
    dividend_yield: Optional[float] = Field(None, description="股息收益率")
    beta: Optional[float] = Field(None, description="贝塔系数")
    eps: Optional[float] = Field(None, description="每股收益")
    price_to_book: Optional[float] = Field(None, description="市净率")
    debt_to_equity: Optional[float] = Field(None, description="债务权益比")
    return_on_equity: Optional[float] = Field(None, description="股本回报率")
    profit_margins: Optional[float] = Field(None, description="利润率")
    revenue_growth: Optional[float] = Field(None, description="收入增长率")
    current_ratio: Optional[float] = Field(None, description="流动比率")
    quick_ratio: Optional[float] = Field(None, description="速动比率")
    target_price: Optional[float] = Field(None, description="分析师目标价")
    analyst_rating: Optional[float] = Field(None, description="分析师评级")
    last_updated: str = Field(..., description="数据更新时间")
    
    class Config:
        schema_extra = {
            "example": {
                "ticker": "AAPL",
                "name": "Apple Inc.",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "market_cap": 2500000000000,
                "pe_ratio": 28.5,
                "dividend_yield": 0.005,
                "beta": 1.2,
                "last_updated": "2025-03-25 12:30:45"
            }
        }


class OptionData(BaseModel):
    """期权数据模型"""
    ticker: str = Field(..., description="标的股票代码")
    expiration_date: str = Field(..., description="到期日期")
    strike: float = Field(..., description="行权价")
    option_type: str = Field(..., description="期权类型 (call/put)")
    last_price: float = Field(..., description="最新价格")
    bid: float = Field(..., description="买入价")
    ask: float = Field(..., description="卖出价")
    volume: int = Field(..., description="成交量")
    open_interest: int = Field(..., description="未平仓合约数")
    implied_volatility: float = Field(..., description="隐含波动率")
    
    class Config:
        schema_extra = {
            "example": {
                "ticker": "AAPL",
                "expiration_date": "2025-06-20",
                "strike": 160.0,
                "option_type": "call",
                "last_price": 5.65,
                "bid": 5.60,
                "ask": 5.70,
                "volume": 1250,
                "open_interest": 8500,
                "implied_volatility": 0.28
            }
        }


class DividendData(BaseModel):
    """分红数据模型"""
    date: str = Field(..., description="分红日期")
    amount: float = Field(..., description="分红金额")
    
    class Config:
        schema_extra = {
            "example": {
                "date": "2025-02-15",
                "amount": 0.25
            }
        }


class PortfolioPosition(BaseModel):
    """投资组合持仓模型"""
    ticker: str = Field(..., description="股票代码")
    quantity: int = Field(..., description="持有数量")
    cost_basis: float = Field(..., description="成本基础")
    current_price: float = Field(..., description="当前价格")
    market_value: float = Field(..., description="市场价值")
    unrealized_gain: float = Field(..., description="未实现收益")
    weight: float = Field(..., description="投资组合权重")
    
    class Config:
        schema_extra = {
            "example": {
                "ticker": "AAPL",
                "quantity": 100,
                "cost_basis": 145.75,
                "current_price": 151.80,
                "market_value": 15180.0,
                "unrealized_gain": 605.0,
                "weight": 0.15
            }
        }


class Portfolio(BaseModel):
    """投资组合模型"""
    cash: float = Field(..., description="现金持有量")
    positions: Dict[str, PortfolioPosition] = Field(..., description="持仓情况")
    total_value: float = Field(..., description="总价值")
    realized_gains: float = Field(..., description="已实现收益")
    unrealized_gains: float = Field(..., description="未实现收益")
    
    class Config:
        schema_extra = {
            "example": {
                "cash": 25000.0,
                "positions": {
                    "AAPL": {
                        "ticker": "AAPL",
                        "quantity": 100,
                        "cost_basis": 145.75,
                        "current_price": 151.80,
                        "market_value": 15180.0,
                        "unrealized_gain": 605.0,
                        "weight": 0.15
                    }
                },
                "total_value": 100000.0,
                "realized_gains": 1200.0,
                "unrealized_gains": 3500.0
            }
        }


class RiskMetrics(BaseModel):
    """风险指标模型"""
    var_95: float = Field(..., description="95%置信度VaR")
    var_99: float = Field(..., description="99%置信度VaR")
    cvar_95: float = Field(..., description="95%置信度CVaR")
    volatility: float = Field(..., description="年化波动率")
    beta: float = Field(..., description="贝塔系数")
    sharpe_ratio: float = Field(..., description="夏普比率")
    max_drawdown: float = Field(..., description="最大回撤")
    
    class Config:
        schema_extra = {
            "example": {
                "var_95": 2500.0,
                "var_99": 3800.0,
                "cvar_95": 3200.0,
                "volatility": 0.18,
                "beta": 1.1,
                "sharpe_ratio": 1.5,
                "max_drawdown": 0.12
            }
        }


# 辅助函数
def convert_to_price_data(data_list: List[Dict[str, Any]]) -> List[PriceData]:
    """
    将原始价格数据转换为PriceData对象列表
    
    参数:
        data_list: 原始价格数据列表
        
    返回:
        PriceData对象列表
    """
    return [PriceData(**item) for item in data_list]


def prices_to_df(prices: List[Dict[str, Any]]) -> 'pd.DataFrame':
    """
    将价格数据转换为pandas DataFrame
    
    参数:
        prices: 价格数据列表
        
    返回:
        pandas DataFrame
    """
    import pandas as pd
    
    if not prices:
        return pd.DataFrame()
    
    df = pd.DataFrame(prices)
    
    # 将日期列转换为datetime类型并设为索引
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    
    return df
