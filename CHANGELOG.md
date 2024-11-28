# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.2] - 2024-11-29

### Changed

- change `DEFAULT_DIR_NAME` to ".modular_trader_log"

### Fixed 

- `get_latest_bar` -> no longer input `self.feed` to `StockLatestBarRequest` and `CryptoLatestBarRequest`
- `get_historical_data` -> no longer input `self.feed` to `StockHistoricalBarRequest`


## [0.0.1] - 2024-10-01

### Added

- First Release