"""
风险指标计算器

提供各种风险指标的计算功能，包括VaR、CVaR、波动率等
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
import scipy.stats as stats
from functools import lru_cache

from data.models import PriceData


class RiskMetricsCalculator:
    """
    风险指标计算器
    
    提供各种风险指标的计算功能
    """
    
    def __init__(self, risk_free_rate: float = 0.0):
        """
        初始化风险指标计算器
        
        参数:
            risk_free_rate: 无风险利率（年化）
        """
        self.risk_free_rate = risk_free_rate
        self.daily_risk_free_rate = (1 + risk_free_rate) ** (1/252) - 1
    
    def calculate_returns(self, prices: pd.DataFrame, method: str = 'simple') -> pd.Series:
        """
        计算收益率
        
        参数:
            prices: 价格数据DataFrame（必须包含'close'列）
            method: 计算方法 ('simple'=简单收益率, 'log'=对数收益率)
            
        返回:
            收益率Series
        """
        if method == 'simple':
            return prices['close'].pct_change().dropna()
        elif method == 'log':
            return np.log(prices['close'] / prices['close'].shift(1)).dropna()
        else:
            raise ValueError(f"Unsupported return calculation method: {method}")
    
    def calculate_volatility(self, returns: pd.Series, window: int = 252, 
                           annualized: bool = True) -> Union[float, pd.Series]:
        """
        计算波动率
        
        参数:
            returns: 收益率Series
            window: 滚动窗口大小（如果为None，则计算整个周期的波动率）
            annualized: 是否年化
            
        返回:
            如果window为None，返回单一波动率值；否则返回滚动波动率Series
        """
        if window is None:
            vol = returns.std()
            if annualized:
                vol *= np.sqrt(252)  # 假设一年有252个交易日
            return vol
        
        # 计算滚动波动率
        rolling_vol = returns.rolling(window=window).std()
        if annualized:
            rolling_vol *= np.sqrt(252)
        
        return rolling_vol
    
    def calculate_var(self, returns: pd.Series, confidence_level: float = 0.95, 
                    time_horizon: int = 1, method: str = 'historical',
                    portfolio_value: float = 1.0) -> float:
        """
        计算风险价值(VaR)
        
        参数:
            returns: 收益率Series
            confidence_level: 置信水平（0-1之间）
            time_horizon: 时间范围（天数）
            method: 计算方法 ('historical', 'parametric', 'monte_carlo')
            portfolio_value: 投资组合价值
            
        返回:
            VaR值（正值表示潜在损失）
        """
        alpha = 1 - confidence_level
        
        if method == 'historical':
            # 历史模拟法
            var = -np.percentile(returns, alpha * 100)
            
        elif method == 'parametric':
            # 参数法（假设正态分布）
            mean = returns.mean()
            std = returns.std()
            var = -(mean + stats.norm.ppf(confidence_level) * std)
            
        elif method == 'monte_carlo':
            # 蒙特卡洛模拟法
            mean = returns.mean()
            std = returns.std()
            simulations = 10000
            simulated_returns = np.random.normal(mean, std, simulations)
            var = -np.percentile(simulated_returns, alpha * 100)
            
        else:
            raise ValueError(f"Unsupported VaR calculation method: {method}")
        
        # 调整时间范围
        var = var * np.sqrt(time_horizon)
        
        # 转换为货币价值
        var = var * portfolio_value
        
        return var
    
    def calculate_cvar(self, returns: pd.Series, confidence_level: float = 0.95,
                      time_horizon: int = 1, portfolio_value: float = 1.0) -> float:
        """
        计算条件风险价值(CVaR/Expected Shortfall)
        
        参数:
            returns: 收益率Series
            confidence_level: 置信水平（0-1之间）
            time_horizon: 时间范围（天数）
            portfolio_value: 投资组合价值
            
        返回:
            CVaR值（正值表示潜在损失）
        """
        alpha = 1 - confidence_level
        var_percentile = np.percentile(returns, alpha * 100)
        
        # 计算超过VaR的损失的平均值
        cvar = -returns[returns <= var_percentile].mean()
        
        # 调整时间范围
        cvar = cvar * np.sqrt(time_horizon)
        
        # 转换为货币价值
        cvar = cvar * portfolio_value
        
        return cvar
    
    def calculate_drawdown(self, prices: pd.DataFrame) -> Tuple[pd.Series, float, int]:
        """
        计算回撤
        
        参数:
            prices: 价格数据DataFrame（必须包含'close'列）
            
        返回:
            (回撤Series, 最大回撤, 最长回撤持续期)
        """
        # 计算累积最大值
        rolling_max = prices['close'].cummax()
        
        # 计算回撤
        drawdown = (prices['close'] / rolling_max - 1)
        
        # 计算最大回撤
        max_drawdown = drawdown.min()
        
        # 计算最长回撤持续期
        is_in_drawdown = drawdown < 0
        drawdown_periods = []
        current_period = 0
        
        for is_dd in is_in_drawdown:
            if is_dd:
                current_period += 1
            else:
                if current_period > 0:
                    drawdown_periods.append(current_period)
                    current_period = 0
        
        # 如果当前仍在回撤中，添加当前回撤期
        if current_period > 0:
            drawdown_periods.append(current_period)
        
        max_drawdown_duration = max(drawdown_periods) if drawdown_periods else 0
        
        return drawdown, abs(max_drawdown), max_drawdown_duration
    
    def calculate_sharpe_ratio(self, returns: pd.Series, annualized: bool = True) -> float:
        """
        计算夏普比率
        
        参数:
            returns: 收益率Series
            annualized: 是否年化
            
        返回:
            夏普比率
        """
        excess_returns = returns - self.daily_risk_free_rate
        std_dev = excess_returns.std()
        
        # 处理标准差为零或NaN的情况
        if std_dev == 0 or np.isnan(std_dev):
            sharpe = 0  # 当标准差为零或NaN时，夏普比率设为0
        else:
            sharpe = excess_returns.mean() / std_dev
        
        if annualized:
            sharpe *= np.sqrt(252)  # 年化
        
        return sharpe
    
    def calculate_sortino_ratio(self, returns: pd.Series, 
                              min_acceptable_return: float = 0.0,
                              annualized: bool = True) -> float:
        """
        计算索提诺比率
        
        参数:
            returns: 收益率Series
            min_acceptable_return: 最低可接受收益率
            annualized: 是否年化
            
        返回:
            索提诺比率
        """
        excess_returns = returns - min_acceptable_return
        
        # 计算下行标准差（只考虑低于最低可接受收益率的收益）
        downside_returns = excess_returns[excess_returns < 0]
        downside_deviation = downside_returns.std()
        
        if downside_deviation == 0:
            return np.inf  # 避免除以零
        
        sortino = excess_returns.mean() / downside_deviation
        
        if annualized:
            sortino *= np.sqrt(252)  # 年化
        
        return sortino
    
    def calculate_beta(self, returns: pd.Series, market_returns: pd.Series) -> float:
        """
        计算贝塔系数
        
        参数:
            returns: 资产收益率Series
            market_returns: 市场收益率Series
            
        返回:
            贝塔系数
        """
        # 确保两个Series具有相同的索引
        aligned_returns = returns.align(market_returns, join='inner')
        asset_returns = aligned_returns[0]
        market_returns = aligned_returns[1]
        
        # 计算协方差和市场方差
        covariance = asset_returns.cov(market_returns)
        market_variance = market_returns.var()
        
        if market_variance == 0:
            return np.nan  # 避免除以零
        
        beta = covariance / market_variance
        
        return beta
    
    def calculate_alpha(self, returns: pd.Series, market_returns: pd.Series, 
                       beta: Optional[float] = None, annualized: bool = True) -> float:
        """
        计算阿尔法
        
        参数:
            returns: 资产收益率Series
            market_returns: 市场收益率Series
            beta: 贝塔系数（如果为None，则计算）
            annualized: 是否年化
            
        返回:
            阿尔法
        """
        # 确保两个Series具有相同的索引
        aligned_returns = returns.align(market_returns, join='inner')
        asset_returns = aligned_returns[0]
        market_returns = aligned_returns[1]
        
        # 如果未提供贝塔，则计算
        if beta is None:
            beta = self.calculate_beta(asset_returns, market_returns)
        
        # 计算阿尔法
        alpha = asset_returns.mean() - self.daily_risk_free_rate - beta * (market_returns.mean() - self.daily_risk_free_rate)
        
        if annualized:
            alpha = (1 + alpha) ** 252 - 1  # 年化
        
        return alpha
    
    def calculate_information_ratio(self, returns: pd.Series, benchmark_returns: pd.Series,
                                  annualized: bool = True) -> float:
        """
        计算信息比率
        
        参数:
            returns: 资产收益率Series
            benchmark_returns: 基准收益率Series
            annualized: 是否年化
            
        返回:
            信息比率
        """
        # 确保两个Series具有相同的索引
        aligned_returns = returns.align(benchmark_returns, join='inner')
        asset_returns = aligned_returns[0]
        benchmark_returns = aligned_returns[1]
        
        # 计算超额收益
        excess_returns = asset_returns - benchmark_returns
        
        # 计算信息比率
        ir = excess_returns.mean() / excess_returns.std()
        
        if annualized:
            ir *= np.sqrt(252)  # 年化
        
        return ir
    
    def calculate_omega_ratio(self, returns: pd.Series, threshold: float = 0.0) -> float:
        """
        计算Omega比率
        
        参数:
            returns: 收益率Series
            threshold: 阈值收益率
            
        返回:
            Omega比率
        """
        # 将收益率分为高于和低于阈值的部分
        returns_above = returns[returns > threshold] - threshold
        returns_below = threshold - returns[returns <= threshold]
        
        # 计算Omega比率
        if returns_below.sum() == 0:
            return np.inf  # 避免除以零
        
        omega = returns_above.sum() / returns_below.sum()
        
        return omega
    
    def calculate_correlation_matrix(self, returns_dict: Dict[str, pd.Series]) -> pd.DataFrame:
        """
        计算相关性矩阵
        
        参数:
            returns_dict: 资产代码到收益率Series的映射
            
        返回:
            相关性矩阵DataFrame
        """
        # 创建包含所有收益率的DataFrame
        returns_df = pd.DataFrame(returns_dict)
        
        # 计算相关性矩阵
        correlation_matrix = returns_df.corr()
        
        return correlation_matrix
    
    def calculate_risk_contribution(self, weights: np.ndarray, cov_matrix: pd.DataFrame) -> np.ndarray:
        """
        计算风险贡献
        
        参数:
            weights: 资产权重数组
            cov_matrix: 协方差矩阵
            
        返回:
            风险贡献数组
        """
        # 计算投资组合波动率
        portfolio_vol = np.sqrt(weights.T @ cov_matrix @ weights)
        
        # 计算边际风险贡献
        marginal_contrib = cov_matrix @ weights
        
        # 计算风险贡献
        risk_contrib = weights * marginal_contrib / portfolio_vol
        
        return risk_contrib
    
    def calculate_risk_metrics(self, prices: pd.DataFrame, 
                             benchmark_prices: Optional[pd.DataFrame] = None,
                             portfolio_value: float = 1.0) -> Dict[str, Any]:
        """
        计算综合风险指标
        
        参数:
            prices: 价格数据DataFrame（必须包含'close'列）
            benchmark_prices: 基准价格数据DataFrame（如果提供）
            portfolio_value: 投资组合价值
            
        返回:
            包含各种风险指标的字典
        """
        # 计算收益率
        returns = self.calculate_returns(prices)
        
        # 计算基准收益率（如果提供）
        benchmark_returns = None
        if benchmark_prices is not None:
            benchmark_returns = self.calculate_returns(benchmark_prices)
        
        # 计算波动率
        volatility = self.calculate_volatility(returns, window=None)
        
        # 计算VaR
        var_95 = self.calculate_var(returns, confidence_level=0.95, portfolio_value=portfolio_value)
        var_99 = self.calculate_var(returns, confidence_level=0.99, portfolio_value=portfolio_value)
        
        # 计算CVaR
        cvar_95 = self.calculate_cvar(returns, confidence_level=0.95, portfolio_value=portfolio_value)
        
        # 计算回撤
        drawdown, max_drawdown, max_drawdown_duration = self.calculate_drawdown(prices)
        
        # 计算夏普比率
        sharpe_ratio = self.calculate_sharpe_ratio(returns)
        
        # 计算索提诺比率
        sortino_ratio = self.calculate_sortino_ratio(returns)
        
        # 计算贝塔和阿尔法（如果提供基准）
        beta = None
        alpha = None
        information_ratio = None
        if benchmark_returns is not None:
            beta = self.calculate_beta(returns, benchmark_returns)
            alpha = self.calculate_alpha(returns, benchmark_returns, beta)
            information_ratio = self.calculate_information_ratio(returns, benchmark_returns)
        
        # 计算Omega比率
        omega_ratio = self.calculate_omega_ratio(returns)
        
        # 汇总结果
        metrics = {
            'volatility': volatility,
            'var_95': var_95,
            'var_99': var_99,
            'cvar_95': cvar_95,
            'max_drawdown': max_drawdown,
            'max_drawdown_duration': max_drawdown_duration,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'omega_ratio': omega_ratio,
            'beta': beta,
            'alpha': alpha,
            'information_ratio': information_ratio,
            'annualized_return': (1 + returns.mean()) ** 252 - 1,
            'skewness': returns.skew(),
            'kurtosis': returns.kurtosis(),
            'positive_days': (returns > 0).sum() / len(returns),
            'risk_free_rate': self.risk_free_rate
        }
        
        return metrics


# 创建全局风险指标计算器实例
risk_calculator = RiskMetricsCalculator()