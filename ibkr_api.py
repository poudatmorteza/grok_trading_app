import requests
import json
import time
import jwt
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IBKRAPI:
    """
    Interactive Brokers Web API client for forex trading
    """
    
    def __init__(self, username: str, password: str, demo: bool = True):
        """
        Initialize IBKR API client
        
        Args:
            username: IBKR username
            password: IBKR password
            demo: Whether to use demo/practice account
        """
        self.username = username
        self.password = password
        self.demo = demo
        
        # API endpoints - using the correct IBKR endpoints
        if demo:
            # For demo/practice accounts, we'll use the regular API with demo credentials
            self.base_url = "https://api.ibkr.com/v1"
        else:
            self.base_url = "https://api.ibkr.com/v1"
            
        # Session management
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        
        # Headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'IBKR-API-Client/1.0'
        })
        
    def _generate_jwt_token(self) -> str:
        """
        Generate JWT token for authentication as per IBKR's private_key_jwt requirement
        """
        # For demo purposes, we'll use a simplified JWT
        # In production, you'd need to use proper private key signing
        payload = {
            'iss': self.username,
            'sub': self.username,
            'aud': self.base_url,
            'iat': int(time.time()),
            'exp': int(time.time()) + 3600,  # 1 hour expiration
            'jti': hashlib.md5(f"{self.username}{time.time()}".encode()).hexdigest()
        }
        
        # This is a simplified implementation
        # In production, you'd need to sign with your private key
        return jwt.encode(payload, 'demo_secret', algorithm='HS256')
    
    def authenticate(self) -> bool:
        """
        Authenticate with IBKR API using OAuth 2.0 with private_key_jwt
        
        Returns:
            bool: True if authentication successful
        """
        try:
            # Generate JWT token
            client_assertion = self._generate_jwt_token()
            
            # OAuth 2.0 token request
            token_url = f"{self.base_url}/oauth/token"
            
            data = {
                'grant_type': 'client_credentials',
                'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
                'client_assertion': client_assertion
            }
            
            response = self.session.post(token_url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                self.refresh_token = token_data.get('refresh_token')
                expires_in = token_data.get('expires_in', 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                # Update session headers with access token
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                
                logger.info("Successfully authenticated with IBKR API")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def _ensure_authenticated(self) -> bool:
        """
        Ensure we have a valid access token, refresh if necessary
        
        Returns:
            bool: True if authenticated
        """
        if not self.access_token:
            return self.authenticate()
        
        # Check if token is expired or about to expire
        if self.token_expires_at and datetime.now() >= self.token_expires_at - timedelta(minutes=5):
            return self._refresh_token()
        
        return True
    
    def _refresh_token(self) -> bool:
        """
        Refresh the access token using refresh token
        
        Returns:
            bool: True if refresh successful
        """
        try:
            if not self.refresh_token:
                return self.authenticate()
            
            token_url = f"{self.base_url}/oauth/token"
            
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token
            }
            
            response = self.session.post(token_url, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get('access_token')
                self.refresh_token = token_data.get('refresh_token')
                expires_in = token_data.get('expires_in', 3600)
                self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                # Update session headers
                self.session.headers.update({
                    'Authorization': f'Bearer {self.access_token}'
                })
                
                logger.info("Successfully refreshed access token")
                return True
            else:
                logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
                return self.authenticate()
                
        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            return self.authenticate()
    
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """
        Get account information
        
        Returns:
            Dict containing account information or None if failed
        """
        if not self._ensure_authenticated():
            return None
        
        try:
            response = self.session.get(f"{self.base_url}/account")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get account info: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting account info: {str(e)}")
            return None
    
    def get_portfolio(self) -> Optional[Dict[str, Any]]:
        """
        Get current portfolio positions
        
        Returns:
            Dict containing portfolio information or None if failed
        """
        if not self._ensure_authenticated():
            return None
        
        try:
            response = self.session.get(f"{self.base_url}/portfolio")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get portfolio: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting portfolio: {str(e)}")
            return None
    
    def get_forex_contracts(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get available forex contracts
        
        Returns:
            List of forex contracts or None if failed
        """
        if not self._ensure_authenticated():
            return None
        
        try:
            # Search for forex contracts
            params = {
                'secType': 'CASH',
                'exchange': 'IDEALPRO'  # IBKR's forex exchange
            }
            
            response = self.session.get(f"{self.base_url}/contracts/search", params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get forex contracts: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting forex contracts: {str(e)}")
            return None
    
    def get_market_data(self, symbol: str, duration: str = "1 D", bar_size: str = "1 min") -> Optional[List[Dict[str, Any]]]:
        """
        Get market data for a forex symbol
        
        Args:
            symbol: Forex symbol (e.g., 'EUR.USD')
            duration: Data duration (e.g., '1 D', '1 W', '1 M')
            bar_size: Bar size (e.g., '1 min', '5 min', '1 hour')
            
        Returns:
            List of market data bars or None if failed
        """
        if not self._ensure_authenticated():
            return None
        
        try:
            params = {
                'symbol': symbol,
                'duration': duration,
                'barSize': bar_size,
                'whatToShow': 'TRADES'
            }
            
            response = self.session.get(f"{self.base_url}/market-data/history", params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get market data: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting market data: {str(e)}")
            return None
    
    def get_forex_rates(self, symbols: List[str] = None) -> Optional[Dict[str, float]]:
        """
        Get current forex rates
        
        Args:
            symbols: List of forex symbols (e.g., ['EUR.USD', 'GBP.USD'])
            
        Returns:
            Dict of symbol to rate mapping or None if failed
        """
        if not self._ensure_authenticated():
            return None
        
        try:
            if symbols is None:
                symbols = ['EUR.USD', 'GBP.USD', 'USD.JPY', 'USD.CHF', 'AUD.USD', 'USD.CAD']
            
            rates = {}
            for symbol in symbols:
                params = {
                    'symbol': symbol,
                    'duration': '1 D',
                    'barSize': '1 min',
                    'whatToShow': 'TRADES'
                }
                
                response = self.session.get(f"{self.base_url}/market-data/history", params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        # Get the latest close price
                        rates[symbol] = float(data[-1].get('close', 0))
                else:
                    logger.warning(f"Failed to get rate for {symbol}: {response.status_code}")
            
            return rates if rates else None
                
        except Exception as e:
            logger.error(f"Error getting forex rates: {str(e)}")
            return None
    
    def place_order(self, symbol: str, action: str, quantity: float, order_type: str = "MKT") -> Optional[Dict[str, Any]]:
        """
        Place a forex order
        
        Args:
            symbol: Forex symbol (e.g., 'EUR.USD')
            action: 'BUY' or 'SELL'
            quantity: Order quantity
            order_type: Order type ('MKT', 'LMT', 'STP', etc.)
            
        Returns:
            Order response or None if failed
        """
        if not self._ensure_authenticated():
            return None
        
        try:
            order_data = {
                'symbol': symbol,
                'secType': 'CASH',
                'exchange': 'IDEALPRO',
                'currency': 'USD',
                'action': action,
                'totalQuantity': quantity,
                'orderType': order_type
            }
            
            response = self.session.post(f"{self.base_url}/order", json=order_data)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to place order: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return None
    
    def get_orders(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get current orders
        
        Returns:
            List of orders or None if failed
        """
        if not self._ensure_authenticated():
            return None
        
        try:
            response = self.session.get(f"{self.base_url}/orders")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get orders: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting orders: {str(e)}")
            return None
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            bool: True if cancellation successful
        """
        if not self._ensure_authenticated():
            return False
        
        try:
            response = self.session.delete(f"{self.base_url}/order/{order_id}")
            
            if response.status_code == 200:
                logger.info(f"Successfully cancelled order {order_id}")
                return True
            else:
                logger.error(f"Failed to cancel order: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error cancelling order: {str(e)}")
            return False
    
    def get_trades(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get trade history
        
        Returns:
            List of trades or None if failed
        """
        if not self._ensure_authenticated():
            return None
        
        try:
            response = self.session.get(f"{self.base_url}/trades")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get trades: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting trades: {str(e)}")
            return None

# Example usage and testing
def test_ibkr_api():
    """
    Test function for IBKR API
    """
    from config import DEMO_USERNAME, DEMO_PASSWORD
    
    # Initialize API client
    ibkr = IBKRAPI(DEMO_USERNAME, DEMO_PASSWORD, demo=True)
    
    # Test authentication
    if ibkr.authenticate():
        print("✅ Authentication successful")
        
        # Test account info
        account_info = ibkr.get_account_info()
        if account_info:
            print("✅ Account info retrieved")
            print(f"Account: {account_info}")
        
        # Test portfolio
        portfolio = ibkr.get_portfolio()
        if portfolio:
            print("✅ Portfolio retrieved")
            print(f"Portfolio: {portfolio}")
        
        # Test forex rates
        rates = ibkr.get_forex_rates(['EUR.USD', 'GBP.USD'])
        if rates:
            print("✅ Forex rates retrieved")
            print(f"Rates: {rates}")
        
        # Test market data
        market_data = ibkr.get_market_data('EUR.USD', duration='1 D', bar_size='1 min')
        if market_data:
            print("✅ Market data retrieved")
            print(f"Data points: {len(market_data)}")
        
    else:
        print("❌ Authentication failed")

if __name__ == "__main__":
    test_ibkr_api() 