"""
Test script to explore Hyperliquid API pagination options
"""

import requests
import json

API_URL = "https://api.hyperliquid.xyz/info"
HLP_VAULT = "0xdfc24b077bc1425ad1dea75bcb6f8158e10df303"

def test_api_parameters():
    """Test various pagination parameters"""
    
    test_cases = [
        # Test 1: No limit (baseline)
        {
            "name": "No limit parameter",
            "payload": {
                "type": "vaultDetails",
                "vaultAddress": HLP_VAULT
            }
        },
        # Test 2: With limit parameter
        {
            "name": "With limit=2000",
            "payload": {
                "type": "vaultDetails",
                "vaultAddress": HLP_VAULT,
                "limit": 2000
            }
        },
        # Test 3: With maxFollowers parameter
        {
            "name": "With maxFollowers=2000",
            "payload": {
                "type": "vaultDetails",
                "vaultAddress": HLP_VAULT,
                "maxFollowers": 2000
            }
        },
        # Test 4: With count parameter
        {
            "name": "With count=2000",
            "payload": {
                "type": "vaultDetails",
                "vaultAddress": HLP_VAULT,
                "count": 2000
            }
        },
        # Test 5: With pageSize parameter
        {
            "name": "With pageSize=2000",
            "payload": {
                "type": "vaultDetails",
                "vaultAddress": HLP_VAULT,
                "pageSize": 2000
            }
        },
        # Test 6: With offset and limit
        {
            "name": "With offset=0, limit=2000",
            "payload": {
                "type": "vaultDetails",
                "vaultAddress": HLP_VAULT,
                "offset": 0,
                "limit": 2000
            }
        }
    ]
    
    print("="*80)
    print("TESTING HYPERLIQUID API PAGINATION PARAMETERS")
    print("="*80)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}: {test['name']}")
        print(f"{'='*80}")
        print(f"Payload: {json.dumps(test['payload'], indent=2)}")
        
        try:
            response = requests.post(API_URL, json=test['payload'], timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'followers' in data:
                    follower_count = len(data['followers'])
                    print(f"✅ SUCCESS - Followers returned: {follower_count}")
                    
                    if follower_count > 100:
                        print(f"🎉 BREAKTHROUGH! Got {follower_count} followers with this payload!")
                        print(f"Winning payload: {json.dumps(test['payload'], indent=2)}")
                    
                    # Show first and last follower for verification
                    if follower_count > 0:
                        print(f"\nFirst follower: {data['followers'][0].get('user', 'N/A')[:20]}...")
                        print(f"Last follower: {data['followers'][-1].get('user', 'N/A')[:20]}...")
                else:
                    print(f"⚠️ No 'followers' key in response")
                    print(f"Response keys: {list(data.keys())}")
            else:
                print(f"❌ HTTP {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    print(f"\n{'='*80}")
    print("TESTING COMPLETE")
    print(f"{'='*80}")

if __name__ == "__main__":
    test_api_parameters()
