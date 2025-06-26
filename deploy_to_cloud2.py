#!/usr/bin/env python3
"""
Enhanced Cloud Deployment - All Evaluators with Reliability

Combines all evaluators from the full version but uses the successful patterns 
from the fast version. Removes problematic parameters and adds fallback handling.
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.evaluation import evaluate
from azure.ai.evaluation import (
    ContentSafetyEvaluator,
    HateUnfairnessEvaluator,
    RelevanceEvaluator,
    CoherenceEvaluator,
    GroundednessEvaluator,
    FluencyEvaluator,
    RetrievalEvaluator,
    IntentResolutionEvaluator,
    TaskAdherenceEvaluator,
    AzureOpenAIModelConfiguration
)
from friendliness.friendliness import FriendlinessEvaluator

# Load environment variables with override (like fast version)
load_dotenv(override=True)

# Azure AI project configuration
azure_ai_project = {
    "subscription_id": os.getenv("AZURE_SUBSCRIPTION_ID"),
    "resource_group_name": os.getenv("AZURE_RESOURCE_GROUP"),
    "project_name": os.getenv("AZURE_AI_FOUNDRY_PROJECT"),
}

# Model configuration (simplified like fast version)
model_config = {
    "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
    "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
    "azure_deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT"),
}

# Azure model config for evaluators that need it
azure_model_config = AzureOpenAIModelConfiguration(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY")
)

print("🚀 Enhanced deployment with all evaluators...")

# Initialize core evaluators (no threshold parameters)
evaluators = {}
evaluator_configs = {}

try:
    # Core evaluators (most reliable)
    print("📊 Initializing core evaluators...")
    evaluators["groundedness"] = GroundednessEvaluator(model_config)
    evaluator_configs["groundedness"] = {
        "column_mapping": {
            "query": "${data.query}",
            "context": "${data.context}",
            "response": "${data.response}"
        }
    }
    
    evaluators["relevance"] = RelevanceEvaluator(model_config)
    evaluator_configs["relevance"] = {
        "column_mapping": {
            "query": "${data.query}",
            "context": "${data.context}",
            "response": "${data.response}"
        }
    }
    
    evaluators["coherence"] = CoherenceEvaluator(model_config)
    evaluator_configs["coherence"] = {
        "column_mapping": {
            "query": "${data.query}",
            "response": "${data.response}"
        }
    }
    
    evaluators["fluency"] = FluencyEvaluator(model_config)
    evaluator_configs["fluency"] = {
        "column_mapping": {
            "query": "${data.query}",
            "context": "${data.context}",
            "response": "${data.response}"
        }
    }
    
    print("✅ Core evaluators initialized successfully")
    
except Exception as e:
    print(f"❌ Error initializing core evaluators: {e}")

# Advanced evaluators (with fallback handling)
try:
    print("🔬 Initializing advanced evaluators...")
    
    # Retrieval evaluator without threshold
    evaluators["retrieval"] = RetrievalEvaluator(model_config=model_config)
    evaluator_configs["retrieval"] = {
        "column_mapping": {
            "query": "${data.query}",
            "context": "${data.context}"
        }
    }
    
    # Custom friendliness evaluator
    evaluators["friendliness"] = FriendlinessEvaluator(azure_model_config)
    evaluator_configs["friendliness"] = {
        "column_mapping": {
            "response": "${data.response}"
        }
    }
    
    # Intent and task evaluators
    evaluators["intent_resolution"] = IntentResolutionEvaluator(azure_model_config)
    evaluator_configs["intent_resolution"] = {
        "column_mapping": {
            "query": "${data.query}",
            "response": "${data.response}"
        }
    }
    
    evaluators["task_adherence"] = TaskAdherenceEvaluator(model_config=azure_model_config)
    evaluator_configs["task_adherence"] = {
        "column_mapping": {
            "query": "${data.query}",
            "response": "${data.response}"
        }
    }
    
    print("✅ Advanced evaluators initialized successfully")
    
except Exception as e:
    print(f"⚠️  Some advanced evaluators failed to initialize: {e}")

# Safety evaluators (require cloud permissions)
try:
    print("🛡️  Initializing safety evaluators...")
    credential = DefaultAzureCredential()
    
    # Remove threshold parameters that cause issues
    evaluators["hate_unfairness"] = HateUnfairnessEvaluator(
        azure_ai_project=azure_ai_project, 
        credential=credential
    )
    evaluator_configs["hate_unfairness"] = {
        "column_mapping": {
            "query": "${data.query}",
            "response": "${data.response}"
        }
    }
    
    evaluators["content_safety"] = ContentSafetyEvaluator(
        azure_ai_project=azure_ai_project, 
        credential=credential
    )
    evaluator_configs["content_safety"] = {
        "column_mapping": {
            "query": "${data.query}",
            "response": "${data.response}"
        }
    }
    
    print("✅ Safety evaluators initialized successfully")
    
except Exception as e:
    print(f"⚠️  Safety evaluators failed (may require additional cloud permissions): {e}")
    print("💡 Continuing with other evaluators...")

print(f"📈 Total evaluators loaded: {len(evaluators)}")

# Deploy to cloud
try:
    print("☁️  Deploying to Azure AI Foundry...")
    
    result = evaluate(
        data="data/sample_data.jsonl",
        evaluators=evaluators,
        evaluator_config=evaluator_configs,
        azure_ai_project=azure_ai_project,
        output_path="./cloud_results_enhanced.json"
    )
    
    print("✅ Enhanced evaluation results deployed to Azure AI Foundry!")
    print(f"📁 Local results saved to: cloud_results_enhanced.json")
    print(f"🌐 Check your Azure AI Foundry project: {azure_ai_project['project_name']}")
    print(f"📊 Deployed {len(result)} evaluation results with {len(evaluators)} evaluators")
    
    # Print summary of which evaluators were used
    print("\n📋 Evaluators successfully deployed:")
    for evaluator_name in evaluators.keys():
        print(f"  ✓ {evaluator_name}")
        
except Exception as e:
    print(f"❌ Cloud deployment failed: {e}")
    print("💡 You may want to check your Azure permissions and project configuration")
    print("🔧 Consider running the fast version first to test basic connectivity") 