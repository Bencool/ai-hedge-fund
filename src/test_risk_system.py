"""
风险管理系统测试脚本

测试新的风险管理系统功能
"""
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# 导入项目模块
from src.data.data_service import data_service
from src.risk.metrics import risk_calculator
from src.risk.manager import risk_manager


def test_data_service():
    """测试数据服务"""
    print("\n=== 测试数据服务 ===")
    
    # 测试股票列表
    tickers = ['AAPL', 'MSFT', 'GOOGL']
    
    # 测试日期范围
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    
    print(f"获取数据: {tickers} 从 {start_date} 到 {end_date}")
    
    # 测试获取价格数据
    for ticker in tickers:
        try:
            prices = data_service.get_prices(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date
            )
            
            print(f"{ticker}: 获取到 {len(prices)} 条价格记录")
            
            # 测试转换为DataFrame
            df = data_service.get_prices_df(
                ticker=ticker,
                start_date=start_date,
                end_date=end_date
            )
            
            print(f"{ticker} DataFrame 形状: {df.shape}")
            
            # 测试获取基本面数据
            fundamentals = data_service.get_fundamentals(ticker=ticker)
            print(f"{ticker} 基本面数据: PE={fundamentals.get('pe_ratio')}, 市值={fundamentals.get('market_cap')}")
            
        except Exception as e:
            print(f"获取 {ticker} 数据时出错: {e}")
    
    # 测试缓存统计
    cache_stats = data_service.get_cache_stats()
    print(f"缓存统计: {cache_stats}")
    
    return True


def test_risk_metrics():
    """测试风险指标计算"""
    print("\n=== 测试风险指标计算 ===")
    
    # 测试股票
    ticker = 'AAPL'
    
    # 测试日期范围
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    print(f"计算 {ticker} 的风险指标 从 {start_date} 到 {end_date}")
    
    try:
        # 获取价格数据
        prices_df = data_service.get_prices_df(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date
        )
        
        if prices_df.empty:
            print(f"无法获取 {ticker} 的价格数据")
            return False
        
        # 计算收益率
        returns = risk_calculator.calculate_returns(prices_df)
        print(f"收益率统计: 均值={returns.mean():.4f}, 标准差={returns.std():.4f}")
        
        # 计算波动率
        volatility = risk_calculator.calculate_volatility(returns, window=None)
        print(f"年化波动率: {volatility:.4f}")
        
        # 计算VaR
        var_95 = risk_calculator.calculate_var(returns, confidence_level=0.95)
        var_99 = risk_calculator.calculate_var(returns, confidence_level=0.99)
        print(f"VaR (95%): {var_95:.4f}")
        print(f"VaR (99%): {var_99:.4f}")
        
        # 计算CVaR
        cvar_95 = risk_calculator.calculate_cvar(returns, confidence_level=0.95)
        print(f"CVaR (95%): {cvar_95:.4f}")
        
        # 计算回撤
        drawdown, max_drawdown, max_dd_duration = risk_calculator.calculate_drawdown(prices_df)
        print(f"最大回撤: {max_drawdown:.4f}")
        print(f"最长回撤持续期: {max_dd_duration} 天")
        
        # 计算夏普比率
        sharpe = risk_calculator.calculate_sharpe_ratio(returns)
        print(f"夏普比率: {sharpe:.4f}")
        
        # 计算综合风险指标
        metrics = risk_calculator.calculate_risk_metrics(prices_df)
        print("\n综合风险指标:")
        for key, value in metrics.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                print(f"  {key}: {value:.4f}")
        
        # 绘制回撤图
        plt.figure(figsize=(12, 6))
        drawdown.plot()
        plt.title(f"{ticker} 回撤")
        plt.xlabel("日期")
        plt.ylabel("回撤")
        plt.grid(True)
        plt.savefig("drawdown.png")
        print(f"回撤图已保存为 drawdown.png")
        
    except Exception as e:
        print(f"计算风险指标时出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_risk_manager():
    """测试风险管理器"""
    print("\n=== 测试风险管理器 ===")
    
    # 测试投资组合
    portfolio = {
        "cash": 100000.0,
        "positions": {
            "AAPL": {
                "long": 100,
                "short": 0,
                "long_cost_basis": 150.0,
                "short_cost_basis": 0.0
            },
            "MSFT": {
                "long": 50,
                "short": 0,
                "long_cost_basis": 300.0,
                "short_cost_basis": 0.0
            },
            "GOOGL": {
                "long": 20,
                "short": 0,
                "long_cost_basis": 120.0,
                "short_cost_basis": 0.0
            }
        }
    }
    
    # 测试日期范围
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    
    print(f"分析投资组合风险 从 {start_date} 到 {end_date}")
    
    try:
        # 分析投资组合风险
        risk_result = risk_manager.analyze_portfolio(
            portfolio=portfolio,
            start_date=start_date,
            end_date=end_date
        )
        
        if risk_result.get('status') == 'error':
            print(f"分析投资组合风险时出错: {risk_result.get('message')}")
            return False
        
        # 打印投资组合风险指标
        portfolio_metrics = risk_result.get('portfolio_metrics', {})
        print("\n投资组合风险指标:")
        for key, value in portfolio_metrics.items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                print(f"  {key}: {value:.4f}")
        
        # 打印资产风险指标
        asset_metrics = risk_result.get('asset_metrics', {})
        print("\n资产风险指标:")
        for ticker, metrics in asset_metrics.items():
            print(f"\n{ticker}:")
            for key, value in metrics.items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    print(f"  {key}: {value:.4f}")
        
        # 打印仓位限制
        position_limits = risk_result.get('position_limits', {})
        print("\n仓位限制:")
        for ticker, limits in position_limits.items():
            print(f"\n{ticker}:")
            for key, value in limits.items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    print(f"  {key}: {value:.2f}")
        
        # 打印警报
        alerts = risk_result.get('alerts', [])
        print(f"\n警报数量: {len(alerts)}")
        for alert in alerts:
            print(f"  {alert.get('level')}: {alert.get('message')}")
        
        # 检查熔断机制
        circuit_breaker = risk_manager.check_circuit_breaker()
        print(f"\n熔断状态: {'激活' if circuit_breaker.get('active') else '未激活'}")
        if circuit_breaker.get('active'):
            print(f"熔断原因: {circuit_breaker.get('reason')}")
        
        # 测试仓位调整
        ticker = 'AAPL'
        signal_strength = 0.8
        current_price = asset_metrics.get(ticker, {}).get('current_price', 150.0)
        
        position_adjustment = risk_manager.adjust_position_size(
            ticker=ticker,
            signal_strength=signal_strength,
            current_price=current_price
        )
        
        print(f"\n仓位调整建议 ({ticker}, 信号强度={signal_strength}):")
        for key, value in position_adjustment.items():
            print(f"  {key}: {value}")
        
        # 绘制相关性矩阵热图
        correlation_matrix = pd.DataFrame(risk_result.get('correlation_matrix', {}))
        if not correlation_matrix.empty:
            plt.figure(figsize=(10, 8))
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
            plt.title("资产相关性矩阵")
            plt.savefig("correlation_matrix.png")
            print(f"相关性矩阵热图已保存为 correlation_matrix.png")
        
    except Exception as e:
        print(f"测试风险管理器时出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """主函数"""
    print("=== 风险管理系统测试 ===")
    
    # 测试数据服务
    if not test_data_service():
        print("数据服务测试失败")
        return
    
    # 测试风险指标计算
    if not test_risk_metrics():
        print("风险指标计算测试失败")
        return
    
    # 测试风险管理器
    if not test_risk_manager():
        print("风险管理器测试失败")
        return
    
    print("\n=== 所有测试通过 ===")


if __name__ == "__main__":
    main()