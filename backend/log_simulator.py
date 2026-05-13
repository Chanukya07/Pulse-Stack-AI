import json
import time
import random
import os
from datetime import datetime, timezone

LOGS_FILE = os.path.join(os.path.dirname(__file__), "local_logs.json")

SERVICES = ["api-gateway", "auth-service", "payment-service", "database", "redis-cache"]
LEVELS = ["info", "info", "info", "warn", "error"]

MESSAGES = {
    "api-gateway": ["Request received", "Routing traffic to auth-service", "Rate limit checking", "Upstream timed out"],
    "auth-service": ["User authenticated successfully", "Token validation failed", "JWT expired", "Connecting to database"],
    "payment-service": ["Processing transaction", "Payment gateway timeout", "Transaction approved", "Insufficient funds"],
    "database": ["Query executed successfully", "Deadlock detected", "Connection pool exhausted", "Vacuuming tables"],
    "redis-cache": ["Cache hit", "Cache miss", "Memory limit reached", "Evicting keys"]
}

def generate_log():
    service = random.choice(SERVICES)
    level = random.choice(LEVELS)
    
    # Force some correlation if it's an error
    if level == "error":
        msg = MESSAGES[service][-1] # the last message in the list is usually an error
    else:
        msg = random.choice(MESSAGES[service][:-1])
        
    # Simulate a sudden spike in 502s occasionally
    if random.random() < 0.05:
        service = "api-gateway"
        level = "error"
        msg = "502 Bad Gateway: Upstream service payment-service unreachable"

    log_entry = {
        "_id": f"sim_{int(time.time() * 1000)}_{random.randint(1000, 9999)}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": service,
        "level": level,
        "message": msg
    }
    return log_entry

print("Starting log simulator... Writing to", LOGS_FILE)
# Clear the file on start
with open(LOGS_FILE, "w", encoding="utf-8") as f:
    f.write("")

try:
    while True:
        # Generate 1 to 3 logs per tick
        for _ in range(random.randint(1, 3)):
            log = generate_log()
            with open(LOGS_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(log) + "\n")
            print(f"[{log['timestamp']}] {log['service']} - {log['level'].upper()}: {log['message']}")
        
        time.sleep(random.uniform(0.5, 2.0))
except KeyboardInterrupt:
    print("\nSimulator stopped.")
