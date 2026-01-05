"""
Hyperliquid API Example - Fetch Vaults and Leaderboard Data

This script demonstrates how to fetch vaults data and create leaderboard rankings
from Hyperliquid API using the requests library.

NOTE: Hyperliquid does not have a public "leaderboard" API endpoint. However,
we can create leaderboard-style rankings by:
1. Fetching vault details (which includes follower performance data)
2. Fetching user portfolio data for specific addresses
3. Aggregating and ranking the data by PnL, ROI, or volume
"""

import requests
import json
import time
import os
import sys
import threading
from datetime import datetime
from typing import Dict, List, Any


class Colors:
    """ANSI color codes for terminal output"""
    # Text colors
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    
    # Styles
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    # Reset
    RESET = '\033[0m'
    
    @staticmethod
    def green(text):
        return f"{Colors.GREEN}{text}{Colors.RESET}"
    
    @staticmethod
    def red(text):
        return f"{Colors.RED}{text}{Colors.RESET}"
    
    @staticmethod
    def yellow(text):
        return f"{Colors.YELLOW}{text}{Colors.RESET}"
    
    @staticmethod
    def bold(text):
        return f"{Colors.BOLD}{text}{Colors.RESET}"
    
    @staticmethod
    def bold_yellow(text):
        return f"{Colors.BOLD}{Colors.YELLOW}{text}{Colors.RESET}"
    
    @staticmethod
    def cyan(text):
        return f"{Colors.CYAN}{text}{Colors.RESET}"


class InteractiveDashboard:
    """Manages interactive controls and alerts for live monitoring"""
    
    def __init__(self):
        self.running = True
        self.refresh_interval = 5
        self.top_n = 10
        self.sort_by = 'pnl'
        self.min_equity = None
        self.min_roi = None
        self.alert_pnl_above = None
        self.alert_pnl_below = None
        self.alert_tvl_above = None
        self.previous_values = {}  # Track previous values for alerts
        self.show_help = False
        
    def check_alerts(self, leaderboard: List[Dict[str, Any]], vault_data: Dict[str, Any]):
        """Check for alert conditions and display notifications"""
        alerts = []
        
        # Check PnL alerts for each follower
        if self.alert_pnl_above is not None or self.alert_pnl_below is not None:
            for follower in leaderboard:
                user = follower.get('user')
                pnl = float(follower.get('allTimePnl', 0))
                
                # Check if we have previous value
                prev_pnl = self.previous_values.get(f"pnl_{user}")
                
                if self.alert_pnl_above and pnl >= self.alert_pnl_above:
                    if prev_pnl is None or prev_pnl < self.alert_pnl_above:
                        alerts.append(
                            f"🔔 {Colors.green('ALERT')}: User {user[:12]}... PnL crossed ${self.alert_pnl_above:,.2f} (now ${pnl:,.2f})"
                        )
                
                if self.alert_pnl_below and pnl <= self.alert_pnl_below:
                    if prev_pnl is None or prev_pnl > self.alert_pnl_below:
                        alerts.append(
                            f"🔔 {Colors.red('ALERT')}: User {user[:12]}... PnL dropped below ${self.alert_pnl_below:,.2f} (now ${pnl:,.2f})"
                        )
                
                # Update previous value
                self.previous_values[f"pnl_{user}"] = pnl
        
        # Check TVL alert
        if self.alert_tvl_above and vault_data:
            # Calculate total TVL from all followers
            tvl = sum(float(f.get('vaultEquity', 0)) for f in leaderboard)
            prev_tvl = self.previous_values.get('tvl')
            
            if tvl >= self.alert_tvl_above:
                if prev_tvl is None or prev_tvl < self.alert_tvl_above:
                    alerts.append(
                        f"🔔 {Colors.yellow('ALERT')}: Vault TVL crossed ${self.alert_tvl_above:,.2f} (now ${tvl:,.2f})"
                    )
            
            self.previous_values['tvl'] = tvl
        
        # Display alerts
        if alerts:
            print("\n" + "="*80)
            for alert in alerts:
                print(alert)
            print("="*80 + "\n")
    
    def handle_input(self):
        """Handle keyboard input in separate thread"""
        print("\n📋 Interactive Controls:")
        print("  Press 'h' - Show help")
        print("  Press 'q' - Quit")
        print("  Press 'i' - Change refresh interval")
        print("  Press 's' - Change sort order")
        print("  Press 't' - Change top N")
        print("  Press 'e' - Set min equity filter")
        print("  Press 'r' - Set min ROI filter")
        print("  Press 'c' - Clear all filters\n")
        
        while self.running:
            try:
                # This is a simple approach - in production, use proper input handling
                user_input = input(">> ").strip().lower()
                
                if user_input == 'q':
                    print("\n✅ Stopping dashboard...")
                    self.running = False
                    break
                
                elif user_input == 'h':
                    self.print_help()
                
                elif user_input == 'i':
                    try:
                        new_interval = int(input("Enter new refresh interval (seconds): "))
                        if new_interval > 0:
                            self.refresh_interval = new_interval
                            print(f"✓ Refresh interval set to {new_interval}s")
                    except ValueError:
                        print("❌ Invalid interval")
                
                elif user_input == 's':
                    print("Sort options: pnl, roi, equity, days")
                    new_sort = input("Enter sort option: ").strip().lower()
                    if new_sort in ['pnl', 'roi', 'equity', 'days']:
                        self.sort_by = new_sort
                        print(f"✓ Sorting by {new_sort.upper()}")
                    else:
                        print("❌ Invalid sort option")
                
                elif user_input == 't':
                    try:
                        new_top = int(input("Enter number of top performers to show: "))
                        if new_top > 0:
                            self.top_n = new_top
                            print(f"✓ Showing top {new_top}")
                    except ValueError:
                        print("❌ Invalid number")
                
                elif user_input == 'e':
                    try:
                        new_equity = float(input("Enter minimum equity (0 to clear): "))
                        self.min_equity = new_equity if new_equity > 0 else None
                        if self.min_equity:
                            print(f"✓ Min equity filter set to ${self.min_equity:,.2f}")
                        else:
                            print("✓ Min equity filter cleared")
                    except ValueError:
                        print("❌ Invalid equity value")
                
                elif user_input == 'r':
                    try:
                        new_roi = float(input("Enter minimum ROI % (0 to clear): "))
                        self.min_roi = new_roi if new_roi > 0 else None
                        if self.min_roi:
                            print(f"✓ Min ROI filter set to {self.min_roi:.2f}%")
                        else:
                            print("✓ Min ROI filter cleared")
                    except ValueError:
                        print("❌ Invalid ROI value")
                
                elif user_input == 'c':
                    self.min_equity = None
                    self.min_roi = None
                    print("✓ All filters cleared")
                
            except EOFError:
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def print_help(self):
        """Print interactive help"""
        print("\n" + "="*80)
        print(Colors.bold("Interactive Dashboard Commands:"))
        print("="*80)
        print("  h - Show this help")
        print("  q - Quit dashboard")
        print("  i - Change refresh interval")
        print("  s - Change sort order (pnl, roi, equity, days)")
        print("  t - Change number of top performers displayed")
        print("  e - Set minimum equity filter")
        print("  r - Set minimum ROI filter")
        print("  c - Clear all filters")
        print("="*80 + "\n")


class HyperliquidAPI:
    """Client for interacting with the Hyperliquid API"""
    
    def __init__(self, base_url: str = "https://api.hyperliquid.xyz/info"):
        self.base_url = base_url
    
    def _post_request(self, payload: Dict[str, Any]) -> Any:
        """
        Make a POST request to the Hyperliquid API
        
        Args:
            payload: The request payload
            
        Returns:
            The JSON response from the API
        """
        try:
            response = requests.post(self.base_url, json=payload, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            return None
    
    def get_vault_details(self, vault_address: str, user: str = None, limit: int = None) -> Dict[str, Any]:
        """
        Fetch vault details from Hyperliquid API
        
        Args:
            vault_address: Vault address to get specific vault details
            user: Optional user address to filter by
            limit: Optional limit for number of followers to fetch
            
        Returns:
            Vault details dictionary including name, leader, APR, followers, etc.
        """
        payload = {
            "type": "vaultDetails",
            "vaultAddress": vault_address
        }
        
        if user:
            payload["user"] = user
        
        # Try adding limit parameter (might not be supported by API)
        if limit:
            payload["limit"] = limit
        
        print(f"Fetching vault details for {vault_address}...")
        if limit:
            print(f"Requesting limit: {limit} followers...")
        
        data = self._post_request(payload)
        
        return data if data else {}
    
    def get_vault_details_batched(self, vault_address: str, target_followers: int = 2000, batch_size: int = 100) -> Dict[str, Any]:
        """
        Fetch vault details with persistent storage to accumulate followers across requests
        
        This function attempts multiple strategies to retrieve more followers:
        1. Makes repeated requests to catch any API updates
        2. Stores followers persistently across dashboard runs
        3. Gradually builds up to 2000+ unique followers over time
        
        Args:
            vault_address: Vault address to get specific vault details
            target_followers: Target number of followers to retrieve (default: 2000)
            batch_size: Number of followers per batch (default: 100)
            
        Returns:
            Vault details dictionary with merged followers from cache and new requests
        """
        import json
        import os
        from pathlib import Path
        
        # Create cache directory
        cache_dir = Path("vault_cache")
        cache_dir.mkdir(exist_ok=True)
        cache_file = cache_dir / f"{vault_address}_followers.json"
        
        # Load previously cached followers
        all_followers = {}
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                    all_followers = {f['user']: f for f in cached_data.get('followers', [])}
                    print(f"[CACHE] Loaded {len(all_followers)} followers from cache")
            except Exception as e:
                print(f"[CACHE] Failed to load cache: {e}")
        
        num_batches = min(20, (target_followers - len(all_followers) + batch_size - 1) // batch_size)
        if num_batches <= 0:
            num_batches = 1
            
        print(f"\n{'='*80}")
        print(f"Fetching vault details - Target: {target_followers} followers")
        print(f"Current cached: {len(all_followers)} | Need: {max(0, target_followers - len(all_followers))}")
        print(f"Making {num_batches} API requests...")
        print(f"{'='*80}\n")
        
        vault_data = None
        requests_made = 0
        new_followers_found = 0
        
        for batch_num in range(num_batches):
            # Try multiple request strategies
            strategies = [
                {"type": "vaultDetails", "vaultAddress": vault_address},  # Basic request
                {"type": "vaultDetails", "vaultAddress": vault_address, "limit": batch_size},  # With limit
                {"type": "vaultDetails", "vaultAddress": vault_address, "offset": batch_num * batch_size, "limit": batch_size},  # With offset
            ]
            
            strategy_idx = batch_num % len(strategies)
            payload = strategies[strategy_idx]
            
            print(f"[Request {batch_num + 1}/{num_batches}] Strategy {strategy_idx + 1}: {list(payload.keys())}")
            
            data = self._post_request(payload)
            requests_made += 1
            
            if not data:
                print(f"   [FAILED]")
                continue
            
            # Store vault metadata from first successful response
            if vault_data is None:
                vault_data = {k: v for k, v in data.items() if k != 'followers'}
            
            # Merge followers
            if 'followers' in data:
                followers = data['followers']
                new_count = 0
                for follower in followers:
                    user_addr = follower.get('user')
                    if user_addr and user_addr not in all_followers:
                        all_followers[user_addr] = follower
                        new_count += 1
                        new_followers_found += 1
                
                total_unique = len(all_followers)
                print(f"   [SUCCESS] Received: {len(followers)} | New: {new_count} | Total: {total_unique}")
                
                # If no new followers after 3 consecutive requests, stop
                if batch_num >= 2 and new_count == 0:
                    print(f"\n   [INFO] No new followers in last {batch_num + 1} requests.")
                    print(f"   [INFO] API limit reached. Current total: {total_unique} followers")
                    break
            else:
                print(f"   [WARNING] No followers in response")
            
            # Small delay between requests
            if batch_num < num_batches - 1:
                import time
                time.sleep(0.3)
        
        # Save to cache
        if vault_data and all_followers:
            try:
                cache_data = {
                    'vault_address': vault_address,
                    'followers': list(all_followers.values()),
                    'cached_at': str(datetime.now())
                }
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, indent=2)
                print(f"\n[CACHE] Saved {len(all_followers)} followers to cache")
            except Exception as e:
                print(f"[CACHE] Failed to save cache: {e}")
        
        # Combine vault data with all unique followers
        if vault_data:
            vault_data['followers'] = list(all_followers.values())
            print(f"\n{'='*80}")
            print(f"[COMPLETE] Total unique followers: {len(all_followers)}")
            print(f"[COMPLETE] New followers this session: {new_followers_found}")
            print(f"[COMPLETE] API requests made: {requests_made}")
            if len(all_followers) >= target_followers:
                print(f"[SUCCESS] Target of {target_followers} followers reached!")
            else:
                print(f"[INFO] Progress: {len(all_followers)}/{target_followers} ({len(all_followers)*100//target_followers}%)")
                print(f"[INFO] Note: Run dashboard multiple times to accumulate more followers")
            print(f"{'='*80}\n")
            return vault_data
        
        return {}
    
    def get_user_portfolio(self, user_address: str) -> List[List]:
        """
        Fetch user portfolio/performance data which includes PnL metrics
        
        Args:
            user_address: User's wallet address
            
        Returns:
            Portfolio data with PnL history, volume, and account value over different periods
        """
        payload = {
            "type": "portfolio",
            "user": user_address
        }
        
        print(f"Fetching portfolio data for {user_address}...")
        data = self._post_request(payload)
        
        return data if data else []
    
    def get_user_vault_equities(self, user_address: str) -> List[Dict[str, Any]]:
        """
        Fetch a user's vault deposit information
        
        Args:
            user_address: User's wallet address
            
        Returns:
            List of vault equities/deposits for the user
        """
        payload = {
            "type": "userVaultEquities",
            "user": user_address
        }
        
        print(f"Fetching vault equities for {user_address}...")
        data = self._post_request(payload)
        
        return data if data else []
    
    def get_vault_leaderboard(self, vault_address: str, sort_by: str = 'pnl', 
                              min_equity: float = None, min_roi: float = None,
                              use_batched: bool = False, target_followers: int = 2000) -> List[Dict[str, Any]]:
        """
        Create a leaderboard from vault follower data with sorting and filtering
        
        Args:
            vault_address: The vault address to get followers from
            sort_by: Sort metric ('pnl', 'roi', 'equity', 'days')
            min_equity: Minimum equity filter
            min_roi: Minimum ROI filter (in percentage)
            use_batched: Whether to use batched requests to try fetching more followers
            target_followers: Target number of followers when using batched mode
            
        Returns:
            List of follower data sorted by performance metrics
        """
        if use_batched:
            vault_data = self.get_vault_details_batched(vault_address, target_followers=target_followers)
        else:
            vault_data = self.get_vault_details(vault_address)
        
        if not vault_data or 'followers' not in vault_data:
            print("No follower data available for this vault")
            return []
        
        followers = vault_data['followers']
        print(f"Creating leaderboard from {len(followers)} vault followers...")
        
        # Apply filters
        filtered_followers = followers
        
        if min_equity is not None:
            filtered_followers = [
                f for f in filtered_followers 
                if float(f.get('vaultEquity', 0)) >= min_equity
            ]
            print(f"Filtered to {len(filtered_followers)} followers with equity >= ${min_equity:,.2f}")
        
        if min_roi is not None:
            def calc_roi(follower):
                equity = float(follower.get('vaultEquity', 0))
                pnl = float(follower.get('allTimePnl', 0))
                if equity > 0:
                    return (pnl / equity) * 100
                return 0
            
            filtered_followers = [
                f for f in filtered_followers 
                if calc_roi(f) >= min_roi
            ]
            print(f"Filtered to {len(filtered_followers)} followers with ROI >= {min_roi:.2f}%")
        
        # Sort by specified metric
        sort_keys = {
            'pnl': lambda x: float(x.get('allTimePnl', 0)),
            'roi': lambda x: (float(x.get('allTimePnl', 0)) / float(x.get('vaultEquity', 1))) * 100 if float(x.get('vaultEquity', 0)) > 0 else 0,
            'equity': lambda x: float(x.get('vaultEquity', 0)),
            'days': lambda x: int(x.get('daysFollowing', 0))
        }
        
        sort_key = sort_keys.get(sort_by.lower(), sort_keys['pnl'])
        sorted_followers = sorted(filtered_followers, key=sort_key, reverse=True)
        
        return sorted_followers
    
    def get_meta(self) -> Dict[str, Any]:
        """
        Fetch exchange metadata including all available perpetuals
        
        Returns:
            Dictionary with universe of available assets
        """
        payload = {"type": "meta"}
        print("Fetching exchange metadata...")
        data = self._post_request(payload)
        return data if data else {}


def format_vault_data(vault: Dict[str, Any]) -> str:
    """Format vault data for display with colors"""
    name = vault.get('name', 'N/A')
    leader = vault.get('leader', 'N/A')
    vault_address = vault.get('vaultAddress', 'N/A')
    apr = vault.get('apr', 'N/A')
    max_withdrawable = vault.get('maxWithdrawable', 'N/A')
    
    # Format APR with color
    if isinstance(apr, str):
        apr_str = apr
    elif apr != 'N/A':
        apr_percent = apr * 100
        apr_formatted = f'{apr_percent:.2f}%'
        apr_str = Colors.green(apr_formatted) if apr > 0 else Colors.red(apr_formatted)
    else:
        apr_str = 'N/A'
    
    # Format max withdrawable
    if isinstance(max_withdrawable, str):
        max_with_str = max_withdrawable
    elif max_withdrawable != 'N/A':
        max_with_str = f'${float(max_withdrawable):,.2f}'
    else:
        max_with_str = 'N/A'
    
    return f"""
Vault: {Colors.bold(name)}
Address: {Colors.cyan(vault_address)}
Leader: {leader}
APR: {apr_str}
Max Withdrawable: {max_with_str}
"""


def format_leaderboard_entry(entry: Dict[str, Any], rank: int) -> str:
    """Format leaderboard entry for display with colors and highlights for top 3"""
    user = entry.get('user', 'Anonymous')[:10] + '...'
    vault_equity = entry.get('vaultEquity', 'N/A')
    current_pnl = entry.get('pnl', 'N/A')
    all_time_pnl = entry.get('allTimePnl', 'N/A')
    days_following = entry.get('daysFollowing', 'N/A')
    
    # Calculate ROI if we have the data
    roi = "N/A"
    if vault_equity != 'N/A' and all_time_pnl != 'N/A':
        try:
            equity_val = float(vault_equity)
            pnl_val = float(all_time_pnl)
            if equity_val > 0:
                roi_value = (pnl_val / equity_val) * 100
                roi_formatted = f"{roi_value:.2f}%"
                roi = Colors.green(roi_formatted) if roi_value >= 0 else Colors.red(roi_formatted)
        except:
            pass
    
    # Format equity (neutral color)
    equity_str = f"${float(vault_equity):,.2f}" if vault_equity != 'N/A' else vault_equity
    
    # Format PnL values with colors
    if current_pnl != 'N/A':
        pnl_val = float(current_pnl)
        pnl_formatted = f"${pnl_val:,.2f}"
        current_pnl_str = Colors.green(pnl_formatted) if pnl_val >= 0 else Colors.red(pnl_formatted)
    else:
        current_pnl_str = current_pnl
    
    if all_time_pnl != 'N/A':
        all_pnl_val = float(all_time_pnl)
        all_pnl_formatted = f"${all_pnl_val:,.2f}"
        all_time_pnl_str = Colors.green(all_pnl_formatted) if all_pnl_val >= 0 else Colors.red(all_pnl_formatted)
    else:
        all_time_pnl_str = all_time_pnl
    
    # Highlight top 3 with bold yellow and medals
    if rank <= 3:
        medals = ["🥇", "🥈", "🥉"]
        medal = medals[rank - 1]
        rank_display = Colors.bold_yellow(f"{medal} {rank}.")
        user_display = Colors.bold_yellow(user)
    else:
        rank_display = f"{rank}."
        user_display = user
    
    return f"""
{rank_display} User: {user_display}
   Current Equity: {equity_str}
   Current PnL: {current_pnl_str}
   All-Time PnL: {all_time_pnl_str}
   ROI: {roi}
   Days Following: {days_following}
"""


def format_portfolio_data(portfolio: List, period_name: str = None) -> str:
    """Format portfolio/performance data for display"""
    if not portfolio:
        return "No portfolio data available"
    
    result = []
    for period_data in portfolio:
        if len(period_data) == 2:
            period, data = period_data
            if period_name and period != period_name:
                continue
            
            pnl_history = data.get('pnlHistory', [])
            vlm = data.get('vlm', 'N/A')
            
            result.append(f"\nPeriod: {Colors.bold(period)}")
            
            # Format volume
            if isinstance(vlm, str):
                vlm_str = vlm
            else:
                vlm_value = float(vlm)
                vlm_str = f"${vlm_value:,.2f}"
            result.append(f"Volume: {vlm_str}")
            
            if pnl_history and len(pnl_history) > 0:
                latest_pnl = pnl_history[-1][1] if len(pnl_history[-1]) > 1 else 'N/A'
                
                # Format PnL with color
                if isinstance(latest_pnl, str):
                    pnl_str = latest_pnl
                else:
                    pnl_value = float(latest_pnl)
                    pnl_formatted = f"${pnl_value:,.2f}"
                    pnl_str = Colors.green(pnl_formatted) if pnl_value >= 0 else Colors.red(pnl_formatted)
                
                result.append(f"Latest PnL: {pnl_str}")
    
    return '\n'.join(result) if result else "No data for specified period"


def main():
    """Main function to demonstrate API usage"""
    
    # Initialize the API client
    api = HyperliquidAPI()
    
    print("=" * 70)
    print("Hyperliquid API - Vaults & Leaderboard Data")
    print("=" * 70)
    print()
    
    # HLP Vault address (mainnet) - contains follower performance data
    hlp_vault = "0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"
    
    # Example 1: Fetch vault details
    print("\n--- Example 1: Fetch Vault Details (HLP) ---")
    vault_data = api.get_vault_details(vault_address=hlp_vault)
    
    if vault_data:
        print(format_vault_data(vault_data))
        if 'followers' in vault_data:
            print(f"Total Followers: {len(vault_data['followers'])}")
    
    print("\n" + "=" * 70 + "\n")
    
    # Example 2: Create Leaderboard from Vault Followers
    print("\n--- Example 2: Vault Follower Leaderboard (Top 10 by All-Time PnL) ---")
    leaderboard = api.get_vault_leaderboard(hlp_vault)
    
    if leaderboard:
        print(f"\nShowing top 10 performers out of {len(leaderboard)} total followers:\n")
        for i, entry in enumerate(leaderboard[:10], 1):
            print(format_leaderboard_entry(entry, i))
    else:
        print("No leaderboard data available")
    
    print("\n" + "=" * 70 + "\n")
    
    # Example 3: Fetch specific user portfolio data
    example_user = "0x010461c14e146ac35fe42271bdc1134ee31c703a"
    
    print(f"\n--- Example 3: Individual User Portfolio ({example_user[:10]}...) ---")
    portfolio = api.get_user_portfolio(example_user)
    
    if portfolio:
        print(format_portfolio_data(portfolio, "allTime"))
        print(format_portfolio_data(portfolio, "day"))
    
    print("\n" + "=" * 70)
    print("Example complete!")
    print("\nNote: The 'leaderboard' is created from vault follower data.")
    print("Hyperliquid does not have a direct leaderboard API endpoint.")
    print("=" * 70)


def clear_screen():
    """Clear the terminal screen (works on Windows, Linux, macOS)"""
    os.system('cls' if os.name == 'nt' else 'clear')


def display_live_leaderboard(api: HyperliquidAPI, vault_address: str, top_n: int = 10,
                            sort_by: str = 'pnl', min_equity: float = None, min_roi: float = None):
    """
    Display live leaderboard data with current timestamp
    
    Args:
        api: HyperliquidAPI instance
        vault_address: Vault address to monitor
        top_n: Number of top performers to display
        sort_by: Sort metric ('pnl', 'roi', 'equity', 'days')
        min_equity: Minimum equity filter
        min_roi: Minimum ROI filter
    """
    leaderboard = api.get_vault_leaderboard(vault_address, sort_by, min_equity, min_roi)
    
    if not leaderboard:
        print("❌ Unable to fetch leaderboard data")
        return False
    
    # Display header with timestamp
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("=" * 80)
    print(Colors.bold(f"🏆  HYPERLIQUID VAULT LEADERBOARD - LIVE MONITOR"))
    print(f"📊  HLP Vault: {Colors.cyan(vault_address)}")
    print(f"⏰  Last Updated: {Colors.yellow(now)}")
    print(f"👥  Total Followers: {Colors.bold(str(len(leaderboard)))} | Showing Top {Colors.bold(str(top_n))}")
    print("=" * 80)
    print()
    
    # Display top performers
    for i, entry in enumerate(leaderboard[:top_n], 1):
        print(format_leaderboard_entry(entry, i))
    
    print("\n" + "=" * 80)
    print("Press Ctrl+C to stop monitoring")
    print("=" * 80)
    
    return True


def display_live_leaderboard_simple(leaderboard: List[Dict[str, Any]], vault_address: str, 
                                   top_n: int = 10, sort_by: str = 'pnl'):
    """
    Simplified leaderboard display for interactive mode
    
    Args:
        leaderboard: Pre-fetched and sorted leaderboard data
        vault_address: Vault address being monitored
        top_n: Number of top performers to display
        sort_by: Current sort metric
    """
    if not leaderboard:
        return False
    
    # Display header with timestamp
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("\n" + "=" * 80)
    print(Colors.bold(f"🏆  HYPERLIQUID VAULT LEADERBOARD - LIVE MONITOR"))
    print(f"📊  Vault: {Colors.cyan(vault_address)}")
    print(f"⏰  Updated: {Colors.yellow(now)} | Sorting: {Colors.bold(sort_by.upper())}")
    print(f"👥  Total: {Colors.bold(str(len(leaderboard)))} | Showing: {Colors.bold(str(min(top_n, len(leaderboard))))}")
    print("=" * 80)
    print()
    
    # Display top performers
    for i, entry in enumerate(leaderboard[:top_n], 1):
        print(format_leaderboard_entry(entry, i))
    
    print("=" * 80)
    print(f"📋 Press 'h' for help | 'q' to quit")
    print("=" * 80)
    
    return True


def live_monitor(vault_address: str, refresh_interval: int = 5, top_n: int = 10,
                sort_by: str = 'pnl', min_equity: float = None, min_roi: float = None,
                alert_pnl_above: float = None, alert_pnl_below: float = None,
                alert_tvl_above: float = None, interactive: bool = True):
    """
    Live monitoring mode - continuously refresh leaderboard data with interactive controls
    
    Args:
        vault_address: Vault address to monitor
        refresh_interval: Seconds between refreshes (default: 5)
        top_n: Number of top performers to display (default: 10)
        sort_by: Sort metric ('pnl', 'roi', 'equity', 'days')
        min_equity: Minimum equity filter
        min_roi: Minimum ROI filter (in percentage)
        alert_pnl_above: Alert when PnL goes above this value
        alert_pnl_below: Alert when PnL goes below this value
        alert_tvl_above: Alert when total TVL goes above this value
        interactive: Enable interactive controls (default: True)
    """
    api = HyperliquidAPI()
    dashboard = InteractiveDashboard()
    
    # Initialize dashboard settings
    dashboard.refresh_interval = refresh_interval
    dashboard.top_n = top_n
    dashboard.sort_by = sort_by
    dashboard.min_equity = min_equity
    dashboard.min_roi = min_roi
    dashboard.alert_pnl_above = alert_pnl_above
    dashboard.alert_pnl_below = alert_pnl_below
    dashboard.alert_tvl_above = alert_tvl_above
    
    print(f"\n🚀 Starting live monitor...")
    print(f"📊 Monitoring vault: {Colors.cyan(vault_address)}")
    
    if interactive:
        # Start input handler in separate thread
        input_thread = threading.Thread(target=dashboard.handle_input, daemon=True)
        input_thread.start()
    
    print(f"\n⚙️  Initial Settings:")
    print(f"  📡 Refresh interval: {refresh_interval}s")
    print(f"  📊 Sort by: {sort_by.upper()}")
    print(f"  🔝 Top: {top_n}")
    if min_equity:
        print(f"  💰 Min Equity: ${min_equity:,.2f}")
    if min_roi:
        print(f"  📈 Min ROI: {min_roi:.2f}%")
    if alert_pnl_above:
        print(f"  🔔 Alert PnL Above: ${alert_pnl_above:,.2f}")
    if alert_pnl_below:
        print(f"  🔔 Alert PnL Below: ${alert_pnl_below:,.2f}")
    if alert_tvl_above:
        print(f"  🔔 Alert TVL Above: ${alert_tvl_above:,.2f}")
    print()
    time.sleep(2)
    
    try:
        while dashboard.running:
            # Use current dashboard settings
            leaderboard = api.get_vault_leaderboard(
                vault_address, 
                dashboard.sort_by, 
                dashboard.min_equity, 
                dashboard.min_roi
            )
            
            if not leaderboard:
                print("\n⚠️  Error fetching data. Retrying in 10 seconds...")
                time.sleep(10)
                continue
            
            # Get vault data for alerts
            vault_data = api.get_vault_details(vault_address)
            
            # Check alerts
            dashboard.check_alerts(leaderboard, vault_data)
            
            # Display leaderboard
            success = display_live_leaderboard_simple(
                leaderboard, 
                vault_address, 
                dashboard.top_n, 
                dashboard.sort_by
            )
            
            if not success:
                print("\n⚠️  Error displaying data. Retrying...")
                time.sleep(5)
                continue
            
            # Wait for next refresh using dashboard interval
            time.sleep(dashboard.refresh_interval)
            
    except KeyboardInterrupt:
        dashboard.running = False
        print("\n✅ Live monitoring stopped.")
        print("Thanks for using Hyperliquid Leaderboard Monitor!\n")
        sys.exit(0)


if __name__ == "__main__":
    # Show help message
    if "--help" in sys.argv or "-h" in sys.argv:
        print("""
Hyperliquid Vault Leaderboard Monitor

Usage:
    python hyperliquid_api_example.py [OPTIONS]

Options:
    --live, -l              Enable live monitoring mode (auto-refresh)
    --interval <seconds>    Refresh interval in seconds (default: 5)
    --top <number>          Number of top performers to display (default: 10)
    --sort-by <metric>      Sort by: pnl, roi, equity, days (default: pnl)
    --vault <address>       Monitor specific vault address
    --min-equity <amount>   Filter followers with minimum equity
    --min-roi <percent>     Filter followers with minimum ROI percentage
    --alert-pnl-above <amount>    Alert when PnL goes above this value
    --alert-pnl-below <amount>    Alert when PnL goes below this value
    --alert-tvl-above <amount>    Alert when total TVL goes above this value
    --no-interactive        Disable interactive controls
    --help, -h              Show this help message

Interactive Controls (when live monitoring):
    h - Show help
    q - Quit
    i - Change refresh interval
    s - Change sort order
    t - Change top N
    e - Set min equity filter
    r - Set min ROI filter
    c - Clear all filters

Examples:
    # Run one-time fetch and display
    python hyperliquid_api_example.py

    # Live monitor with interactive controls
    python hyperliquid_api_example.py --live

    # Monitor with alerts for high PnL performers
    python hyperliquid_api_example.py --live --alert-pnl-above 1000000

    # Alert when vault TVL exceeds $10M
    python hyperliquid_api_example.py --live --alert-tvl-above 10000000

    # Combined: Monitor whales with alerts
    python hyperliquid_api_example.py --live --min-equity 1000000 --alert-pnl-above 500000
        """)
        sys.exit(0)
    
    # Check for live mode flag
    if "--live" in sys.argv or "-l" in sys.argv:
        # HLP Vault address (default)
        hlp_vault = "0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"
        
        # Parse vault address if provided
        if "--vault" in sys.argv:
            try:
                idx = sys.argv.index("--vault")
                hlp_vault = sys.argv[idx + 1]
            except IndexError:
                print("⚠️  No vault address provided, using default HLP vault")
        
        # Parse refresh interval if provided
        refresh_interval = 5
        if "--interval" in sys.argv:
            try:
                idx = sys.argv.index("--interval")
                refresh_interval = int(sys.argv[idx + 1])
            except (IndexError, ValueError):
                print("⚠️  Invalid interval value, using default: 5 seconds")
        
        # Parse top N if provided
        top_n = 10
        if "--top" in sys.argv:
            try:
                idx = sys.argv.index("--top")
                top_n = int(sys.argv[idx + 1])
            except (IndexError, ValueError):
                print("⚠️  Invalid top value, using default: 10")
        
        # Parse sort-by if provided
        sort_by = 'pnl'
        if "--sort-by" in sys.argv:
            try:
                idx = sys.argv.index("--sort-by")
                sort_by = sys.argv[idx + 1].lower()
                if sort_by not in ['pnl', 'roi', 'equity', 'days']:
                    print(f"⚠️  Invalid sort option '{sort_by}', using default: pnl")
                    sort_by = 'pnl'
            except IndexError:
                print("⚠️  No sort option provided, using default: pnl")
        
        # Parse min equity if provided
        min_equity = None
        if "--min-equity" in sys.argv:
            try:
                idx = sys.argv.index("--min-equity")
                min_equity = float(sys.argv[idx + 1])
            except (IndexError, ValueError):
                print("⚠️  Invalid min-equity value, filter disabled")
        
        # Parse min ROI if provided
        min_roi = None
        if "--min-roi" in sys.argv:
            try:
                idx = sys.argv.index("--min-roi")
                min_roi = float(sys.argv[idx + 1])
            except (IndexError, ValueError):
                print("⚠️  Invalid min-roi value, filter disabled")
        
        # Parse alert parameters
        alert_pnl_above = None
        if "--alert-pnl-above" in sys.argv:
            try:
                idx = sys.argv.index("--alert-pnl-above")
                alert_pnl_above = float(sys.argv[idx + 1])
            except (IndexError, ValueError):
                print("⚠️  Invalid alert-pnl-above value")
        
        alert_pnl_below = None
        if "--alert-pnl-below" in sys.argv:
            try:
                idx = sys.argv.index("--alert-pnl-below")
                alert_pnl_below = float(sys.argv[idx + 1])
            except (IndexError, ValueError):
                print("⚠️  Invalid alert-pnl-below value")
        
        alert_tvl_above = None
        if "--alert-tvl-above" in sys.argv:
            try:
                idx = sys.argv.index("--alert-tvl-above")
                alert_tvl_above = float(sys.argv[idx + 1])
            except (IndexError, ValueError):
                print("⚠️  Invalid alert-tvl-above value")
        
        interactive = "--no-interactive" not in sys.argv
        
        live_monitor(hlp_vault, refresh_interval, top_n, sort_by, min_equity, min_roi,
                    alert_pnl_above, alert_pnl_below, alert_tvl_above, interactive)
    else:
        # Run original one-time example
        main()
