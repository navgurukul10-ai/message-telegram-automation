"""
Authorize only Account 1
"""
import asyncio
import os
from telethon import TelegramClient
from config import ACCOUNTS, PATHS

async def auth_account1():
    """Authorize Account 1 only"""
    print("="*60)
    print("AUTHORIZING ACCOUNT 1")
    print("="*60)
    print()
    
    account = ACCOUNTS[0]  # First account
    
    print(f"Account: {account['name']}")
    print(f"Phone: {account['phone']}")
    print()
    
    session_path = os.path.join(PATHS['sessions'], account['session_name'])
    
    client = TelegramClient(
        session_path,
        account['api_id'],
        account['api_hash']
    )
    
    await client.connect()
    
    if not await client.is_user_authorized():
        print(f"📱 Sending code to {account['phone']}...")
        await client.send_code_request(account['phone'])
        print(f"✅ Code sent! Check your Telegram app.")
        print()
        
        code = input(f"Enter the code for {account['name']} ({account['phone']}): ")
        
        try:
            await client.sign_in(account['phone'], code)
            print()
            print("✅ Account 1 authorized successfully!")
            print()
            
            # Verify
            me = await client.get_me()
            print(f"📱 Name: {me.first_name} {me.last_name or ''}")
            print(f"🆔 User ID: {me.id}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("✅ Account 1 is already authorized!")
        me = await client.get_me()
        print(f"📱 Name: {me.first_name} {me.last_name or ''}")
    
    await client.disconnect()
    
    print()
    print("="*60)
    print("DONE!")
    print("="*60)
    print()
    print("Now all 4 accounts should be authorized.")
    print("Run: python3 check_auth.py to verify")
    print()

if __name__ == "__main__":
    asyncio.run(auth_account1())

