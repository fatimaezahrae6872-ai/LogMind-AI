
import json
import urllib.request
import urllib.error

url = "http://localhost:11434/api/chat"

payload = {
    "model": "qwen2.5:1.5b",
    "messages": [
        {
            "role": "system",
            "content": "You are LogMind AI, an intelligent log analysis assistant."
        },
        {
            "role": "user",
            "content": "Explain briefly what a database connection error means."
        }
    ],
    "stream": False,
    "options": {
        "num_predict": 120
    }
}

try:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        result = json.loads(response.read().decode("utf-8"))

    print("\n========== LOGMIND AI - OLLAMA TEST ==========")
    print("Model:", result.get("model"))
    print("\nAI Response:")
    print(result["message"]["content"])
    print("\nOllama connection successful!")

except urllib.error.URLError as error:
    print("Ollama connection failed:", error)

except Exception as error:
    print("Unexpected error:", error)
