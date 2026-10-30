import os
import sys
import time

def test_connection():
    print("=" * 60)
    print("  CineMatch MongoDB Connection Tester")
    print("=" * 60)
    
    # 1. Load .env
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_path):
        print("[ERROR] backend/.env file not found!")
        print("        Please create backend/.env with your MONGO_URI.")
        return False
        
    from dotenv import load_dotenv
    load_dotenv(env_path)
    
    mongo_uri = os.getenv('MONGO_URI', '').strip()
    db_name = os.getenv('MONGO_DBNAME', 'cinematch_db').strip()
    
    # 2. Check URI configuration
    if not mongo_uri:
        print("\n[INFO] MONGO_URI is currently EMPTY in backend/.env")
        print("       The application is running in local offline storage mode (local_db.json).")
        print("\nTo connect MongoDB:")
        print("  1. Open 'backend/.env' in your editor")
        print("  2. Add: MONGO_URI=your_actual_mongodb_connection_string")
        print("  3. Run this test again: python test_connection.py")
        return False
        
    placeholders = ["your-username", "your-password", "<username>", "<password>", "cluster-name", "<db_password>"]
    for ph in placeholders:
        if ph in mongo_uri:
            print(f"\n[WARNING] Your MONGO_URI contains placeholder text '{ph}'!")
            print("          Please replace it with your actual username/password in backend/.env.")
            return False
            
    print(f"\nTesting connection to MongoDB...")
    # Hide password in displayed URI
    masked_uri = mongo_uri
    if "@" in masked_uri:
        parts = masked_uri.split("@")
        prefix = parts[0]
        if ":" in prefix:
            user = prefix.split(":")[0] + ":" + prefix.split(":")[1].split("//")[1] if "//" in prefix else prefix.split(":")[0]
            masked_uri = f"{user}:****@{parts[1]}"
    print(f"  Target URI: {masked_uri}")
    print(f"  Target DB:  {db_name}")
    
    # 3. Test Connection
    try:
        import certifi
        from pymongo import MongoClient
        from pymongo.errors import OperationFailure, ServerSelectionTimeoutError, ConfigurationError
        
        client_kwargs = {
            "serverSelectionTimeoutMS": 5000,
            "connectTimeoutMS": 5000
        }
        if "mongodb+srv://" in mongo_uri or "ssl=true" in mongo_uri.lower():
            client_kwargs["tlsCAFile"] = certifi.where()
            
        client = MongoClient(mongo_uri, **client_kwargs)
        
        start_time = time.time()
        print("  Contacting MongoDB server (timeout: 5s)...")
        ping_res = client.admin.command('ping')
        latency_ms = int((time.time() - start_time) * 1000)
        
        print("\n" + "=" * 60)
        print("[SUCCESS] Connected to MongoDB successfully!")
        print(f"          Response time: {latency_ms}ms")
        print("=" * 60)
        
        # Test DB access
        db = client[db_name]
        cols = db.list_collection_names()
        print(f"  Database '{db_name}' collections: {cols if cols else '(none yet)'}")
        print("\nReady! You can now seed initial movie data by running:")
        print("  cd backend && python seed.py")
        print("Or launch the application:")
        print("  run-app.bat")
        return True
        
    except OperationFailure as e:
        print("\n" + "=" * 60)
        print("[ERROR] AUTHENTICATION FAILED")
        print("=" * 60)
        print(f"Details: {e}")
        print("\nHOW TO FIX:")
        print("1. Go to MongoDB Atlas (https://cloud.mongodb.com)")
        print("2. Navigate to 'Database Access' under Security in the left sidebar")
        print("3. Check that your Database User exists and you know its password")
        print("4. Make sure the password doesn't contain unescaped special characters (e.g. '@', ':', '/')")
        print("5. Update your username and password in backend/.env")
        return False
        
    except ServerSelectionTimeoutError as e:
        print("\n" + "=" * 60)
        print("[ERROR] SERVER SELECTION TIMEOUT (Cannot reach cluster)")
        print("=" * 60)
        print(f"Details: {e}")
        print("\nHOW TO FIX (Most likely IP Whitelist):")
        print("1. Go to MongoDB Atlas (https://cloud.mongodb.com)")
        print("2. Navigate to 'Network Access' under Security in the left sidebar")
        print("3. Click '+ ADD IP ADDRESS'")
        print("4. Select 'ALLOW ACCESS FROM ANYWHERE' (0.0.0.0/0)")
        print("5. Click 'Confirm' and wait 1 minute for it to apply, then test again")
        return False
        
    except ConfigurationError as e:
        print("\n" + "=" * 60)
        print("[ERROR] CONFIGURATION ERROR")
        print("=" * 60)
        print(f"Details: {e}")
        print("\nHOW TO FIX:")
        print("1. Check your MONGO_URI format in backend/.env")
        print("2. A standard MongoDB Atlas URI looks like:")
        print("   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority")
        return False
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"[ERROR] CONNECTION FAILED: {type(e).__name__}")
        print("=" * 60)
        print(f"Details: {e}")
        return False

if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)
