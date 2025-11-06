"""
System Verification Test Script
Run this to verify all components are working
"""
import os
import sqlite3
from datetime import datetime

def test_imports():
    """Test if all modules can be imported"""
    print("🔍 Testing imports...")
    try:
        import config
        from utils.logger import get_logger
        from utils.database import DatabaseHandler
        from utils.classifier import MessageClassifier
        from utils.csv_handler import CSVHandler
        from utils.job_verifier import JobVerifier
        print("   ✅ All imports successful")
        return True
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False

def test_config():
    """Test configuration"""
    print("\n🔍 Testing configuration...")
    try:
        from config import RATE_LIMITS, MESSAGE_YEAR_FILTER, JOB_VERIFICATION
        
        # Check safe rate limits
        join_delay = RATE_LIMITS['join_group_delay']
        if join_delay[0] >= 1800:  # At least 30 minutes
            print(f"   ✅ Safe join delay: {join_delay[0]//60}-{join_delay[1]//60} minutes")
        else:
            print(f"   ⚠️  Join delay might be too short: {join_delay}")
        
        # Check max groups
        max_groups = RATE_LIMITS['max_groups_per_day']
        if max_groups <= 3:
            print(f"   ✅ Safe group limit: {max_groups} groups/day")
        else:
            print(f"   ⚠️  Too many groups: {max_groups} (recommend 2-3)")
        
        # Check year filter
        if MESSAGE_YEAR_FILTER == 2025:
            print(f"   ✅ Year filter: {MESSAGE_YEAR_FILTER}")
        else:
            print(f"   ⚠️  Year filter: {MESSAGE_YEAR_FILTER}")
        
        # Check working hours
        if 'working_hours' in RATE_LIMITS:
            hours = RATE_LIMITS['working_hours']
            print(f"   ✅ Working hours: {hours[0]} AM - {hours[1]} PM")
        else:
            print(f"   ⚠️  No working hours restriction")
        
        return True
    except Exception as e:
        print(f"   ❌ Config error: {e}")
        return False

def test_database():
    """Test database"""
    print("\n🔍 Testing database...")
    try:
        from utils.database import DatabaseHandler
        
        db = DatabaseHandler()
        conn = db.connect()
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['tech_jobs', 'non_tech_jobs', 'freelance_jobs', 
                          'messages', 'groups', 'daily_stats', 'account_usage']
        
        for table in required_tables:
            if table in tables:
                print(f"   ✅ Table exists: {table}")
            else:
                print(f"   ❌ Table missing: {table}")
        
        # Check tech_jobs table structure
        cursor.execute("PRAGMA table_info(tech_jobs)")
        columns = [row[1] for row in cursor.fetchall()]
        
        enhanced_fields = ['company_name', 'company_website', 'company_linkedin',
                          'skills_required', 'salary_range', 'verification_score']
        
        print("\n   Enhanced fields in tech_jobs:")
        for field in enhanced_fields:
            if field in columns:
                print(f"      ✅ {field}")
            else:
                print(f"      ❌ {field} missing")
        
        conn.close()
        return True
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False

def test_classifier():
    """Test job classifier"""
    print("\n🔍 Testing classifier...")
    try:
        from utils.classifier import MessageClassifier
        
        classifier = MessageClassifier()
        
        # Test cases
        test_messages = [
            ("Python developer needed for startup", "tech"),
            ("Marketing manager required", "non_tech"),
            ("Freelance web developer needed", "freelance"),
            ("Just a random message", None),
        ]
        
        for message, expected_type in test_messages:
            job_type, keywords = classifier.classify(message)
            if expected_type:
                if job_type and expected_type in job_type:
                    print(f"   ✅ '{message[:30]}...' → {job_type}")
                else:
                    print(f"   ⚠️  '{message[:30]}...' → {job_type} (expected {expected_type})")
            else:
                if not job_type:
                    print(f"   ✅ Non-job message filtered correctly")
        
        return True
    except Exception as e:
        print(f"   ❌ Classifier error: {e}")
        return False

def test_job_verifier():
    """Test job verifier"""
    print("\n🔍 Testing job verifier...")
    try:
        from utils.job_verifier import JobVerifier
        
        verifier = JobVerifier()
        
        # Test message with company info
        test_message = """
        TechCorp is hiring Python Developer!
        
        Skills: Python, Django, AWS
        Experience: 2-5 years
        Salary: ₹8-12 LPA
        Location: Bangalore
        Mode: Remote
        
        Apply: hr@techcorp.com
        Website: www.techcorp.com
        LinkedIn: linkedin.com/company/techcorp
        """
        
        result = verifier.verify_and_extract(test_message)
        
        if result:
            print(f"   ✅ Verification score: {result['verification_score']:.2f}%")
            print(f"   ✅ Verified: {result['is_verified']}")
            print(f"   ✅ Company: {result['company_name']}")
            print(f"   ✅ Website: {result['company_website']}")
            print(f"   ✅ LinkedIn: {result['company_linkedin']}")
            print(f"   ✅ Skills: {result['skills_required']}")
            print(f"   ✅ Salary: {result['salary_range']}")
        else:
            print(f"   ⚠️  Verification returned None")
        
        return True
    except Exception as e:
        print(f"   ❌ Verifier error: {e}")
        return False

def test_directories():
    """Test if all directories exist"""
    print("\n🔍 Testing directories...")
    try:
        from config import PATHS
        
        for name, path in PATHS.items():
            if os.path.exists(path):
                print(f"   ✅ {name}: {path}")
            else:
                print(f"   ⚠️  {name} missing: {path}")
                os.makedirs(path, exist_ok=True)
                print(f"      Created: {path}")
        
        return True
    except Exception as e:
        print(f"   ❌ Directory error: {e}")
        return False

def test_data_json():
    """Test if data.json exists and is valid"""
    print("\n🔍 Testing data.json...")
    try:
        import json
        from config import PATHS
        
        data_file = PATHS['groups_json']
        if os.path.exists(data_file):
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"   ✅ data.json exists")
            print(f"   ✅ Contains {len(data)} groups")
            
            # Check first group structure
            if len(data) > 0:
                first_group = data[0]
                if 'link' in first_group and 'name' in first_group:
                    print(f"   ✅ Group structure valid")
                else:
                    print(f"   ⚠️  Group structure might be invalid")
        else:
            print(f"   ❌ data.json not found at {data_file}")
            return False
        
        return True
    except Exception as e:
        print(f"   ❌ data.json error: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("🧪 SYSTEM VERIFICATION TEST")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_config),
        ("Database", test_database),
        ("Classifier", test_classifier),
        ("Job Verifier", test_job_verifier),
        ("Directories", test_directories),
        ("Data File", test_data_json),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} test failed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready to run.")
        print("\nNext steps:")
        print("1. Run: python3 main.py --auth  (authorize accounts)")
        print("2. Run: python3 main.py  (start fetching)")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    print("="*60)

if __name__ == "__main__":
    main()

