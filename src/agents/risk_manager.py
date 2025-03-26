"""
风险管理代理

控制仓位大小和风险暴露
"""
from langchain_core.messages import HumanMessage
from graph.state import AgentState, show_agent_reasoning
from utils.progress import progress
from tools.api import get_prices, prices_to_df
from risk.manager import risk_manager
import json
from datetime import datetime, timedelta


##### Risk Management Agent #####
def risk_management_agent(state: AgentState):
    """
    控制基于实际风险因素的仓位大小和风险暴露
    
    使用高级风险管理系统分析投资组合风险，计算仓位限制，
    并检查是否需要触发熔断机制
    """
    portfolio = state["data"]["portfolio"]
    data = state["data"]
    tickers = data["tickers"]
    
    # 获取分析日期范围（使用过去3个月的数据进行风险分析）
    end_date = data["end_date"]
    start_date_obj = datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=90)
    start_date = start_date_obj.strftime("%Y-%m-%d")
    
    progress.update_status("risk_management_agent", None, "Analyzing portfolio risk")
    
    # 初始化风险分析结果
    risk_analysis = {}
    current_prices = {}  # 存储当前价格以避免重复API调用
    
    # 获取每个股票的价格数据
    price_data = {}
    for ticker in tickers:
        progress.update_status("risk_management_agent", ticker, "Fetching price data")
        
        prices = get_prices(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
        )
        
        if not prices:
            progress.update_status("risk_management_agent", ticker, "Failed: No price data found")
            continue
        
        prices_df = prices_to_df(prices)
        price_data[ticker] = prices_df
        
        # 存储当前价格
        current_prices[ticker] = float(prices_df["close"].iloc[-1])
    
    # 分析投资组合风险
    progress.update_status("risk_management_agent", None, "Analyzing portfolio risk metrics")
    
    # 使用风险管理器分析投资组合
    risk_result = risk_manager.analyze_portfolio(
        portfolio=portfolio,
        start_date=start_date,
        end_date=end_date
    )
    
    # 检查是否需要触发熔断机制
    circuit_breaker = risk_manager.check_circuit_breaker()
    
    # 为每个股票生成风险分析结果
    for ticker in tickers:
        if ticker not in current_prices:
            continue
            
        progress.update_status("risk_management_agent", ticker, "Calculating position limits")
        
        # 获取仓位限制
        position_limit = risk_manager.risk_state.get('position_limits', {}).get(ticker, {})
        
        # 获取资产风险指标
        asset_metrics = risk_manager.risk_state.get('asset_metrics', {}).get(ticker, {})
        
        # 构建风险分析结果
        risk_analysis[ticker] = {
            "remaining_position_limit": float(position_limit.get('remaining_limit', 0)),
            "current_price": current_prices[ticker],
            "volatility": asset_metrics.get('volatility', 0),
            "var_95": asset_metrics.get('var_95', 0),
            "max_drawdown": asset_metrics.get('max_drawdown', 0),
            "circuit_breaker_active": circuit_breaker.get('active', False),
            "reasoning": {
                "portfolio_value": float(portfolio.get("cash", 0) + sum(
                    portfolio.get("positions", {}).get(t, {}).get("long", 0) * 
                    portfolio.get("positions", {}).get(t, {}).get("long_cost_basis", 0)
                    for t in portfolio.get("positions", {})
                )),
                "position_limit": float(position_limit.get('adjusted_limit', 0)),
                "volatility_factor": float(position_limit.get('volatility_factor', 1.0)),
                "available_cash": float(portfolio.get("cash", 0)),
            },
        }
        
        # 如果有警报，添加到分析结果中
        alerts = [alert for alert in risk_manager.risk_state.get('alerts', []) 
                 if alert.get('ticker') == ticker]
        if alerts:
            risk_analysis[ticker]["alerts"] = alerts
        
        progress.update_status("risk_management_agent", ticker, "Done")
    
    # 添加投资组合级别的风险指标
    portfolio_metrics = risk_manager.risk_state.get('portfolio_metrics', {})
    risk_analysis["_portfolio"] = {
        "var_95": portfolio_metrics.get('var_95', 0),
        "cvar_95": portfolio_metrics.get('cvar_95', 0),
        "volatility": portfolio_metrics.get('volatility', 0),
        "max_drawdown": portfolio_metrics.get('max_drawdown', 0),
        "sharpe_ratio": portfolio_metrics.get('sharpe_ratio', 0),
        "circuit_breaker": circuit_breaker
    }
    
    # 创建消息
    message = HumanMessage(
        content=json.dumps(risk_analysis),
        name="risk_management_agent",
    )
    
    # 如果需要显示推理过程
    if state["metadata"]["show_reasoning"]:
        show_agent_reasoning(risk_analysis, "Risk Management Agent")
    
    # 将信号添加到分析信号列表
    state["data"]["analyst_signals"]["risk_management_agent"] = risk_analysis
    
    return {
        "messages": state["messages"] + [message],
        "data": data,
    }
