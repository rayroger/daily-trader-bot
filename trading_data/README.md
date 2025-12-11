# Trading Data

This directory contains the persistent data for the daily trading bot.

## Files

- **portfolio_state.json** - Current portfolio state including cash balance and positions
- **trading_history.json** - Complete history of all trading sessions
- **analysis/** - Daily analysis results (one file per day)

## Structure

### portfolio_state.json
```json
{
  "cash_balance": 100000.0,
  "positions": [
    {
      "symbol": "AAPL",
      "quantity": 10,
      "avg_price": 150.0,
      "total_cost": 1500.0
    }
  ],
  "total_value": 101500.0,
  "initial_balance": 100000.0,
  "last_updated": "2025-12-11T20:45:00"
}
```

### trading_history.json
```json
[
  {
    "timestamp": "2025-12-11T20:45:00",
    "date": "2025-12-11",
    "symbols_analyzed": 5,
    "signals": [...],
    "orders": [...],
    "portfolio_value": 101500.0,
    "cash_balance": 100000.0
  }
]
```

## Notes

- This data is automatically updated by the GitHub Actions workflow
- All files are version controlled to track trading history
- Data is stored in JSON format for easy reading and version control
