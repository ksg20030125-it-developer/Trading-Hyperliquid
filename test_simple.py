"""Simple test to check if data displays"""
import sys
sys.path.insert(0, 'D:/Project/Hyperliquid-Data')

from hyperliquid_api_example import HyperliquidAPI

print("Testing API connection...")
api = HyperliquidAPI()

hlp_vault = "0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"
print(f"\nFetching vault: {hlp_vault}")

vault_data = api.get_vault_details(hlp_vault)

if vault_data:
    print("\n✅ Data received successfully!")
    print(f"Vault name: {vault_data.get('name', 'N/A')}")
    print(f"Leader: {vault_data.get('leader', 'N/A')}")
    print(f"Number of followers: {len(vault_data.get('followers', []))}")
    
    if 'followers' in vault_data and vault_data['followers']:
        print("\n📊 Top 3 followers:")
        for i, follower in enumerate(vault_data['followers'][:3], 1):
            print(f"{i}. {follower.get('user', 'N/A')[:15]}... - PnL: ${follower.get('allTimePnl', 0)}")
else:
    print("\n❌ No data received!")
