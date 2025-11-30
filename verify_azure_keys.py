import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def mask_key(key):
    if not key:
        return "None"
    if len(key) < 8:
        return "****"
    return f"{key[:4]}...{key[-4:]} (Length: {len(key)})"

def test_azure_deployment(api_key, api_base, api_version, deployment_name, label="Azure"):
    print(f"\n--- Testing {label} Configuration ---")
    
    if not api_key or not api_base or not deployment_name:
        print(f"❌ Missing configuration for {label}.")
        print(f"   Key: {mask_key(api_key)}")
        print(f"   Base: {api_base or 'Missing'}")
        print(f"   Deployment: {deployment_name or 'Missing'}")
        return

    # Check for common key issues
    if len(api_key) != 32:
        print(f"⚠️  WARNING: Your API Key length is {len(api_key)} characters.")
        print(f"   Standard Azure OpenAI keys are exactly 32 characters (hexadecimal).")
        print(f"   You might have copied a Connection String, a Token, or the wrong value.")
        print(f"   Please check 'Keys and Endpoint' in the Azure Portal again.")


    # Clean up base URL
    base_url = api_base.rstrip('/')
    
    # 1. Test Standard Azure OpenAI Path with api-key header
    url_standard = f"{base_url}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"
    
    print(f"1. Testing Standard URL: {url_standard}")
    print(f"   Using Header 'api-key': {mask_key(api_key)}")
    
    payload = {
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 5
    }
    
    try:
        response = requests.post(url_standard, headers={"api-key": api_key, "Content-Type": "application/json"}, json=payload)
        
        if response.status_code == 200:
            print(f"   ✅ Success! Response: {response.json()['choices'][0]['message']['content']}")
            return
        else:
            print(f"   ❌ Failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Connection Error: {str(e)}")

    # 2. Test MaaS/Serverless Path (often used in AI Studio)
    # Format: {base_url}/chat/completions
    url_maas = f"{base_url}/chat/completions"
    print(f"\n2. Testing MaaS/Serverless URL: {url_maas}")
    
    # Try with api-key header
    print(f"   Attempt A: Using Header 'api-key': {mask_key(api_key)}")
    try:
        resp_maas_key = requests.post(url_maas, headers={"api-key": api_key, "Content-Type": "application/json"}, json=payload)
        if resp_maas_key.status_code == 200:
            print(f"   ✅ Success! Response: {resp_maas_key.json()['choices'][0]['message']['content']}")
            return
        else:
            print(f"   ❌ Failed: {resp_maas_key.status_code}")
            # print(f"   Response: {resp_maas_key.text}") # Reduce noise
    except Exception as e:
        print(f"   ❌ Connection Error: {str(e)}")

    # Try with Bearer Token (Authorization header)
    print(f"   Attempt B: Using Header 'Authorization: Bearer ...'")
    try:
        resp_maas_bearer = requests.post(url_maas, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, json=payload)
        if resp_maas_bearer.status_code == 200:
            print(f"   ✅ Success! Response: {resp_maas_bearer.json()['choices'][0]['message']['content']}")
            return
        else:
            print(f"   ❌ Failed: {resp_maas_bearer.status_code}")
            print(f"   Response: {resp_maas_bearer.text}")
    except Exception as e:
        print(f"   ❌ Connection Error: {str(e)}")

    print(f"\n❌ All attempts failed for {label}. Please verify your Key and Endpoint.")

# Test Foundry
test_azure_deployment(
    os.getenv("AZURE_FOUNDRY_API_KEY"),
    os.getenv("AZURE_FOUNDRY_API_BASE"),
    os.getenv("AZURE_FOUNDRY_API_VERSION", "2024-02-15-preview"),
    os.getenv("AZURE_GPT4_DEPLOYMENT"), 
    "Azure Foundry (GPT-4)"
)
