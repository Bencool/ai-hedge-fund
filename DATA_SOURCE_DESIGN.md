# 数据源集成设计方案

## 1. 架构改进目标

1. 支持多数据源(Yahoo Finance、Alpha Vantage等)
2. 统一数据格式
3. 增强缓存机制
4. 改进错误处理
5. 增加数据源健康检查

## 2. 新文件结构

```
src/data/
├── api/               # 数据源适配器
│   ├── yahoo.py       # Yahoo Finance适配器
│   ├── alpha.py       # Alpha Vantage适配器
│   └── base.py        # 基础适配器类
├── cache.py           # 改进的缓存系统
├── models.py          # 统一数据模型
└── data_service.py    # 数据获取主服务
```

## 3. 统一数据模型

```python
# src/data/models.py
from pydantic import BaseModel
from datetime import datetime

class PriceData(BaseModel):
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adjusted_close: float | None = None
    dividend: float | None = None
    split: float | None = None

class FundamentalData(BaseModel):
    pe_ratio: float | None
    market_cap: float | None
    dividend_yield: float | None
    # 其他基本面数据字段...
```

## 4. Yahoo Finance适配器示例

```python
# src/data/api/yahoo.py
import yfinance as yf
from .base import BaseAdapter
from ..models import PriceData, FundamentalData

class YahooFinanceAdapter(BaseAdapter):
    def __init__(self, api_key=None):  # 保持参数统一即使某些源不需要key
        self.session = yf.Ticker()
    
    def get_prices(self, ticker, start_date, end_date, interval='1d'):
        data = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            interval=interval,
            progress=False
        )
        return [PriceData(**row) for row in data.to_dict('records')]
    
    def get_fundamentals(self, ticker):
        info = yf.Ticker(ticker).info
        return FundamentalData(
            pe_ratio=info.get('trailingPE'),
            market_cap=info.get('marketCap'),
            dividend_yield=info.get('dividendYield')
        )
```

## 5. 改进的缓存系统

```python
# src/data/cache.py
from datetime import timedelta
from .models import PriceData
import diskcache

class DataCache:
    def __init__(self):
        self.cache = diskcache.Cache('./.datacache')
        self.cache_expire = timedelta(hours=6)  # 缓存6小时

    def get_prices(self, source, ticker, start, end):
        cache_key = f"{source}|{ticker}|{start}|{end}"
        if cached := self.cache.get(cache_key):
            return [PriceData(**item) for item in cached]
        return None

    def set_prices(self, source, ticker, start, end, data):
        cache_key = f"{source}|{ticker}|{start}|{end}"
        self.cache.set(cache_key, [item.dict() for item in data], self.cache_expire)
```

## 6. 数据服务协调器

```python
# src/data/data_service.py
from .api import YahooFinanceAdapter, AlphaVantageAdapter
from .cache import DataCache

class DataService:
    def __init__(self, config):
        self.cache = DataCache()
        self.adapters = {
            'yahoo': YahooFinanceAdapter(),
            'alpha': AlphaVantageAdapter(api_key=config.ALPHA_KEY)
        }
        self.default_source = 'yahoo'
    
    def get_prices(self, ticker, start, end, source=None):
        source = source or self.default_source
        if cached := self.cache.get_prices(source, ticker, start, end):
            return cached
        
        if adapter := self.adapters.get(source):
            data = adapter.get_prices(ticker, start, end)
            self.cache.set_prices(source, ticker, start, end, data)
            return data
        
        raise ValueError(f"Unsupported data source: {source}")
```

## 7. 集成步骤

1. 安装依赖：`pip install yfinance diskcache`
2. 创建配置文件`.env`：
```ini
# 数据源配置
DEFAULT_DATA_SOURCE=yahoo
ALPHA_VANTAGE_KEY=your_key_here
```

3. 修改现有调用点（如`risk_manager.py`）：
```python
# 原调用方式
# prices = get_prices(ticker, start_date, end_date)

# 新调用方式
from data.data_service import data_service
prices = data_service.get_prices(ticker, start_date, end_date)
```

## 8. 优势分析

1. **多数据源支持**：可配置使用Yahoo Finance或其他源
2. **数据一致性**：统一返回格式确保下游处理一致
3. **缓存优化**：区分不同数据源的缓存条目
4. **故障转移**：可添加自动回退机制（如Yahoo不可用时切Alpha）
5. **扩展性**：轻松添加新数据源适配器

## 9. 注意事项

1. Yahoo Finance的速率限制（非官方API）
2. 不同数据源的时间区间限制
3. 时区处理（统一转换为UTC）
4. 股票代码格式差异（如Yahoo用.T后缀表示东京交易所）
5. 数据精度差异（调整收盘价等字段）