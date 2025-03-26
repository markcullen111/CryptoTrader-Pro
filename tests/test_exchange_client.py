import pytest
from datetime import datetime, timedelta
from app.trading.exchange_client import ExchangeClient

def test_get_ohlcv(mock_exchange_client):
    """Test getting OHLCV data from the exchange."""
    # Setup
    symbol = "BTC/USDT"
    timeframe = "1h"
    since = datetime.now() - timedelta(days=1)
    limit = 24
    
    # Configure mock
    mock_exchange_client.get_ohlcv.return_value = [
        [int(since.timestamp() * 1000), 50000, 51000, 49000, 50500, 100],
        [int((since + timedelta(hours=1)).timestamp() * 1000), 50500, 51500, 49500, 51000, 120],
        # Add more mock data as needed
    ]
    
    # Execute
    result = mock_exchange_client.get_ohlcv(symbol, timeframe, since, limit)
    
    # Assert
    assert result is not None
    assert len(result) > 0
    assert len(result[0]) == 6  # timestamp, open, high, low, close, volume
    mock_exchange_client.get_ohlcv.assert_called_once_with(symbol, timeframe, since, limit)

def test_get_balance(mock_exchange_client):
    """Test getting account balance."""
    # Setup
    mock_exchange_client.get_balance.return_value = {
        "BTC": {"free": 1.0, "used": 0.5, "total": 1.5},
        "USDT": {"free": 50000, "used": 10000, "total": 60000}
    }
    
    # Execute
    result = mock_exchange_client.get_balance()
    
    # Assert
    assert result is not None
    assert "BTC" in result
    assert "USDT" in result
    assert all(key in result["BTC"] for key in ["free", "used", "total"])
    mock_exchange_client.get_balance.assert_called_once()

def test_create_order(mock_exchange_client):
    """Test creating a new order."""
    # Setup
    symbol = "BTC/USDT"
    order_type = "limit"
    side = "buy"
    amount = 0.1
    price = 50000
    
    mock_exchange_client.create_order.return_value = {
        "id": "123456",
        "symbol": symbol,
        "type": order_type,
        "side": side,
        "amount": amount,
        "price": price,
        "status": "open"
    }
    
    # Execute
    result = mock_exchange_client.create_order(symbol, order_type, side, amount, price)
    
    # Assert
    assert result is not None
    assert result["id"] == "123456"
    assert result["symbol"] == symbol
    assert result["type"] == order_type
    assert result["side"] == side
    assert result["amount"] == amount
    assert result["price"] == price
    assert result["status"] == "open"
    mock_exchange_client.create_order.assert_called_once_with(symbol, order_type, side, amount, price)

def test_cancel_order(mock_exchange_client):
    """Test canceling an order."""
    # Setup
    order_id = "123456"
    symbol = "BTC/USDT"
    
    mock_exchange_client.cancel_order.return_value = {
        "id": order_id,
        "symbol": symbol,
        "status": "canceled"
    }
    
    # Execute
    result = mock_exchange_client.cancel_order(order_id, symbol)
    
    # Assert
    assert result is not None
    assert result["id"] == order_id
    assert result["symbol"] == symbol
    assert result["status"] == "canceled"
    mock_exchange_client.cancel_order.assert_called_once_with(order_id, symbol)

def test_get_order_status(mock_exchange_client):
    """Test getting order status."""
    # Setup
    order_id = "123456"
    symbol = "BTC/USDT"
    
    mock_exchange_client.get_order_status.return_value = {
        "id": order_id,
        "symbol": symbol,
        "status": "closed",
        "filled": 0.1,
        "remaining": 0,
        "cost": 5000
    }
    
    # Execute
    result = mock_exchange_client.get_order_status(order_id, symbol)
    
    # Assert
    assert result is not None
    assert result["id"] == order_id
    assert result["symbol"] == symbol
    assert result["status"] == "closed"
    assert "filled" in result
    assert "remaining" in result
    assert "cost" in result
    mock_exchange_client.get_order_status.assert_called_once_with(order_id, symbol) 