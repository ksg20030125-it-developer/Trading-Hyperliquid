"""Quick test of the live monitor functionality"""
import sys
sys.path.insert(0, 'd:/Project/Hyperliquid-Data')

from hyperliquid_api_example import live_monitor

# Test with 3-second refresh showing top 5
hlp_vault = "0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"
print("\n🚀 Starting live monitor test (press Ctrl+C to stop)...\n")
live_monitor(hlp_vault, refresh_interval=3, top_n=5)
