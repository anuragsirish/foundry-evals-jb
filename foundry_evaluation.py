#!/usr/bin/env python3
"""
Foundry Evaluation Script

Comprehensive evaluation script that runs all available evaluators organized by categories:
- RAG & Retrieval (3 evaluators)
- Agents (2 evaluators) 
- General Purpose (3 evaluators)
- Safety & Security (2 evaluators)

Total: 10 evaluators across 4 categories
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.evaluation import AzureOpenAIModelConfiguration

# Architecture pipeline evaluators
from azure.ai.evaluation import (
    ContentSafetyEvaluator,
    HateUnfairnessEvaluator,
    RelevanceEvaluator,
    CoherenceEvaluator,
    GroundednessEvaluator,
    FluencyEvaluator,
    RetrievalEvaluator,
)

# Agent evaluators
from azure.ai.evaluation import (
    IntentResolutionEvaluator,
    TaskAdherenceEvaluator,
)

# Custom evaluator
from friendliness.friendliness import FriendlinessEvaluator


class FoundryEvaluation:
    """Comprehensive evaluation framework for Azure AI Foundry agents."""
    
    def __init__(self, config_file: str = ".env"):
        """Initialize the evaluation framework."""
        self.load_configuration(config_file)
        self.setup_azure_config()
        self.setup_model_config()
        self.initialize_evaluators()
        
    def load_configuration(self, config_file: str):
        """Load environment variables and Azure configuration."""
        load_dotenv(config_file, override=True)
        print("🔄 Environment variables loaded from .env file")
        
        # Validate required environment variables
        required_vars = [
            "AZURE_OPENAI_ENDPOINT",
            "AZURE_OPENAI_API_KEY", 
            "AZURE_OPENAI_DEPLOYMENT",
            "AZURE_OPENAI_API_VERSION",
            "AZURE_SUBSCRIPTION_ID",
            "AZURE_RESOURCE_GROUP",
            "AZURE_AI_FOUNDRY_PROJECT"
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
        
        self.azure_ai_project = {
            "subscription_id": os.getenv("AZURE_SUBSCRIPTION_ID"),
            "resource_group_name": os.getenv("AZURE_RESOURCE_GROUP"),
            "project_name": os.getenv("AZURE_AI_FOUNDRY_PROJECT"),
        }
        
        print("✅ Configuration loaded successfully")
        
    def setup_azure_config(self):
        """Setup Azure credentials and configuration."""
        self.credential = DefaultAzureCredential()
        
    def setup_model_config(self):
        """Setup model configuration for evaluators."""
        self.model_config = {
            "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
            "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "azure_deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        }
        
        self.azure_model_config = AzureOpenAIModelConfiguration(
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY")
        )
        
    def initialize_evaluators(self):
        """Initialize all evaluators organized by category."""
        try:
            print("🔧 Initializing evaluators by category...")
            
            # RAG & Retrieval Evaluators (3)
            self.retrieval_evaluator = RetrievalEvaluator(model_config=self.model_config, threshold=3)
            self.groundedness_evaluator = GroundednessEvaluator(self.model_config)
            self.relevance_evaluator = RelevanceEvaluator(self.model_config)
            print("✅ RAG & Retrieval evaluators initialized (3)")
            
            # Agent Evaluators (2)
            self.intent_resolution_evaluator = IntentResolutionEvaluator(self.azure_model_config)
            self.task_adherence_evaluator = TaskAdherenceEvaluator(model_config=self.azure_model_config)
            print("✅ Agent evaluators initialized (2)")
            
            # General Purpose Evaluators (3)
            self.coherence_evaluator = CoherenceEvaluator(self.model_config)
            self.fluency_evaluator = FluencyEvaluator(self.model_config)
            self.friendliness_evaluator = FriendlinessEvaluator(self.azure_model_config)
            print("✅ General Purpose evaluators initialized (3)")
            
            # Safety & Security Evaluators (2)
            self.hate_unfairness_evaluator = HateUnfairnessEvaluator(
                azure_ai_project=self.azure_ai_project, 
                credential=self.credential, 
                threshold=3
            )
            self.content_safety_evaluator = ContentSafetyEvaluator(
                azure_ai_project=self.azure_ai_project, 
                credential=self.credential,
                threshold=3
            )
            print("✅ Safety & Security evaluators initialized (2)")
            
            print("🎯 Total: 10 evaluators across 4 categories")
            
        except Exception as e:
            print(f"❌ Error initializing evaluators: {e}")
            raise

    def load_sample_data(self, data_path: str = "data/sample_data.jsonl") -> List[Dict]:
        """Load and parse the sample data file."""
        try:
            data = []
            with open(data_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
            
            print(f"✅ Loaded {len(data)} samples from {data_path}")
            return data
            
        except FileNotFoundError:
            print(f"❌ File not found: {data_path}")
            raise
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON: {e}")
            raise

    def run_rag_evaluations(self, data: List[Dict]) -> List[Dict]:
        """Run RAG & Retrieval evaluations."""
        print("\n🔍 Running RAG & Retrieval Evaluations...")
        results = []
        
        for i, item in enumerate(data):
            print(f"  Processing item {i+1}/{len(data)}")
            
            query = item.get("query", "")
            context = item.get("context", "")
            response = item.get("response", "")
            
            item_results = {
                "item_index": i,
                "query": query,
                "context": context,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
            
            # Retrieval Evaluation
            try:
                retrieval_result = self.retrieval_evaluator(query=query, context=context)
                item_results["retrieval_eval"] = retrieval_result
            except Exception as e:
                print(f"    Retrieval evaluation error: {e}")
                item_results["retrieval_eval"] = {"error": str(e)}
            
            # Groundedness Evaluation
            try:
                groundedness_result = self.groundedness_evaluator(
                    query=query, 
                    context=context, 
                    response=response
                )
                item_results["groundedness_eval"] = groundedness_result
            except Exception as e:
                print(f"    Groundedness evaluation error: {e}")
                item_results["groundedness_eval"] = {"error": str(e)}
            
            # Relevance Evaluation
            try:
                relevance_result = self.relevance_evaluator(
                    query=query, 
                    context=context, 
                    response=response
                )
                item_results["relevance_eval"] = relevance_result
            except Exception as e:
                print(f"    Relevance evaluation error: {e}")
                item_results["relevance_eval"] = {"error": str(e)}
            
            results.append(item_results)
        
        print(f"✅ RAG evaluations completed for {len(results)} items")
        return results

    def run_agent_evaluations(self, data: List[Dict]) -> List[Dict]:
        """Run Agent evaluations."""
        print("\n🤖 Running Agent Evaluations...")
        results = []
        
        for i, item in enumerate(data):
            print(f"  Processing item {i+1}/{len(data)}")
            
            query = item.get("query", "")
            response = item.get("response", "")
            
            item_results = {
                "item_index": i,
                "query": query,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
            
            # Intent Resolution Evaluation
            try:
                intent_result = self.intent_resolution_evaluator(query=query, response=response)
                item_results["intent_resolution_eval"] = intent_result
                print(f"    Intent Resolution: {intent_result.get('intent_resolution', 'unknown')}")
            except Exception as e:
                print(f"    Intent evaluation error: {e}")
                item_results["intent_resolution_eval"] = {"error": str(e)}
            
            # Task Adherence Evaluation
            try:
                task_result = self.task_adherence_evaluator(query=query, response=response)
                item_results["task_adherence_eval"] = task_result
                print(f"    Task Adherence: {task_result.get('task_adherence', 'unknown')}")
            except Exception as e:
                print(f"    Task evaluation error: {e}")
                item_results["task_adherence_eval"] = {"error": str(e)}
            
            results.append(item_results)
        
        print(f"✅ Agent evaluations completed for {len(results)} items")
        return results

    def run_general_purpose_evaluations(self, data: List[Dict]) -> List[Dict]:
        """Run General Purpose evaluations."""
        print("\n🎯 Running General Purpose Evaluations...")
        results = []
        
        for i, item in enumerate(data):
            print(f"  Processing item {i+1}/{len(data)}")
            
            query = item.get("query", "")
            context = item.get("context", "")
            response = item.get("response", "")
            
            item_results = {
                "item_index": i,
                "query": query,
                "context": context,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
            
            # Coherence Evaluation
            try:
                coherence_result = self.coherence_evaluator(query=query, response=response)
                item_results["coherence_eval"] = coherence_result
            except Exception as e:
                print(f"    Coherence evaluation error: {e}")
                item_results["coherence_eval"] = {"error": str(e)}
            
            # Fluency Evaluation
            try:
                fluency_result = self.fluency_evaluator(
                    query=query, 
                    context=context, 
                    response=response
                )
                item_results["fluency_eval"] = fluency_result
            except Exception as e:
                print(f"    Fluency evaluation error: {e}")
                item_results["fluency_eval"] = {"error": str(e)}
            
            # Friendliness Evaluation
            try:
                friendliness_result = self.friendliness_evaluator(response=response)
                item_results["friendliness_eval"] = friendliness_result
            except Exception as e:
                print(f"    Friendliness evaluation error: {e}")
                item_results["friendliness_eval"] = {"error": str(e)}
            
            results.append(item_results)
        
        print(f"✅ General Purpose evaluations completed for {len(results)} items")
        return results

    def run_safety_evaluations(self, data: List[Dict]) -> List[Dict]:
        """Run Safety & Security evaluations."""
        print("\n🛡️ Running Safety & Security Evaluations...")
        results = []
        
        for i, item in enumerate(data):
            print(f"  Processing item {i+1}/{len(data)}")
            
            query = item.get("query", "")
            response = item.get("response", "")
            
            item_results = {
                "item_index": i,
                "query": query,
                "response": response,
                "timestamp": datetime.now().isoformat()
            }
            
            # Hate/Unfairness Evaluation
            try:
                hate_result = self.hate_unfairness_evaluator(query=query, response=response)
                item_results["hate_unfairness_eval"] = hate_result
                print(f"    Hate/Unfairness: {hate_result.get('hate_unfairness_result', 'unknown')} (score: {hate_result.get('hate_unfairness_score', 'N/A')})")
            except Exception as e:
                print(f"    Hate evaluation error: {e}")
                item_results["hate_unfairness_eval"] = {"error": str(e)}
            
            # Content Safety Composite Evaluation (includes Violence, Sexual, Self-Harm, Hate)
            try:
                safety_result = self.content_safety_evaluator(query=query, response=response)
                item_results["content_safety_eval"] = safety_result
                
                # Display detailed results from composite evaluator
                print(f"    Content Safety Composite:")
                print(f"      Hate: {safety_result.get('hate_unfairness', 'N/A')} (score: {safety_result.get('hate_unfairness_score', 'N/A')})")
                print(f"      Sexual: {safety_result.get('sexual', 'N/A')} (score: {safety_result.get('sexual_score', 'N/A')})")
                print(f"      Violence: {safety_result.get('violence', 'N/A')} (score: {safety_result.get('violence_score', 'N/A')})")
                print(f"      Self-Harm: {safety_result.get('self_harm', 'N/A')} (score: {safety_result.get('self_harm_score', 'N/A')})")
                
                # Check overall safety
                safety_checks = ['hate_unfairness_result', 'sexual_result', 'violence_result', 'self_harm_result']
                all_safe = all(safety_result.get(check) == 'pass' for check in safety_checks if check in safety_result)
                print(f"      Overall Safe: {all_safe}")
            except Exception as e:
                print(f"    Content Safety Composite error: {e}")
                item_results["content_safety_eval"] = {"error": str(e)}
            
            results.append(item_results)
        
        print(f"✅ Safety evaluations completed for {len(results)} items")
        return results

    def save_results(self, results: List[Dict], category: str, timestamp: str) -> str:
        """Save evaluation results to JSONL file."""
        output_dir = "evaluation_results"
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = f"{output_dir}/foundry_{category.lower().replace(' & ', '_').replace(' ', '_')}_results_{timestamp}.jsonl"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(json.dumps(result) + '\n')
        
        print(f"✅ {category} results saved to: {output_file}")
        return output_file

    def run_comprehensive_evaluation(self, data_path: str = "data/sample_data.jsonl"):
        """Run all evaluations and save results by category."""
        print("🚀 Foundry Comprehensive Evaluation")
        print("=" * 50)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Load data
        data = self.load_sample_data(data_path)
        
        # Run evaluations by category
        categories_results = {}
        
        # 1. RAG & Retrieval (3 evaluators)
        rag_results = self.run_rag_evaluations(data)
        rag_file = self.save_results(rag_results, "RAG & Retrieval", timestamp)
        categories_results["rag_retrieval"] = {"file": rag_file, "count": len(rag_results)}
        
        # 2. Agents (2 evaluators)
        agent_results = self.run_agent_evaluations(data)
        agent_file = self.save_results(agent_results, "Agents", timestamp)
        categories_results["agents"] = {"file": agent_file, "count": len(agent_results)}
        
        # 3. General Purpose (3 evaluators)
        general_results = self.run_general_purpose_evaluations(data)
        general_file = self.save_results(general_results, "General Purpose", timestamp)
        categories_results["general_purpose"] = {"file": general_file, "count": len(general_results)}
        
        # 4. Safety & Security (3 evaluators)
        safety_results = self.run_safety_evaluations(data)
        safety_file = self.save_results(safety_results, "Safety & Security", timestamp)
        categories_results["safety_security"] = {"file": safety_file, "count": len(safety_results)}
        
        # Summary
        print(f"\n🎉 Foundry Evaluation Complete!")
        print(f"📊 Evaluation Summary:")
        print(f"   RAG & Retrieval: 3 evaluators → {categories_results['rag_retrieval']['file']}")
        print(f"   Agents: 2 evaluators → {categories_results['agents']['file']}")
        print(f"   General Purpose: 3 evaluators → {categories_results['general_purpose']['file']}")
        print(f"   Safety & Security: 2 evaluators → {categories_results['safety_security']['file']}")
        print(f"   Total: 10 evaluators across 4 categories")
        
        return categories_results


def main():
    """Main function to run the foundry evaluation."""
    try:
        evaluator = FoundryEvaluation()
        results = evaluator.run_comprehensive_evaluation()
        
        print(f"\n✅ All evaluations completed successfully!")
        print(f"📁 Check the 'evaluation_results' directory for category-specific results.")
        
        return 0
        
    except Exception as e:
        print(f"❌ Foundry evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main()) 