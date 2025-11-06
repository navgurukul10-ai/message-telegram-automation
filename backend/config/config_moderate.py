"""
Moderate Rate Limits Configuration
थोड़ा faster but still relatively safe

⚠️ Use at your own risk - ban risk increases slightly
"""

# Moderate Limits (Faster than ultra-safe, safer than aggressive)
MODERATE_RATE_LIMITS = {
    'join_group_delay': (300, 600),     # 5-10 minutes (instead of 30-60)
    'message_fetch_delay': (2, 5),      # Same
    'max_groups_per_day': 5,            # 5 instead of 2
    'max_groups_per_hour': 2,           # 2 instead of 1
    'daily_message_limit': 75,          # Same
    'request_delay': (5, 15),           # Same
    'working_hours': (10, 20),          # Same
}

"""
Comparison:

Ultra-Safe (Current):
  - 30-60 min delays
  - 2 groups/day
  - Ban risk: ~3%
  - Time: 2-3 hours for 2 groups

Moderate (This):
  - 5-10 min delays
  - 5 groups/day
  - Ban risk: ~10%
  - Time: 1-2 hours for 5 groups

Aggressive (DON'T USE):
  - 1-2 min delays
  - 15+ groups/day
  - Ban risk: ~50%+
"""

# To use moderate limits:
# 1. Open config.py
# 2. Replace RATE_LIMITS with MODERATE_RATE_LIMITS values
# 3. Save and run

print("""
⚠️  MODERATE RATE LIMITS

Faster but slightly higher ban risk.

Recommended for testing only, not daily production use.

To use:
  1. Copy these values to config.py RATE_LIMITS
  2. Save
  3. Run daily_run.py
  
Time: 1-2 hours for 5 groups
Ban Risk: ~10% (acceptable for testing)
""")

