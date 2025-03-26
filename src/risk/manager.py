"""
风险管理器

提供风险监控、仓位调整和预警功能
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import logging

from .metrics import risk_calculator
from data.data_service import data_service
from data.models import Portfolio, PortfolioPosition

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('risk_manager')


class RiskManager:
    """
    风险管理器
    
    提供风险监控、仓位调整和预警功能
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化风险管理器
        
        参数:
            config: 风险管理配置
        """
        self.config = config or {}
        
        # 设置默认配置
        self.max_position_size = self.config.get('max_position_size', 0.2)  # 单一仓位最大比例
        self.max_sector_exposure = self.config.get('max_sector_exposure', 0.3)  # 单一行业最大暴露
        self.max_drawdown_limit = self.config.get('max_drawdown_limit', 0.2)  # 最大回撤限制
        self.var_limit = self.config.get('var_limit', 0.05)  # VaR限制（95%置信度）
        self.risk_free_rate = self.config.get('risk_free_rate', 0.02)  # 无风险利率
        
        # 风险状态
        self.risk_state = {
            'alerts': [],
            'position_limits': {},
            'portfolio_metrics': {},
            'circuit_breaker_active': False
        }
        
        # 初始化风险计算器
        self._init_risk_calculator()
    
    def _init_risk_calculator(self):
        """初始化风险计算器"""
        risk_calculator.risk_free_rate = self.risk_free_rate
    
    def analyze_portfolio(self, portfolio: Dict[str, Any], 
                        start_date: str, end_date: str) -> Dict[str, Any]:
        """
        分析投资组合风险
        
        参数:
            portfolio: 投资组合数据
            start_date: 分析开始日期
            end_date: 分析结束日期
            
        返回:
            风险分析结果
        """
        logger.info(f"Analyzing portfolio risk from {start_date} to {end_date}")
        
        # 提取投资组合信息
        positions = portfolio.get('positions', {})
        cash = portfolio.get('cash', 0)
        
        # 计算投资组合总价值
        total_value = cash
        for ticker, position in positions.items():
            # 计算多头和空头价值
            long_value = position.get('long', 0) * position.get('long_cost_basis', 0)
            short_value = position.get('short', 0) * position.get('short_cost_basis', 0)
            total_value += long_value - short_value
        
        # 获取每个资产的历史价格数据
        price_data = {}
        returns_data = {}
        for ticker in positions.keys():
            try:
                # 获取价格数据
                prices_df = data_service.get_prices_df(
                    ticker=ticker,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if not prices_df.empty:
                    price_data[ticker] = prices_df
                    
                    # 计算收益率
                    returns_data[ticker] = risk_calculator.calculate_returns(prices_df)
            except Exception as e:
                logger.error(f"Error fetching data for {ticker}: {e}")
        
        # 如果没有价格数据，返回空结果
        if not price_data:
            logger.warning("No price data available for risk analysis")
            return {
                'status': 'error',
                'message': 'No price data available for risk analysis'
            }
        
        # 计算各资产的风险指标
        asset_metrics = {}
        for ticker, prices_df in price_data.items():
            try:
                metrics = risk_calculator.calculate_risk_metrics(
                    prices=prices_df,
                    portfolio_value=positions[ticker].get('long', 0) * positions[ticker].get('long_cost_basis', 0)
                )
                asset_metrics[ticker] = metrics
            except Exception as e:
                logger.error(f"Error calculating risk metrics for {ticker}: {e}")
        
        # 计算投资组合收益率（加权平均）
        portfolio_returns = pd.Series(0, index=next(iter(returns_data.values())).index)
        for ticker, returns in returns_data.items():
            position = positions[ticker]
            weight = (position.get('long', 0) * position.get('long_cost_basis', 0)) / total_value
            portfolio_returns += returns * weight
        
        # 计算投资组合风险指标
        portfolio_metrics = risk_calculator.calculate_risk_metrics(
            prices=pd.DataFrame({'close': (1 + portfolio_returns).cumprod()}),
            portfolio_value=total_value
        )
        
        # 计算相关性矩阵
        correlation_matrix = risk_calculator.calculate_correlation_matrix(returns_data)
        
        # 计算风险贡献
        weights = []
        tickers = []
        for ticker, position in positions.items():
            if ticker in price_data:
                weight = (position.get('long', 0) * position.get('long_cost_basis', 0)) / total_value
                weights.append(weight)
                tickers.append(ticker)
        
        weights = np.array(weights)
        
        # 计算协方差矩阵
        returns_df = pd.DataFrame({ticker: returns for ticker, returns in returns_data.items() if ticker in tickers})
        cov_matrix = returns_df.cov()
        
        # 计算风险贡献
        risk_contrib = {}
        if len(weights) > 0:
            contrib = risk_calculator.calculate_risk_contribution(weights, cov_matrix)
            for i, ticker in enumerate(tickers):
                risk_contrib[ticker] = contrib.iloc[i]  # 使用iloc按位置访问，而不是直接使用整数索引
        
        # 检查是否触发任何风险警报
        alerts = self._check_risk_alerts(portfolio_metrics, asset_metrics)
        
        # 更新风险状态
        self.risk_state['portfolio_metrics'] = portfolio_metrics
        self.risk_state['asset_metrics'] = asset_metrics
        self.risk_state['correlation_matrix'] = correlation_matrix.to_dict()
        self.risk_state['risk_contribution'] = risk_contrib
        self.risk_state['alerts'] = alerts
        
        # 计算仓位限制
        position_limits = self._calculate_position_limits(
            portfolio=portfolio,
            asset_metrics=asset_metrics
        )
        self.risk_state['position_limits'] = position_limits
        
        # 返回风险分析结果
        result = {
            'status': 'success',
            'portfolio_metrics': portfolio_metrics,
            'asset_metrics': asset_metrics,
            'correlation_matrix': correlation_matrix.to_dict(),
            'risk_contribution': risk_contrib,
            'alerts': alerts,
            'position_limits': position_limits
        }
        
        return result
    
    def _check_risk_alerts(self, portfolio_metrics: Dict[str, Any], 
                         asset_metrics: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        检查风险警报
        
        参数:
            portfolio_metrics: 投资组合风险指标
            asset_metrics: 各资产风险指标
            
        返回:
            风险警报列表
        """
        alerts = []
        
        # 检查投资组合VaR是否超过限制
        if portfolio_metrics['var_95'] > self.var_limit * portfolio_metrics.get('portfolio_value', 1.0):
            alerts.append({
                'level': 'warning',
                'type': 'var_breach',
                'message': f"Portfolio VaR (95%) exceeds limit: {portfolio_metrics['var_95']:.2f}",
                'value': portfolio_metrics['var_95'],
                'limit': self.var_limit * portfolio_metrics.get('portfolio_value', 1.0)
            })
        
        # 检查最大回撤是否超过限制
        if portfolio_metrics['max_drawdown'] > self.max_drawdown_limit:
            alerts.append({
                'level': 'warning',
                'type': 'drawdown_breach',
                'message': f"Portfolio drawdown exceeds limit: {portfolio_metrics['max_drawdown']:.2%}",
                'value': portfolio_metrics['max_drawdown'],
                'limit': self.max_drawdown_limit
            })
        
        # 检查各资产的波动率是否异常高
        for ticker, metrics in asset_metrics.items():
            if metrics['volatility'] > 0.5:  # 年化波动率超过50%
                alerts.append({
                    'level': 'info',
                    'type': 'high_volatility',
                    'message': f"High volatility for {ticker}: {metrics['volatility']:.2%}",
                    'ticker': ticker,
                    'value': metrics['volatility']
                })
        
        return alerts
    
    def _calculate_position_limits(self, portfolio: Dict[str, Any], 
                                 asset_metrics: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        计算仓位限制
        
        参数:
            portfolio: 投资组合数据
            asset_metrics: 各资产风险指标
            
        返回:
            仓位限制字典
        """
        position_limits = {}
        
        # 计算投资组合总价值
        total_value = portfolio.get('cash', 0)
        for ticker, position in portfolio.get('positions', {}).items():
            long_value = position.get('long', 0) * position.get('long_cost_basis', 0)
            short_value = position.get('short', 0) * position.get('short_cost_basis', 0)
            total_value += long_value - short_value
        
        # 计算各资产的仓位限制
        for ticker, position in portfolio.get('positions', {}).items():
            # 获取当前仓位价值
            long_value = position.get('long', 0) * position.get('long_cost_basis', 0)
            short_value = position.get('short', 0) * position.get('short_cost_basis', 0)
            current_value = long_value - short_value
            
            # 基础仓位限制（基于投资组合总价值的百分比）
            base_limit = total_value * self.max_position_size
            
            # 调整因子（基于资产波动率）
            volatility_factor = 1.0
            if ticker in asset_metrics:
                vol = asset_metrics[ticker].get('volatility', 0)
                # 波动率越高，调整因子越低
                volatility_factor = max(0.2, 1.0 - vol)
            
            # 计算调整后的仓位限制
            adjusted_limit = base_limit * volatility_factor
            
            # 计算剩余可用限额
            remaining_limit = adjusted_limit - abs(current_value)
            
            position_limits[ticker] = {
                'base_limit': base_limit,
                'adjusted_limit': adjusted_limit,
                'current_value': current_value,
                'remaining_limit': max(0, remaining_limit),
                'volatility_factor': volatility_factor
            }
        
        return position_limits
    
    def adjust_position_size(self, ticker: str, signal_strength: float, 
                           current_price: float) -> Dict[str, Any]:
        """
        调整仓位大小
        
        参数:
            ticker: 股票代码
            signal_strength: 信号强度（-1到1之间，负值表示做空）
            current_price: 当前价格
            
        返回:
            调整后的仓位建议
        """
        # 获取仓位限制
        position_limit = self.risk_state.get('position_limits', {}).get(ticker, {})
        remaining_limit = position_limit.get('remaining_limit', 0)
        
        # 根据信号强度计算目标仓位价值
        target_value = remaining_limit * abs(signal_strength)
        
        # 计算股数
        shares = int(target_value / current_price)
        
        # 确定交易方向
        direction = 'buy' if signal_strength > 0 else 'sell' if signal_strength < 0 else 'hold'
        
        return {
            'ticker': ticker,
            'direction': direction,
            'shares': shares,
            'estimated_value': shares * current_price,
            'signal_strength': signal_strength,
            'limit_used': (shares * current_price) / position_limit.get('adjusted_limit', 1) if position_limit else 0
        }
    
    def check_circuit_breaker(self) -> Dict[str, Any]:
        """
        检查是否需要触发熔断机制
        
        返回:
            熔断状态信息
        """
        # 检查是否有严重警报
        severe_alerts = [alert for alert in self.risk_state.get('alerts', []) 
                        if alert.get('level') == 'severe']
        
        # 检查投资组合回撤
        portfolio_metrics = self.risk_state.get('portfolio_metrics', {})
        max_drawdown = portfolio_metrics.get('max_drawdown', 0)
        
        # 熔断条件
        circuit_breaker_triggered = False
        reason = None
        
        # 条件1：有严重警报
        if severe_alerts:
            circuit_breaker_triggered = True
            reason = f"Severe risk alert: {severe_alerts[0].get('message')}"
        
        # 条件2：回撤超过阈值
        elif max_drawdown > self.max_drawdown_limit * 1.5:  # 超过限制的1.5倍
            circuit_breaker_triggered = True
            reason = f"Excessive drawdown: {max_drawdown:.2%}"
        
        # 更新熔断状态
        self.risk_state['circuit_breaker_active'] = circuit_breaker_triggered
        
        return {
            'active': circuit_breaker_triggered,
            'reason': reason,
            'timestamp': datetime.now().isoformat(),
            'alerts': severe_alerts
        }
    
    def get_risk_report(self) -> Dict[str, Any]:
        """
        获取风险报告
        
        返回:
            风险报告
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'portfolio_metrics': self.risk_state.get('portfolio_metrics', {}),
            'alerts': self.risk_state.get('alerts', []),
            'position_limits': self.risk_state.get('position_limits', {}),
            'circuit_breaker': {
                'active': self.risk_state.get('circuit_breaker_active', False)
            }
        }


# 创建全局风险管理器实例
risk_manager = RiskManager()