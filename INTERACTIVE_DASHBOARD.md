# 🎮 Interactive Hyperliquid Dashboard

A fully interactive, real-time monitoring dashboard with on-the-fly controls and intelligent alerts!

## 🚀 New Features

### 1. **Interactive Controls** 🎛️

Change settings while the dashboard is running - no need to restart!

**Available Commands:**

- `h` - Show help
- `q` - Quit dashboard
- `i` - Change refresh interval on the fly
- `s` - Change sort order (pnl, roi, equity, days)
- `t` - Change number of top performers shown
- `e` - Set/update minimum equity filter
- `r` - Set/update minimum ROI filter
- `c` - Clear all active filters

### 2. **Smart Alert System** 🔔

Get notified when important thresholds are crossed!

**Alert Types:**

- **PnL Above Alert** - Notifies when any follower's PnL exceeds threshold
- **PnL Below Alert** - Notifies when any follower's PnL drops below threshold
- **TVL Above Alert** - Notifies when total vault TVL crosses threshold

**Alert Features:**

- ✅ Only alerts on threshold crossing (not every refresh)
- ✅ Color-coded notifications (green for gains, red for drops)
- ✅ User-specific PnL tracking
- ✅ Vault-wide TVL monitoring

## 📖 Usage Examples

### Basic Interactive Mode

```bash
python hyperliquid_api_example.py --live
```

Then use keyboard commands to adjust settings in real-time!

### Monitor High Performers with Alert

```bash
python hyperliquid_api_example.py --live --alert-pnl-above 1000000
```

Get notified when anyone's PnL crosses $1M!

### Whale Tracker with Multiple Alerts

```bash
python hyperliquid_api_example.py --live --min-equity 1000000 --alert-pnl-above 500000 --alert-tvl-above 50000000
```

Monitor whales (>$1M equity) and get alerts for:

- Individual PnL > $500K
- Total vault TVL > $50M

### Ultra-Responsive Monitoring

```bash
python hyperliquid_api_example.py --live --interval 3 --sort-by roi
```

Fast 3-second refresh, sorted by ROI. Change to equity sorting on the fly by pressing `s`!

## 🎯 Interactive Workflow Example

1. **Start monitoring:**

   ```bash
   python hyperliquid_api_example.py --live
   ```

2. **Dashboard shows initial data** with controls at bottom

3. **Want to see only high-ROI performers?**

   - Press `s` → choose "roi"
   - Press `r` → enter "25" (for 25% minimum ROI)

4. **Want faster updates?**

   - Press `i` → enter "2" (for 2-second refresh)

5. **Want to see more performers?**

   - Press `t` → enter "20" (show top 20 instead of 10)

6. **Clear filters and start over:**

   - Press `c` → all filters cleared

7. **Done monitoring?**
   - Press `q` → clean exit

## 🔔 Alert Examples

### Example 1: High Performer Alert

```bash
python hyperliquid_api_example.py --live --alert-pnl-above 1500000
```

**Output when triggered:**

```
================================================================================
🔔 ALERT: User 0x8196e064... PnL crossed $1,500,000.00 (now $1,574,225.38)
================================================================================
```

### Example 2: Risk Alert

```bash
python hyperliquid_api_example.py --live --alert-pnl-below 100000
```

**Output when triggered:**

```
================================================================================
🔔 ALERT: User 0xabcd1234... PnL dropped below $100,000.00 (now $95,432.12)
================================================================================
```

### Example 3: TVL Milestone Alert

```bash
python hyperliquid_api_example.py --live --alert-tvl-above 100000000
```

**Output when triggered:**

```
================================================================================
🔔 ALERT: Vault TVL crossed $100,000,000.00 (now $105,234,567.89)
================================================================================
```

## 💡 Pro Tips

1. **Start Simple, Adjust Live:**

   - Begin with default settings
   - Use interactive controls to fine-tune based on what you see

2. **Combine Filters for Precision:**

   - Use `--min-equity` to focus on whales
   - Use `--min-roi` to find best performers
   - Adjust both interactively while monitoring

3. **Set Strategic Alerts:**

   - `--alert-pnl-above` for identifying breakout performers
   - `--alert-tvl-above` for tracking vault growth milestones
   - Alerts persist across filter changes

4. **Multi-Monitor Setup:**

   - Run multiple instances with different filters
   - One for whales, one for high-ROI, one for all followers
   - Each with custom alerts

5. **Performance Optimization:**
   - Use longer refresh intervals (10-30s) for passive monitoring
   - Use shorter intervals (2-5s) when actively trading/analyzing
   - Adjust via `i` command based on current needs

## 🎨 Dashboard Display

```
================================================================================
🏆  HYPERLIQUID VAULT LEADERBOARD - LIVE MONITOR
📊  Vault: 0xdfc24b077bc1425ad1dea75bcb6f8158e10df303
⏰  Updated: 2025-12-25 15:30:45 | Sorting: ROI
👥  Total: 100 | Showing: 10
================================================================================

🥇 1. User: 0x8196e064...
   Current Equity: $3,771,420.67
   Current PnL: $747,488.01
   All-Time PnL: $1,474,164.92
   ROI: 39.09%
   Days Following: 841

... (more entries)

================================================================================
📋 Press 'h' for help | 'q' to quit
================================================================================
```

## 🛠️ Technical Details

**Threading:**

- Main thread: Data fetching and display
- Input thread: Keyboard command handling
- Non-blocking design for smooth operation

**Alert Logic:**

- Tracks previous values per user/vault
- Only triggers on threshold crossings
- Prevents alert spam on fluctuations

**Interactive State:**

- Settings persist across refreshes
- Real-time filter application
- Immediate sort order changes

## 🚨 Troubleshooting

**Q: Interactive controls not working?**

- Ensure you're running with `--live` flag
- Use `--no-interactive` if you want auto-mode only

**Q: Too many alerts?**

- Set higher thresholds
- Use more specific filters first

**Q: Settings not updating?**

- Wait for next refresh cycle
- Check terminal for confirmation messages

---

**Enjoy your fully interactive Hyperliquid monitoring experience!** 🎯📊🚀
