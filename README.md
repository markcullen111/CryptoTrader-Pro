# CryptoTrader Pro

A professional cryptocurrency trading application with advanced features for automated trading, backtesting, and strategy development.

## Features

- Real-time trading on Binance
- Multiple trading strategies
- Advanced backtesting capabilities
- Machine learning model integration
- Experiment tracking
- Performance monitoring
- Risk management
- Beautiful web interface

## Quick Installation

### Prerequisites

- Python 3.8 or higher
- Git

### One-Line Installation (Linux/Mac)

```bash
git clone https://github.com/yourusername/cryptotrader-pro.git && cd cryptotrader-pro && python3 install.py
```

### Step-by-Step Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cryptotrader-pro.git
   cd cryptotrader-pro
   ```

2. Run the installation script:
   ```bash
   # On Linux/Mac
   python3 install.py

   # On Windows
   python install.py
   ```

3. Configure your settings:
   - Edit `config/config.yaml` with your trading preferences
   - Edit `.env` with your API keys and secrets

4. Start the application:
   ```bash
   # On Linux/Mac
   ./run.sh

   # On Windows
   run.bat
   ```

5. Open your web browser and go to:
   ```
   http://localhost:8501
   ```

## Configuration

### Setting Up API Keys

1. Log into your Binance account
2. Go to API Management in your account settings
3. Create a new API key with the following permissions:
   - Enable Reading
   - Enable Spot & Margin Trading
   - Disable Withdrawals
4. Copy the API key and secret to your `.env` file

### Trading Configuration

Edit `config/config.yaml` to configure:
- Trading pairs
- Risk management settings
- Strategy parameters
- Monitoring preferences
- Database settings

## Features in Detail

### Trading
- Real-time market data
- Multiple order types (market, limit)
- Position management
- Risk controls

### Backtesting
- Historical data analysis
- Strategy optimization
- Performance metrics
- Risk analysis

### Machine Learning
- Feature engineering
- Model training
- Prediction integration
- Performance tracking

### Monitoring
- Real-time performance metrics
- Trade history
- Portfolio analysis
- Risk metrics

## Support

For issues and feature requests, please use the GitHub issue tracker.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Security Notice

Never share your API keys or secrets. The `.env` file containing your credentials is excluded from version control for security. 