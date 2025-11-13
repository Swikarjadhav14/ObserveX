# ingestion/generator.py
import json, random, uuid
from datetime import datetime, timedelta

def random_log(i):
    return {
        "timestamp": (datetime.utcnow() + timedelta(seconds=i)).isoformat(),
        "traceId": str(uuid.uuid4()),
        "endpoint": random.choice(["/login","/search","/order","/checkout"]),
        "latency_ms": max(1, int(random.gauss(120,30) + (1 if random.random()<0.02 else 0)*1000)),
        "status_code": random.choice([200]*95 + [500]*3 + [404]*2),
        "user_id": random.randint(1,1000)
    }

if __name__ == "__main__":
    logs = [random_log(i) for i in range(5000)]
    with open("data/sample_logs.json", "w") as f:
        json.dump(logs, f, indent=2)
    print("✅ Wrote data/sample_logs.json (5000 logs)")
