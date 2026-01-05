# 🚀 Hyperliquid Live Leaderboard Monitor

A real-time monitoring tool for Hyperliquid vault leaderboards that auto-refreshes in your terminal, just like the Hyperliquid homepage!

## Features

- 🔄 **Auto-refresh**: Continuously updates leaderboard data every few seconds
- 📊 **Live rankings**: See top performers ranked by all-time PnL
- ⏱️ **Customizable refresh**: Set your own refresh interval
- 🎯 **Flexible display**: Choose how many top performers to show
- 🎨 **Clean UI**: Beautiful terminal display with emojis and formatting
- ⌨️ **Easy exit**: Press Ctrl+C to stop monitoring

## Usage

### Quick Start

Run the live monitor with default settings (5-second refresh, top 10):

```bash
python hyperliquid_api_example.py --live
```

### Custom Configuration

**3-second refresh interval:**

```bash
python hyperliquid_api_example.py --live --interval 3
```

**Show top 15 performers:**

```bash
python hyperliquid_api_example.py --live --top 15
```

**Combined (3-second refresh, top 20):**

```bash
python hyperliquid_api_example.py --live --interval 3 --top 20
```

### One-time Display

Run without live mode to fetch and display once:

```bash
python hyperliquid_api_example.py
```

### Get Help

```bash
python hyperliquid_api_example.py --help
```

## Command-Line Options

| Option                 | Short | Description                      | Default |
| ---------------------- | ----- | -------------------------------- | ------- |
| `--live`               | `-l`  | Enable live monitoring mode      | Off     |
| `--interval <seconds>` | -     | Refresh interval in seconds      | 5       |
| `--top <number>`       | -     | Number of top performers to show | 10      |
| `--help`               | `-h`  | Show help message                | -       |

## What You'll See

The live monitor displays:

- 🏆 **Vault name and address**
- ⏰ **Last update timestamp**
- 👥 **Total number of followers**
- 📈 **Top performers with:**
  - User address (truncated)
  - Current vault equity
  - Current PnL
  - All-time PnL (ranking metric)
  - ROI percentage
  - Days following the vault

## Example Output

```
================================================================================
🏆  HYPERLIQUID VAULT LEADERBOARD - LIVE MONITOR
📊  HLP Vault: 0xdfc24b077bc1425ad1dea75bcb6f8158e10df303
⏰  Last Updated: 2025-12-25 14:30:45
👥  Total Followers: 100 | Showing Top 10
================================================================================

1. User: 0x8196e064...
   Current Equity: $3,771,481.14
   Current PnL: $747,548.48
   All-Time PnL: $1,474,225.38
   ROI: 39.09%
   Days Following: 841

2. User: 0x3a648fc9...
   Current Equity: $8,912,644.68
   Current PnL: $912,644.89
   All-Time PnL: $932,896.47
   ROI: 10.47%
   Days Following: 331

... (more entries)

================================================================================
Press Ctrl+C to stop monitoring
================================================================================
```

## How It Works

Since Hyperliquid doesn't have a direct "leaderboard" API endpoint, the monitor:

1. Fetches vault details (includes follower performance data)
2. Sorts followers by all-time PnL
3. Displays the top performers
4. Automatically refreshes at your specified interval

## Monitoring Tips

- **Faster refresh (1-2 seconds)**: Good for active monitoring but uses more API calls
- **Standard refresh (5 seconds)**: Balanced, recommended for most use cases
- **Slower refresh (10+ seconds)**: Lighter on API, good for passive monitoring
- **Top 5-10**: Quick overview of best performers
- **Top 20-50**: Broader view of the leaderboard

## Stopping the Monitor

Press `Ctrl+C` to gracefully stop the live monitor. You'll see a confirmation message before exiting.

## Requirements

- Python 3.7+
- `requests` library

## Monitored Vault

Currently monitors the **HLP (Hyperliquidity Provider) Vault**:

- Address: `0xdfc24b077bc1425ad1dea75bcb6f8158e10df303`
- One of the main Hyperliquid vaults

You can modify the vault address in the script to monitor other vaults.

---

**Enjoy monitoring! 🎯📊**
