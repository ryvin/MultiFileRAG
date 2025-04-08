import requests
import json

def check_pipeline_status(server_url="http://localhost:9621"):
    """Check the pipeline status of the MultiFileRAG server."""
    try:
        response = requests.get(f"{server_url}/documents/pipeline_status")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Status code: {response.status_code}", "details": response.text}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    status = check_pipeline_status()
    print(json.dumps(status, indent=2))
