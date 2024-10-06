<a id="readme-top"></a>

# Modular-Trader
![Python Badge](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff&style=for-the-badge)
![Pydantic Badge](https://img.shields.io/badge/Pydantic-E92063?logo=pydantic&logoColor=fff&style=for-the-badge)


<!-- ![logo](docs/source/modular-trader-logo.svg) -->
![logo](https://raw.githubusercontent.com/kfuangsung/modular-trader/refs/heads/main/docs/source/_static/modular-trader-logo.svg)



## About The Project
<!-- ![flow](docs/source/modular-trader-flow.svg) -->
![flow](https://raw.githubusercontent.com/kfuangsung/modular-trader/refs/heads/main/docs/source/_static/modular-trader-flow.svg)



Modular-trader is a algorithmic trading framework written in Python, designed with focus on modularity and flexibility. The framework provides solution as building blocks for live deployment of algorithmic trading, consists of five modules; Asset Selection, Signal Generation, Portfolio Builder, Order Execution and, Risk Management.

### Built-in Models 

#### Asset Selection 
- Manual

#### Signal Generation
- Constant

#### Portfolio Builder 
- EqualWeight
- ThresholdDeviation

#### Order Execution
- Instant

#### Risk Management
- FixedStopLoss

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Supported Brokerages

- [Alpaca](https://alpaca.markets/)

**Important Note**: We are not affiliated, associated, authorized, endorsed by, or in any way officially connected with Alpaca Securities LLC, or any of its subsidiaries or its affiliates. The official Alpaca Securities LLC website can be found at https://alpaca.markets/.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Getting Started

### Installation
```bash
pip install modular-trader
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Usage 
```python
from dotenv import load_dotenv
from modular_trader.common.enums import TradingMode
from modular_trader.engine import AlpacaEngine
from modular_trader.framework import FrameworkCollection
from modular_trader.framework.asset_selection import ManualAssetSelection
from modular_trader.framework.order_execution import InstantOrderExecution
from modular_trader.framework.portfolio_builder import EqualWeightPortfolioBuilder
from modular_trader.framework.risk_management import NullRiskManagement
from modular_trader.framework.signal_generation import ConstantSignalGeneration
from modular_trader.trader import AlpacaTrader

# set Alpaca Token  as environment variable
# create `.env` file then add
# ALPACA_API_KEY=xxxxxxxx
# ALPACA_SECRET_KEY=xxxxxxx
load_dotenv()

# Equally weighted portfolio
# with Instant rebalancing
symbols = ["SPY", "QQQ", "GLD"]
framework = FrameworkCollection(
    asset_selection=ManualAssetSelection(symbols=symbols),
    signal_generation=ConstantSignalGeneration(),
    portfolio_builder=EqualWeightPortfolioBuilder(),
    order_execution=InstantOrderExecution(),
    risk_management=NullRiskManagement(),
)

# using Paper portfolio
engine = AlpacaEngine(mode=TradingMode.PAPER)

trader = AlpacaTrader(
    engine=engine,
    framework=framework,
    subscription_symbols=symbols,
)

trader.run()
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## License 
Distributed under the MIT License. See [`LICENSE`](https://github.com/kfuangsung/modular-trader/blob/main/LICENSE) for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Maintainers

Modular-Trader is currently maintained by [kfuangsung](https://github.com/kfuangsung) (kachain.f@outlook.com).

**Important Note**: We do not provide technical support, or consulting and do not answer personal questions via email.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Acknowledgments
- [alpaca-py](https://github.com/alpacahq/alpaca-py): An official Python SDK for Alpaca APIs.
<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Disclaimer 
Authors and contributors of Modular-Trader cannot be held responsible for possible losses or other damage. Consequently, no claims for damages can be asserted. Please also note that trading has a certain addictive potential. If you find yourself at risk, please seek professional help.
<p align="right">(<a href="#readme-top">back to top</a>)</p>