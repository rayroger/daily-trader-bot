# Quick Start Guide: Automated Daily Trading Bot

This guide will help you set up the daily trading bot to run automatically on GitHub Actions.

## Prerequisites

- GitHub account with this repository
- (Optional) OpenAI API key for AI-powered analysis

## Setup Steps

### 1. Fork or Clone the Repository

If you haven't already, fork this repository to your own GitHub account.

### 2. Enable GitHub Actions

1. Go to your repository on GitHub
2. Click on the **Settings** tab
3. Navigate to **Actions** → **General**
4. Under "Actions permissions", select **Allow all actions and reusable workflows**
5. Click **Save**

### 3. (Optional) Add OpenAI API Key

If you want to use AI-powered market analysis:

1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
2. In your GitHub repository, go to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `OPENAI_API_KEY`
5. Value: Your OpenAI API key
6. Click **Add secret**

> **Note:** The bot works without an OpenAI API key, but AI features will be disabled.

### 4. Configure Trading Symbols (Optional)

Edit the symbols the bot will analyze:

1. Open `.github/workflows/daily-bot.yml`
2. Or create a `config.json` file (copy from `config.example.json`)
3. Modify the `trading.symbols` value with your preferred stocks

Default symbols: `AAPL,MSFT,GOOGL,AMZN,TSLA`

### 5. Initialize Portfolio

On first run, the bot will automatically initialize a portfolio with $100,000 in paper trading funds.

To customize the initial balance:

1. Create a `config.json` file:
   ```bash
   cp config.example.json config.json
   ```
2. Edit `broker.initial_balance` to your desired amount
3. Commit and push the config file

### 6. Manual First Run (Recommended)

Test the bot manually before the scheduled run:

1. Go to the **Actions** tab in your repository
2. Select **Daily Trading Bot** from the left sidebar
3. Click **Run workflow** button
4. Click the green **Run workflow** button
5. Wait for the workflow to complete
6. Check the logs to verify everything works

### 7. Verify the Results

After the first run:

1. Check the `trading_data/` directory in your repository
2. You should see:
   - `portfolio_state.json` - Current portfolio state
   - `trading_history.json` - Trading history
   - `analysis/` directory with daily analysis files

### 8. Monitor Daily Runs

The bot will now run automatically every weekday at 4:30 PM ET (after market close).

To monitor:

1. Check the **Actions** tab for run history
2. Review commit history - each run creates a commit
3. Examine the trading_data files for portfolio status

## Customization Options

### Change Schedule

Edit `.github/workflows/daily-bot.yml`:

```yaml
schedule:
  - cron: '30 21 * * 1-5'  # 4:30 PM ET, Mon-Fri
```

Use [crontab.guru](https://crontab.guru/) to generate different schedules.

### Disable Auto-Trading

To only analyze without executing trades:

1. Create/edit `config.json`
2. Set `trading.auto_execute` to `false`
3. Or manually trigger with `execute_trades: false`

### Change Trading Quantity

Edit `config.json`:

```json
{
  "trading": {
    "default_quantity": 10
  }
}
```

### Adjust Strategy Parameters

Edit `config.json`:

```json
{
  "strategy": {
    "min_confidence": 0.6,
    "stop_loss_pct": 0.05,
    "take_profit_pct": 0.10
  }
}
```

## Understanding the Data

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
  "initial_balance": 100000.0
}
```

### trading_history.json

Contains all trading sessions with:
- Date and timestamp
- Symbols analyzed
- Trading signals generated
- Orders executed
- Portfolio value

## Troubleshooting

### Bot Not Running

1. Check if GitHub Actions is enabled
2. Verify the workflow file exists: `.github/workflows/daily-bot.yml`
3. Check Actions tab for error messages

### Network Errors

- The bot fetches data from Yahoo Finance
- Network issues may cause failures
- The bot will retry on next scheduled run

### API Errors

- If using OpenAI, verify your API key is correct
- Check that you have API credits available
- Bot works without OpenAI, just without AI features

### Data Not Committing

1. Check workflow permissions in Settings → Actions → General
2. Ensure "Read and write permissions" is enabled
3. Verify git is configured correctly in the workflow

## Next Steps

- Monitor the bot's performance over time
- Adjust strategy parameters based on results
- Review trading_history.json to analyze decisions
- Consider training price prediction models for better accuracy

## Safety Reminders

⚠️ **Important:**
- This is **paper trading only** - no real money is used
- Do not connect to real brokers without thorough testing
- Past performance doesn't guarantee future results
- This is for educational purposes only

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing issues and discussions
- Review the main README.md for more details
