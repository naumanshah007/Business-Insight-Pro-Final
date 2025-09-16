#!/usr/bin/env python3
"""
Production-Ready GenAI Client for BusinessInsightsPro
Features:
- Consistent responses with temperature control
- Intelligent fallbacks between models
- Caching for repeated queries
- Error handling and retry logic
- Business-focused prompting
"""

import json
import time
import hashlib
from typing import Dict, List, Optional, Any
from openai import OpenAI
import streamlit as st

class GenAIClient:
    """Production-ready GenAI client with consistency controls"""
    
    def __init__(self, api_key: str = "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"):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        
        # Model configuration with consistency settings
        self.models = {
            "primary": {
                "id": "openai/gpt-oss-20b:free",
                "name": "OpenAI 20B",
                "temperature": 0.3,  # Low temperature for consistency
                "max_tokens": 800,
                "strengths": ["business_insights", "sentiment", "chart_interpretation"]
            },
            "secondary": {
                "id": "deepseek/deepseek-chat-v3.1:free", 
                "name": "DeepSeek V3.1",
                "temperature": 0.2,  # Even lower for reasoning tasks
                "max_tokens": 1000,
                "strengths": ["reasoning", "pattern_recognition", "custom_analysis"]
            },
            "fallback": {
                "id": "mistralai/mistral-7b-instruct:free",
                "name": "Mistral 7B",
                "temperature": 0.4,
                "max_tokens": 600,
                "strengths": ["general", "fast", "reliable"]
            }
        }
        
        # Cache for consistent responses
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache
        
        # Business context templates for consistency
        self.business_context = {
            "retail": {
                "domain_knowledge": "retail e-commerce business",
                "key_metrics": ["revenue", "profit margin", "customer acquisition", "retention"],
                "common_challenges": ["inventory management", "pricing optimization", "customer churn"]
            },
            "real_estate": {
                "domain_knowledge": "real estate market",
                "key_metrics": ["property values", "market trends", "agent performance", "time on market"],
                "common_challenges": ["market volatility", "pricing accuracy", "client satisfaction"]
            }
        }
    
    def _get_cache_key(self, prompt: str, model_id: str, context: str = "") -> str:
        """Generate consistent cache key"""
        content = f"{prompt}|{model_id}|{context}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[str]:
        """Get cached response if still valid"""
        if cache_key in self.cache:
            cached_time, response = self.cache[cache_key]
            if time.time() - cached_time < self.cache_ttl:
                return response
            else:
                del self.cache[cache_key]
        return None
    
    def _cache_response(self, cache_key: str, response: str):
        """Cache response with timestamp"""
        self.cache[cache_key] = (time.time(), response)
    
    def _build_consistent_prompt(self, task_type: str, data_context: Dict, domain: str = "retail") -> str:
        """Build consistent prompts with business context"""
        
        base_instructions = f"""
You are a senior business analyst specializing in {self.business_context[domain]['domain_knowledge']}.
Your role is to provide consistent, actionable insights based on data analysis.

CRITICAL CONSISTENCY REQUIREMENTS:
- Use the same analytical framework for similar data patterns
- Maintain consistent terminology and metrics focus
- Provide structured insights with clear action items
- Avoid dramatic variations in interpretation of similar data
- Focus on {', '.join(self.business_context[domain]['key_metrics'])} as primary metrics

RESPONSE FORMAT:
1. Key Finding (1-2 sentences)
2. Business Impact (quantified when possible)
3. Actionable Recommendations (2-3 specific steps)
4. Risk/Opportunity Assessment

"""
        
        if task_type == "insights_generation":
            return f"""{base_instructions}
            
TASK: Generate business insights for the following analysis results:

DATA CONTEXT:
{json.dumps(data_context, indent=2)}

DOMAIN: {domain.title()}

Provide insights that are:
- Data-driven and specific to the numbers shown
- Actionable for business decision-making
- Consistent with industry best practices
- Focused on growth and optimization opportunities

"""
        
        elif task_type == "sentiment_analysis":
            return f"""{base_instructions}
            
TASK: Analyze customer sentiment and provide actionable feedback insights:

SENTIMENT DATA:
{json.dumps(data_context, indent=2)}

DOMAIN: {domain.title()}

Focus on:
- Identifying specific improvement areas
- Quantifying sentiment impact on business metrics
- Providing concrete steps to address negative feedback
- Highlighting positive feedback patterns to leverage

"""
        
        elif task_type == "question_generation":
            return f"""{base_instructions}
            
TASK: Generate relevant business questions based on available data:

DATA STRUCTURE:
{json.dumps(data_context, indent=2)}

DOMAIN: {domain.title()}

Generate 3-5 specific, actionable questions that:
- Leverage the available data columns
- Focus on key business metrics for {domain}
- Are relevant to common business challenges
- Can be answered with data analysis

"""
        
        elif task_type == "data_profiling":
            return f"""{base_instructions}
            
TASK: Analyze data quality and provide column mapping recommendations:

DATA PROFILE:
{json.dumps(data_context, indent=2)}

DOMAIN: {domain.title()}

Provide:
- Column mapping suggestions with confidence scores
- Data quality assessment
- Missing data impact analysis
- Recommendations for data improvement

"""
        
        return base_instructions
    
    def _call_model(self, model_config: Dict, prompt: str, retries: int = 2) -> Optional[str]:
        """Call a specific model with retry logic"""
        for attempt in range(retries + 1):
            try:
                completion = self.client.chat.completions.create(
                    model=model_config["id"],
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional business analyst. Provide clear, actionable, and consistent insights."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    temperature=model_config["temperature"],
                    max_tokens=model_config["max_tokens"]
                )
                
                response = completion.choices[0].message.content.strip()
                return response
                
            except Exception as e:
                if attempt < retries:
                    time.sleep(1)  # Brief delay before retry
                    continue
                else:
                    print(f"Model {model_config['name']} failed after {retries + 1} attempts: {e}")
                    return None
        
        return None
    
    def generate_insights(self, analysis_data: Dict, domain: str = "retail", question_type: str = "general") -> str:
        """Generate consistent business insights from analysis results"""
        
        # Determine best model for task
        if question_type in ["sentiment", "chart_interpretation"]:
            primary_model = "primary"
        elif question_type in ["reasoning", "custom_analysis"]:
            primary_model = "secondary"
        else:
            primary_model = "primary"
        
        # Build consistent prompt
        prompt = self._build_consistent_prompt("insights_generation", analysis_data, domain)
        
        # Check cache first
        cache_key = self._get_cache_key(prompt, self.models[primary_model]["id"], f"{domain}_{question_type}")
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            return cached_response
        
        # Try models in order of preference
        models_to_try = [primary_model, "secondary", "fallback"]
        
        for model_key in models_to_try:
            model_config = self.models[model_key]
            response = self._call_model(model_config, prompt)
            
            if response:
                # Cache successful response
                self._cache_response(cache_key, response)
                return response
        
        # Fallback to static response if all models fail
        return self._get_fallback_insights(analysis_data, domain)
    
    def analyze_sentiment(self, sentiment_data: Dict, domain: str = "retail") -> str:
        """Enhanced sentiment analysis with GenAI insights"""
        
        prompt = self._build_consistent_prompt("sentiment_analysis", sentiment_data, domain)
        
        # Check cache
        cache_key = self._get_cache_key(prompt, self.models["primary"]["id"], f"sentiment_{domain}")
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            return cached_response
        
        # Try primary model (best for sentiment)
        response = self._call_model(self.models["primary"], prompt)
        
        if response:
            self._cache_response(cache_key, response)
            return response
        
        # Fallback
        return self._get_fallback_sentiment_analysis(sentiment_data, domain)
    
    def generate_questions(self, data_structure: Dict, domain: str = "retail") -> List[str]:
        """Generate relevant business questions based on data structure"""
        
        prompt = self._build_consistent_prompt("question_generation", data_structure, domain)
        
        # Check cache
        cache_key = self._get_cache_key(prompt, self.models["secondary"]["id"], f"questions_{domain}")
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            try:
                return json.loads(cached_response)
            except:
                pass
        
        # Try secondary model (best for reasoning)
        response = self._call_model(self.models["secondary"], prompt)
        
        if response:
            try:
                # Try to parse as JSON first
                questions = json.loads(response)
                if isinstance(questions, list):
                    self._cache_response(cache_key, response)
                    return questions
            except:
                # Parse as text if not JSON
                questions = [q.strip() for q in response.split('\n') if q.strip()]
                if questions:
                    self._cache_response(cache_key, json.dumps(questions))
                    return questions
        
        # Fallback
        return self._get_fallback_questions(domain)
    
    def profile_data(self, data_profile: Dict, domain: str = "retail") -> Dict:
        """Intelligent data profiling with GenAI recommendations"""
        
        prompt = self._build_consistent_prompt("data_profiling", data_profile, domain)
        
        # Check cache
        cache_key = self._get_cache_key(prompt, self.models["secondary"]["id"], f"profile_{domain}")
        cached_response = self._get_cached_response(cache_key)
        if cached_response:
            try:
                return json.loads(cached_response)
            except:
                pass
        
        # Try secondary model (best for pattern recognition)
        response = self._call_model(self.models["secondary"], prompt)
        
        if response:
            try:
                profile_result = json.loads(response)
                self._cache_response(cache_key, response)
                return profile_result
            except:
                # Return structured response even if not JSON
                return {
                    "mapping_suggestions": {},
                    "quality_assessment": response,
                    "recommendations": []
                }
        
        # Fallback
        return self._get_fallback_data_profile(data_profile, domain)
    
    def _get_fallback_insights(self, analysis_data: Dict, domain: str) -> str:
        """Fallback insights when GenAI is unavailable"""
        return f"""
### 📊 Business Insights Summary

Based on the analysis results, here are the key findings:

**Key Metrics:** The data shows important patterns in your {domain} business performance.

**Business Impact:** These insights can help optimize operations and drive growth.

**Recommendations:** 
1. Monitor these metrics regularly
2. Investigate any significant trends or outliers
3. Consider implementing targeted improvements

*Note: Enhanced AI insights are temporarily unavailable. Basic analysis results are shown above.*
"""
    
    def _get_fallback_sentiment_analysis(self, sentiment_data: Dict, domain: str) -> str:
        """Fallback sentiment analysis"""
        return f"""
### 💬 Customer Sentiment Overview

**Overall Sentiment:** Based on the available feedback data.

**Key Themes:** Customer feedback patterns have been identified.

**Action Items:**
1. Address any negative feedback themes
2. Leverage positive feedback for marketing
3. Implement regular sentiment monitoring

*Note: Enhanced sentiment analysis is temporarily unavailable.*
"""
    
    def _get_fallback_questions(self, domain: str) -> List[str]:
        """Fallback questions when GenAI is unavailable"""
        if domain == "retail":
            return [
                "What are the top-performing products by revenue?",
                "How has customer acquisition changed over time?",
                "What is the average order value trend?",
                "Which sales channels are most effective?",
                "What is the customer retention rate?"
            ]
        else:
            return [
                "What are the top-performing locations by sales value?",
                "How have property prices changed over time?",
                "What is the average time on market?",
                "Which agents have the best performance?",
                "What is the market trend analysis?"
            ]
    
    def _get_fallback_data_profile(self, data_profile: Dict, domain: str) -> Dict:
        """Fallback data profiling"""
        return {
            "mapping_suggestions": {},
            "quality_assessment": "Data quality analysis completed with basic checks.",
            "recommendations": [
                "Ensure all required fields are mapped",
                "Check for missing values in key columns",
                "Verify data types are appropriate"
            ]
        }
    
    def clear_cache(self):
        """Clear the response cache"""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            "cached_responses": len(self.cache),
            "cache_ttl": self.cache_ttl,
            "models_available": len(self.models)
        }

# Global instance for the app
@st.cache_resource
def get_genai_client():
    """Get cached GenAI client instance"""
    return GenAIClient()

# Convenience functions for easy integration
def generate_business_insights(analysis_data: Dict, domain: str = "retail", question_type: str = "general") -> str:
    """Generate business insights using GenAI"""
    client = get_genai_client()
    return client.generate_insights(analysis_data, domain, question_type)

def analyze_customer_sentiment(sentiment_data: Dict, domain: str = "retail") -> str:
    """Analyze customer sentiment using GenAI"""
    client = get_genai_client()
    return client.analyze_sentiment(sentiment_data, domain)

def generate_smart_questions(data_structure: Dict, domain: str = "retail") -> List[str]:
    """Generate smart business questions using GenAI"""
    client = get_genai_client()
    return client.generate_questions(data_structure, domain)

def profile_data_intelligently(data_profile: Dict, domain: str = "retail") -> Dict:
    """Profile data intelligently using GenAI"""
    client = get_genai_client()
    return client.profile_data(data_profile, domain)
