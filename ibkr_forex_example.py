#!/usr/bin/env python3
"""
Interactive Brokers Forex Trading Example
Demonstrates how to use the IBKR API module for forex trading
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ibkr_api import IBKRAPI
from config import DEMO_USERNAME, DEMO_PASSWORD
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class IBKRForexTrader:
    """
    Forex trading class using IBKR API
    """
    
    def __init__(self, username: str, password: str, demo: bool = True):
        """
        Initialize the forex trader
        
        Args:
            username: IBKR username
            password: IBKR password
            demo: Whether to use demo account
        """
        self.ibkr = IBKRAPI(username, password, demo)
        self.authenticated = False
        self.account_info = None
        self.portfolio = None
        
    def connect(self) -> bool:
        """
        Connect to IBKR API
        
        Returns:
            bool: True if connection successful
        """
        print("🔗 Connecting to IBKR API...")
        
        try:
            if self.ibkr.authenticate():
                self.authenticated = True
                print("✅ Successfully connected to IBKR API")
                
                # Get account information
                self.account_info = self.ibkr.get_account_info()
                if self.account_info:
                    print(f"📊 Account: {self.account_info.get('accountId', 'N/A')}")
                    print(f"💰 Balance: ${self.account_info.get('balance', 0):,.2f}")
                
                # Get portfolio
                self.portfolio = self.ibkr.get_portfolio()
                if self.portfolio:
                    positions = self.portfolio.get('positions', [])
                    print(f"📈 Active positions: {len(positions)}")
                
                return True
            else:
                print("❌ Failed to connect to IBKR API")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {str(e)}")
            return False
    
    def get_forex_rates(self, symbols: List[str] = None) -> Optional[Dict[str, float]]:
        """
        Get current forex rates
        
        Args:
            symbols: List of forex symbols
            
        Returns:
            Dict of symbol to rate mapping
        """
        if not self.authenticated:
            print("❌ Not authenticated. Please connect first.")
            return None
        
        if symbols is None:
            symbols = ['EUR.USD', 'GBP.USD', 'USD.JPY', 'USD.CHF', 'AUD.USD', 'USD.CAD']
        
        print(f"💱 Getting forex rates for {len(symbols)} symbols...")
        
        try:
            rates = self.ibkr.get_forex_rates(symbols)
            if rates:
                print("✅ Forex rates retrieved:")
                for symbol, rate in rates.items():
                    print(f"  {symbol}: {rate:.4f}")
                return rates
            else:
                print("❌ Failed to retrieve forex rates")
                return None
                
        except Exception as e:
            print(f"❌ Error getting forex rates: {str(e)}")
            return None
    
    def get_market_data(self, symbol: str, duration: str = "1 D", bar_size: str = "1 min") -> Optional[List[Dict]]:
        """
        Get market data for analysis
        
        Args:
            symbol: Forex symbol
            duration: Data duration
            bar_size: Bar size
            
        Returns:
            List of market data bars
        """
        if not self.authenticated:
            print("❌ Not authenticated. Please connect first.")
            return None
        
        print(f"📊 Getting market data for {symbol}...")
        
        try:
            data = self.ibkr.get_market_data(symbol, duration, bar_size)
            if data:
                print(f"✅ Retrieved {len(data)} data points")
                if len(data) > 0:
                    latest = data[-1]
                    print(f"📈 Latest: {latest.get('time', 'N/A')} - Close: {latest.get('close', 'N/A')}")
                return data
            else:
                print("❌ Failed to retrieve market data")
                return None
                
        except Exception as e:
            print(f"❌ Error getting market data: {str(e)}")
            return None
    
    def analyze_forex_pair(self, symbol: str) -> Dict:
        """
        Analyze a forex pair for trading opportunities
        
        Args:
            symbol: Forex symbol to analyze
            
        Returns:
            Analysis results
        """
        print(f"🔍 Analyzing {symbol}...")
        
        # Get market data
        data = self.get_market_data(symbol, duration="1 D", bar_size="5 min")
        if not data or len(data) < 10:
            return {"error": "Insufficient data"}
        
        # Simple analysis (you can enhance this)
        closes = [float(bar.get('close', 0)) for bar in data]
        highs = [float(bar.get('high', 0)) for bar in data]
        lows = [float(bar.get('low', 0)) for bar in data]
        
        current_price = closes[-1]
        avg_price = sum(closes) / len(closes)
        max_high = max(highs)
        min_low = min(lows)
        
        # Calculate simple indicators
        price_change = ((current_price - closes[0]) / closes[0]) * 100
        volatility = (max_high - min_low) / avg_price * 100
        
        analysis = {
            "symbol": symbol,
            "current_price": current_price,
            "average_price": avg_price,
            "price_change_percent": price_change,
            "volatility_percent": volatility,
            "high": max_high,
            "low": min_low,
            "data_points": len(data),
            "trend": "UP" if current_price > avg_price else "DOWN",
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"📊 Analysis for {symbol}:")
        print(f"  Current Price: {current_price:.4f}")
        print(f"  Average Price: {avg_price:.4f}")
        print(f"  Price Change: {price_change:.2f}%")
        print(f"  Volatility: {volatility:.2f}%")
        print(f"  Trend: {analysis['trend']}")
        
        return analysis
    
    def place_forex_order(self, symbol: str, action: str, quantity: float, order_type: str = "MKT") -> bool:
        """
        Place a forex order
        
        Args:
            symbol: Forex symbol
            action: 'BUY' or 'SELL'
            quantity: Order quantity
            order_type: Order type
            
        Returns:
            bool: True if order placed successfully
        """
        if not self.authenticated:
            print("❌ Not authenticated. Please connect first.")
            return False
        
        print(f"📋 Placing {action} order for {quantity} {symbol}...")
        
        try:
            order = self.ibkr.place_order(symbol, action, quantity, order_type)
            if order:
                print(f"✅ Order placed successfully")
                print(f"Order ID: {order.get('orderId', 'N/A')}")
                print(f"Status: {order.get('status', 'N/A')}")
                return True
            else:
                print("❌ Failed to place order")
                return False
                
        except Exception as e:
            print(f"❌ Error placing order: {str(e)}")
            return False
    
    def get_order_status(self) -> List[Dict]:
        """
        Get current order status
        
        Returns:
            List of orders
        """
        if not self.authenticated:
            print("❌ Not authenticated. Please connect first.")
            return []
        
        try:
            orders = self.ibkr.get_orders()
            if orders:
                print(f"📋 Found {len(orders)} active orders:")
                for order in orders:
                    print(f"  Order ID: {order.get('orderId', 'N/A')}")
                    print(f"  Symbol: {order.get('symbol', 'N/A')}")
                    print(f"  Action: {order.get('action', 'N/A')}")
                    print(f"  Status: {order.get('status', 'N/A')}")
                    print("  ---")
            else:
                print("📋 No active orders found")
            
            return orders or []
            
        except Exception as e:
            print(f"❌ Error getting orders: {str(e)}")
            return []
    
    def monitor_forex_pairs(self, symbols: List[str], interval: int = 60):
        """
        Monitor forex pairs continuously
        
        Args:
            symbols: List of symbols to monitor
            interval: Monitoring interval in seconds
        """
        if not self.authenticated:
            print("❌ Not authenticated. Please connect first.")
            return
        
        print(f"👀 Starting forex monitoring for {len(symbols)} pairs...")
        print(f"⏱️  Update interval: {interval} seconds")
        print("Press Ctrl+C to stop monitoring")
        
        try:
            while True:
                print(f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("-" * 40)
                
                # Get current rates
                rates = self.get_forex_rates(symbols)
                if rates:
                    for symbol, rate in rates.items():
                        print(f"  {symbol}: {rate:.4f}")
                
                # Wait for next update
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n⏹️  Monitoring stopped by user")
        except Exception as e:
            print(f"❌ Monitoring error: {str(e)}")

def main():
    """
    Main example function
    """
    print("🏦 IBKR Forex Trading Example")
    print("=" * 40)
    
    # Initialize trader
    trader = IBKRForexTrader(DEMO_USERNAME, DEMO_PASSWORD, demo=True)
    
    # Connect to IBKR
    if not trader.connect():
        print("❌ Cannot proceed without connection")
        return
    
    # Example 1: Get forex rates
    print("\n" + "=" * 40)
    print("Example 1: Getting Forex Rates")
    print("=" * 40)
    
    symbols = ['EUR.USD', 'GBP.USD', 'USD.JPY']
    rates = trader.get_forex_rates(symbols)
    
    # Example 2: Analyze a forex pair
    print("\n" + "=" * 40)
    print("Example 2: Analyzing Forex Pair")
    print("=" * 40)
    
    analysis = trader.analyze_forex_pair('EUR.USD')
    
    # Example 3: Check order status
    print("\n" + "=" * 40)
    print("Example 3: Checking Orders")
    print("=" * 40)
    
    orders = trader.get_order_status()
    
    # Example 4: Monitor forex pairs (commented out for safety)
    print("\n" + "=" * 40)
    print("Example 4: Forex Monitoring (Demo)")
    print("=" * 40)
    print("To start monitoring, uncomment the following line:")
    print("# trader.monitor_forex_pairs(['EUR.USD', 'GBP.USD'], interval=30)")
    
    print("\n✅ IBKR Forex Trading Example Completed!")
    print("=" * 40)

if __name__ == "__main__":
    main() 