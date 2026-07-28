"""
Fetch all available OpenAI models and filter by free/cheap options
"""

from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ============================================================================
# FETCH ALL AVAILABLE MODELS
# ============================================================================

def fetch_all_models():
    """Get all available models from OpenAI"""
    models = client.models.list()
    return [model.id for model in models]


def get_cheap_models():
    """Filter cheap/free models"""
    
    # Pricing as of 2024 (per 1M tokens)
    pricing = {
        # ✅ CHEAPEST (Use these for learning)
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50, "note": "CHEAPEST"},
        
        # DISCONTINUED (still work but being phased out)
        "gpt-4o-mini": {"input": 0.15, "output": 0.60, "note": "SUPER CHEAP"},
        
        # ✅ AFFORDABLE
        "gpt-4o": {"input": 2.50, "output": 10.00, "note": "Best quality"},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00, "note": "Expensive"},
        
        # FREE TIER (if you have free credits)
        "davinci-002": {"input": 0.10, "output": 0.20, "note": "Cheap embedding model"},
    }
    
    print("🔥 CHEAPEST OpenAI MODELS 🔥")
    print("=" * 70)
    print(f"{'Model':<20} {'Input (per 1M)':<15} {'Output':<10} {'Note':<15}")
    print("-" * 70)
    
    for model, prices in pricing.items():
        print(f"{model:<25} ${prices['input']:<19.2f} ${prices['output']:<19.2f} {prices['note']:<15}")
    
    print("\n✅ RECOMMENDATIONS:")
    print("  • For learning: gpt-3.5-turbo (cheapest, good enough)")
    print("  • For production: gpt-4o-mini (affordable + good quality)")
    print("  • For premium: gpt-4o (best but pricier)")
    print("  • AVOID: gpt-4-turbo (very expensive)")


# ============================================================================
# LIVE MODEL LISTING (from API)
# ============================================================================

def list_live_models():
    """Fetch actual models available from your API key"""
    print("\n📡 MODELS AVAILABLE ON YOUR ACCOUNT:")
    print("=" * 70)
    
    try:
        models = fetch_all_models()
        
        # Filter for useful models
        useful_models = [m for m in models if any(x in m.lower() for x in [
            "gpt", "turbo", "mini", "4o", "davinci"
        ])]
        
        for model in sorted(useful_models)[:15]:  # Show top 15
            print(f"  • {model}")
        
        print(f"\n✅ Total models available: {len(models)}")
        
    except Exception as e:
        print(f"❌ Error fetching models: {e}")
        print("   Check your API key")


# ============================================================================
# COST ESTIMATOR
# ============================================================================

def estimate_cost(prompt_length: int, response_length: int, model: str = "gpt-3.5-turbo"):
    """Estimate API call cost"""
    
    pricing = {
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4o": {"input": 2.50, "output": 10.00},
    }
    
    if model not in pricing:
        print(f"❌ Model {model} not found")
        return
    
    # Rough estimate: 1 token ≈ 4 characters
    prompt_tokens = prompt_length // 4
    response_tokens = response_length // 4
    
    prices = pricing[model]
    input_cost = (prompt_tokens / 1_000_000) * prices["input"]
    output_cost = (response_tokens / 1_000_000) * prices["output"]
    total_cost = input_cost + output_cost
    
    print(f"\n💰 COST ESTIMATE ({model}):")
    print(f"  Prompt: ~{prompt_tokens} tokens → ${input_cost:.6f}")
    print(f"  Response: ~{response_tokens} tokens → ${output_cost:.6f}")
    print(f"  Total: ${total_cost:.6f}")


# ============================================================================
# QUICK TEST - Make a cheap API call
# ============================================================================

def test_cheap_model():
    """Test the cheapest model"""
    print("\n🧪 TESTING gpt-3.5-turbo:")
    print("-" * 70)
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'Hello' in 2 words"}],
            max_tokens=10
        )
        
        print(f"✅ Response: {response.choices[0].message.content}")
        print(f"📊 Tokens used: {response.usage.total_tokens}")
        print(f"💵 Cost: ~${(response.usage.total_tokens / 1_000_000) * 0.75:.6f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("🤖 OpenAI Models - Price Comparison\n")
    
    # Show pricing
    get_cheap_models()
    
    # List live models
    list_live_models()
    
    # Cost estimation
    estimate_cost(prompt_length=500, response_length=200, model="gpt-3.5-turbo")
    
    # Test cheap model
    test_cheap_model()
    
    print("\n" + "=" * 70)
    print("✨ For backend learning: USE gpt-3.5-turbo")
    print("   It's the cheapest at ~$2 per 1M tokens")
    print("=" * 70)


"""
RUN THIS:
--------
python fetch_models.py

OUTPUT EXAMPLE:
-----------
🤖 OpenAI Models - Price Comparison

🔥 CHEAPEST OpenAI MODELS 🔥
==============================================================================
Model                    Input (per 1M)       Output               Note
------
gpt-3.5-turbo            $0.50                $1.50                CHEAPEST
gpt-4o-mini              $0.15                $0.60                SUPER CHEAP
gpt-4o                   $2.50                $10.00               Best quality
gpt-4-turbo              $10.00               $30.00               Expensive

✅ RECOMMENDATIONS:
  • For learning: gpt-3.5-turbo (cheapest, good enough)
  • For production: gpt-4o-mini (affordable + good quality)

📡 MODELS AVAILABLE ON YOUR ACCOUNT:
  • gpt-3.5-turbo
  • gpt-4o-mini
  • gpt-4o
  • ... (more models)
"""