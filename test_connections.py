# test_connections.py
import asyncio
import redis.asyncio as aioredis
import asyncpg
from pymongo import MongoClient
import httpx

async def test_all():
    print("\n" + "="*50)
    print("  TESTING ALL CONNECTIONS")
    print("="*50 + "\n")

    results = {}

    # Test Redis
    print("1. Testing Redis...")
    try:
        r = await aioredis.from_url(
            "redis://localhost:6379",
            encoding="utf-8",
            decode_responses=True
        )
        await r.set("test_key", "hello_agriguard")
        val = await r.get("test_key")
        await r.delete("test_key")
        assert val == "hello_agriguard"
        print("   ✅ Redis — CONNECTED & WORKING\n")
        results["Redis"] = "✅"
    except Exception as e:
        print(f"   ❌ Redis — FAILED: {e}")
        print("   → Fix: cd infrastructure && docker-compose up -d redis\n")
        results["Redis"] = "❌"

    # Test PostgreSQL
    print("2. Testing PostgreSQL...")
    try:
        conn = await asyncpg.connect(
            "postgresql://agriguard_user:agriguard_pass@localhost:5433/agriguard",
            timeout=5
        )
        version = await conn.fetchval("SELECT version()")
        await conn.close()
        print(f"   ✅ PostgreSQL — CONNECTED")
        print(f"   Version: {version[:40]}...\n")
        results["PostgreSQL"] = "✅"
    except Exception as e:
        print(f"   ❌ PostgreSQL — FAILED: {e}")
        print("   → Fix: cd infrastructure && docker-compose up -d postgres\n")
        results["PostgreSQL"] = "❌"

    # Test MongoDB
    print("3. Testing MongoDB...")
    try:
        client = MongoClient(
            "mongodb://localhost:27017",
            serverSelectionTimeoutMS=3000
        )
        client.server_info()
        dbs = client.list_database_names()
        client.close()
        print(f"   ✅ MongoDB — CONNECTED")
        print(f"   Databases: {dbs}\n")
        results["MongoDB"] = "✅"
    except Exception as e:
        print(f"   ❌ MongoDB — FAILED: {e}")
        print("   → Fix: cd infrastructure && docker-compose up -d mongodb\n")
        results["MongoDB"] = "❌"

    # Test Ollama
    print("4. Testing Ollama...")
    try:
        resp = httpx.get("http://localhost:11434", timeout=5)
        print(f"   ✅ Ollama — RUNNING: {resp.text.strip()}")
        # Test model list
        models_resp = httpx.get("http://localhost:11434/api/tags", timeout=5)
        models = models_resp.json().get("models", [])
        model_names = [m["name"] for m in models]
        print(f"   Models available: {model_names}\n")
        if not any("llama3" in m or "mistral" in m for m in model_names):
            print("   ⚠️  llama3 not found — run: ollama pull llama3\n")
        results["Ollama"] = "✅"
    except Exception as e:
        print(f"   ❌ Ollama — FAILED: {e}")
        print("   → Fix: Open new terminal and run: ollama serve\n")
        results["Ollama"] = "❌"

    # Summary
    print("="*50)
    print("  SUMMARY")
    print("="*50)
    for service, status in results.items():
        print(f"  {status} {service}")
    
    all_good = all(v == "✅" for v in results.values())
    if all_good:
        print("\n🎉 All connections working! Ready for next step.\n")
    else:
        print("\n⚠️  Fix failed connections before continuing.\n")

asyncio.run(test_all())