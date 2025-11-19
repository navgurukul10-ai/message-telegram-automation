"""
Patch Telethon's SQLite session to use WAL mode and proper timeouts
This prevents database lock errors during disconnect
"""
import sqlite3
from telethon.sessions import SQLiteSession

# Store original _execute method
_original_execute = SQLiteSession._execute

def _patched_execute(self, stmt, *values):
    """Patched execute that ensures WAL mode and timeout"""
    # Ensure connection exists
    if self._conn is None:
        self._conn = sqlite3.connect(
            self.filename,
            timeout=30.0,  # 30 second timeout
            check_same_thread=False
        )
        # Enable WAL mode and optimizations
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._conn.execute("PRAGMA busy_timeout=30000")
        self._conn.execute("PRAGMA cache_size=-64000")
    
    # Call original execute
    return _original_execute(self, stmt, *values)

def patch_telethon_sessions():
    """Apply the patch to Telethon's SQLiteSession"""
    SQLiteSession._execute = _patched_execute
    print("✅ Telethon session patch applied (WAL mode + timeout)")

# Auto-patch on import
patch_telethon_sessions()

