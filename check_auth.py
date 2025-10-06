"""
Check authorization status of all accounts
"""
import asyncio
import os
from telethon import TelegramClient
from config import ACCOUNTS, PATHS

async def check_accounts():
    """Check if accounts are authorized"""
    print("="*60)
    print("CHECKING TELEGRAM ACCOUNT AUTHORIZATION")
    print("="*60)
    print()
    
    for i, account in enumerate(ACCOUNTS, 1):
        print(f"\n{i}. Checking {account['name']} ({account['phone']})...")
        
        session_path = os.path.join(PATHS['sessions'], account['session_name'])
        
        try:
            client = TelegramClient(
                session_path,
                account['api_id'],
                account['api_hash']
            )
            
            await client.connect()
            
            if await client.is_user_authorized():
                me = await client.get_me()
                print(f"   ✅ AUTHORIZED")
                print(f"   📱 Name: {me.first_name} {me.last_name or ''}")
                print(f"   🆔 User ID: {me.id}")
            else:
                print(f"   ❌ NOT AUTHORIZED")
                print(f"   ℹ️  Need to authorize this account")
            
            await client.disconnect()
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
    print("\n" + "="*60)
    print("AUTHORIZATION CHECK COMPLETE")
    print("="*60)
    print()
    print("💡 To re-authorize accounts:")
    print("   1. Delete session files: rm sessions/*.session")
    print("   2. Run: python3 main.py --auth")
    print()

if __name__ == "__main__":
    asyncio.run(check_accounts())

