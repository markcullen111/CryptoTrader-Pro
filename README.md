# CryptoTrader Pro

An advanced cryptocurrency trading platform built with Python, featuring AI-powered strategies, real-time trading, and comprehensive analytics.

## Features

- 🤖 AI-powered trading strategies
- 📊 Real-time trading and monitoring
- 📈 Advanced performance analytics
- 🔄 Strategy management and optimization
- 📉 Risk management tools
- 🔍 Backtesting capabilities
- 📊 Experiment tracking
- 📱 Modern web interface

## Quick Start

### Prerequisites

- Python 3.8 or later
- Git

### Installation

#### Windows

1. Clone the repository:
   ```bash
   git clone https://github.com/markcullen111/CryptoTrader-Pro.git
   cd CryptoTrader-Pro
   ```

2. Run the setup script:
   ```bash
   setup_windows.bat
   ```

3. Edit the configuration files:
   - Open `config/config.yaml` and update your exchange settings
   - Open `.env` and add your API keys

4. Start the application:
   ```bash
   run.bat
   ```

#### Linux/macOS

1. Clone the repository:
   ```bash
   git clone https://github.com/markcullen111/CryptoTrader-Pro.git
   cd CryptoTrader-Pro
   ```

2. Make the setup script executable and run it:
   ```bash
   chmod +x setup_linux.sh
   ./setup_linux.sh
   ```

3. Edit the configuration files:
   - Open `config/config.yaml` and update your exchange settings
   - Open `.env` and add your API keys

4. Start the application:
   ```bash
   ./run.sh
   ```

### Configuration

The setup scripts will create the following configuration files:

1. `config/config.yaml`: Main configuration file
   ```yaml
   exchange:
     name: binance
     api_key: ""
     api_secret: ""
     testnet: false

   trading:
     default_symbol: "BTC/USDT"
     default_timeframe: "1h"
     risk_per_trade: 0.02
     max_positions: 5

   risk_management:
     max_drawdown: 0.1
     stop_loss: 0.02
     take_profit: 0.04
     trailing_stop: 0.01
   ```

2. `.env`: Environment variables (API keys)
   ```
   EXCHANGE_API_KEY=your_api_key_here
   EXCHANGE_API_SECRET=your_api_secret_here
   ```

### Directory Structure

```
CryptoTrader-Pro/
├── app/                    # Application source code
├── config/                 # Configuration files
├── data/                   # Data storage
├── logs/                   # Application logs
├── models/                 # ML models
├── tests/                  # Test suite
├── setup_linux.sh         # Linux setup script
├── setup_windows.bat      # Windows setup script
├── run.sh                 # Linux run script
├── run.bat                # Windows run script
└── requirements.txt       # Python dependencies
```

## Development

### Git Workflow

We follow a structured Git workflow to maintain code quality and collaboration:

#### Branch Strategy

- `main`: Production-ready code
- `develop`: Main development branch
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `hotfix/*`: Urgent production fixes
- `release/*`: Release preparation
- `streamlit_cloud_deploy`: Streamlit Cloud deployment

#### Commit Conventions

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

Examples:
```bash
git commit -m "feat(trading): add real-time price alerts"
git commit -m "fix(dashboard): resolve data refresh issue"
git commit -m "docs: update installation instructions"
```

#### Development Workflow

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

3. Keep your branch updated:
   ```bash
   git fetch origin
   git rebase origin/develop
   ```

4. Push your changes:
   ```bash
   git push origin feature/your-feature-name
   ```

5. Create a Pull Request:
   - Use the PR template
   - Link related issues
   - Request reviews
   - Ensure CI passes

### Running Tests

```bash
pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch following the branch naming convention
3. Make your changes following the commit conventions
4. Push to your fork
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This software is for educational purposes only. Use at your own risk. The authors are not responsible for any financial losses incurred through the use of this software.

## Support

For support, please:
1. Check the [Documentation](docs/)
2. Search existing [Issues](https://github.com/markcullen111/CryptoTrader-Pro/issues)
3. Open a new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information 