#!/usr/bin/env python3
"""
DataGenie - Intelligent Data Chatbot
AI-powered chatbot that answers any question about uploaded data
"""

import streamlit as st
import pandas as pd
import json
import sqlite3
from typing import Dict, List, Any, Optional
import re
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from genai_client import generate_business_insights
from data_profiler import AdvancedDataProfiler

class DataGenieChatbot:
    """Intelligent chatbot for data analysis and insights"""
    
    def __init__(self):
        self.profiler = AdvancedDataProfiler()
        self.conversation_history = []
        self.data_context = {}
        self.knowledge_base = {}
        
    def initialize_session(self, df: pd.DataFrame, business_type: str = "general"):
        """Initialize chatbot session with data"""
        # Create comprehensive data profile
        self.data_context = self.profiler.create_comprehensive_profile(df, business_type)
        
        # Store in session state
        if 'datagenie_context' not in st.session_state:
            st.session_state.datagenie_context = self.data_context
        
        if 'datagenie_history' not in st.session_state:
            st.session_state.datagenie_history = []
        
        # Initialize conversation
        self.conversation_history = st.session_state.datagenie_history
        self.data_context = st.session_state.datagenie_context
        
        return self.data_context
    
    def process_question(self, question: str, df: pd.DataFrame) -> Dict[str, Any]:
        """Process user question and generate intelligent response"""
        
        # Add to conversation history
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "user",
            "content": question
        })
        
        # Get relevant context for the question
        context = self.profiler.get_context_for_question(question, self.data_context)
        
        # Determine question type and generate response
        response = self._generate_intelligent_response(question, df, context)
        
        # Add response to conversation history
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "type": "assistant",
            "content": response["answer"],
            "data_used": response.get("data_used", {}),
            "confidence": response.get("confidence", 0.8)
        })
        
        # Update session state
        st.session_state.datagenie_history = self.conversation_history
        
        return response
    
    def _generate_intelligent_response(self, question: str, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate intelligent response based on question type with enhanced prompt engineering"""
        
        question_lower = question.lower()
        
        # Enhanced question categorization with more sophisticated analysis
        question_type, question_intent = self._categorize_question_advanced(question_lower)
        
        # Debug: Print question type for troubleshooting (commented out for production)
        # print(f"DEBUG: Question '{question}' -> Type: {question_type}, Intent: {question_intent}")
        
        # Build comprehensive context for AI
        enhanced_context = self._build_enhanced_context(question, df, context, question_type, question_intent)
        
        # Generate response based on type with sophisticated prompts
        if question_type == "data_overview":
            return self._handle_data_overview_question_enhanced(question, df, enhanced_context)
        elif question_type == "statistical":
            return self._handle_statistical_question_enhanced(question, df, enhanced_context)
        elif question_type == "trend_analysis":
            return self._handle_trend_question_enhanced(question, df, enhanced_context)
        elif question_type == "comparison":
            return self._handle_comparison_question_enhanced(question, df, enhanced_context)
        elif question_type == "prediction":
            return self._handle_prediction_question_enhanced(question, df, enhanced_context)
        elif question_type == "data_quality":
            return self._handle_data_quality_question_enhanced(question, df, enhanced_context)
        elif question_type == "business_insights":
            return self._handle_business_insights_question(question, df, enhanced_context)
        elif question_type == "customer_analysis":
            return self._handle_customer_analysis_question(question, df, enhanced_context)
        elif question_type == "product_analysis":
            return self._handle_product_analysis_question(question, df, enhanced_context)
        else:
            return self._handle_general_question_enhanced(question, df, enhanced_context)
    
    def _categorize_question_advanced(self, question: str) -> tuple:
        """Enhanced question categorization with intent analysis"""
        
        # Business-specific keywords
        business_keywords = {
            'revenue': ['revenue', 'income', 'sales', 'profit', 'earnings', 'money', 'financial'],
            'customer': ['customer', 'client', 'buyer', 'user', 'patron', 'visitor'],
            'product': ['product', 'item', 'service', 'menu', 'dish', 'sku', 'inventory'],
            'performance': ['performance', 'efficiency', 'productivity', 'success', 'growth'],
            'market': ['market', 'competition', 'competitor', 'industry', 'sector'],
            'operational': ['operation', 'process', 'workflow', 'procedure', 'system']
        }
        
        # Question intent analysis
        intent_keywords = {
            'what': ['what', 'which', 'who'],
            'how': ['how', 'why', 'explain'],
            'when': ['when', 'time', 'schedule', 'timing'],
            'where': ['where', 'location', 'place'],
            'how_much': ['how much', 'how many', 'quantity', 'amount', 'number'],
            'compare': ['compare', 'vs', 'versus', 'difference', 'better', 'worse', 'best', 'worst'],
            'trend': ['trend', 'change', 'over time', 'growth', 'decline', 'pattern', 'increase', 'decrease'],
            'predict': ['predict', 'forecast', 'future', 'next', 'will', 'expect', 'projection'],
            'analyze': ['analyze', 'analysis', 'insight', 'findings', 'discover']
        }
        
        # Determine business domain
        business_domain = "general"
        for domain, keywords in business_keywords.items():
            if any(keyword in question for keyword in keywords):
                business_domain = domain
                break
        
        # Determine question intent
        question_intent = "general"
        for intent, keywords in intent_keywords.items():
            if any(keyword in question for keyword in keywords):
                question_intent = intent
                break
        
        # Determine question type based on combination (prioritize specific terms first)
        if any(word in question for word in ['trend', 'change', 'over time', 'growth', 'decline', 'pattern', 'increasing', 'decreasing']):
            question_type = "trend_analysis"
        elif any(word in question for word in ['compare', 'vs', 'versus', 'difference', 'better', 'worse', 'best', 'worst']):
            question_type = "comparison"
        elif any(word in question for word in ['predict', 'forecast', 'future', 'next', 'will', 'expect', 'projection']):
            question_type = "prediction"
        elif any(word in question for word in ['average', 'mean', 'median', 'total', 'sum', 'count', 'statistics']):
            question_type = "statistical"
        elif any(word in question for word in ['missing', 'null', 'quality', 'error', 'issue']):
            question_type = "data_quality"
        elif business_domain == "customer":
            question_type = "customer_analysis"
        elif business_domain == "product":
            question_type = "product_analysis"
        elif business_domain in ["revenue", "performance", "market", "operational"]:
            question_type = "business_insights"
        elif any(word in question for word in ['overview', 'summary', 'tell me about', 'describe', 'explain']):
            question_type = "data_overview"
        else:
            question_type = "general"
        
        return question_type, {
            "intent": question_intent,
            "business_domain": business_domain,
            "keywords_found": [word for word in question.split() if len(word) > 3]
        }
    
    def _build_enhanced_context(self, question: str, df: pd.DataFrame, context: Dict[str, Any], 
                               question_type: str, question_intent: Dict[str, Any]) -> Dict[str, Any]:
        """Build comprehensive context for AI analysis"""
        
        # Extract relevant data based on question type
        relevant_data = self._extract_relevant_data(question, df, question_type)
        
        # Build conversation context
        conversation_context = self._build_conversation_context()
        
        # Enhanced context structure
        enhanced_context = {
            "question": question,
            "question_type": question_type,
            "question_intent": question_intent,
            "business_type": self.data_context["metadata"]["business_type"],
            "data_summary": {
                "total_records": len(df),
                "total_columns": len(df.columns),
                "column_names": df.columns.tolist(),
                "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "memory_usage": df.memory_usage(deep=True).sum()
            },
            "relevant_data": relevant_data,
            "data_quality": self.data_context["data_quality"],
            "business_insights": self.data_context["business_insights"],
            "conversation_context": conversation_context,
            "sample_data": df.head(5).to_dict('records'),
            "column_analysis": self.data_context["column_analysis"],
            "quick_facts": self.data_context["quick_facts"]
        }
        
        return enhanced_context
    
    def _extract_relevant_data(self, question: str, df: pd.DataFrame, question_type: str) -> Dict[str, Any]:
        """Extract relevant data based on question type and content"""
        
        relevant_data = {}
        
        # Extract numeric columns for statistical analysis
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            relevant_data["numeric_columns"] = numeric_cols
            relevant_data["numeric_summary"] = df[numeric_cols].describe().to_dict()
        
        # Extract categorical columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if categorical_cols:
            relevant_data["categorical_columns"] = categorical_cols
            relevant_data["categorical_summary"] = {}
            for col in categorical_cols[:5]:  # Limit to first 5 categorical columns
                relevant_data["categorical_summary"][col] = {
                    "unique_count": df[col].nunique(),
                    "top_values": df[col].value_counts().head(5).to_dict()
                }
        
        # Extract date columns
        date_cols = [col for col in df.columns if any(keyword in col.lower() 
                    for keyword in ['date', 'time', 'created', 'purchase', 'order', 'timestamp'])]
        if date_cols:
            relevant_data["date_columns"] = date_cols
            try:
                df_temp = df.copy()
                df_temp[date_cols[0]] = pd.to_datetime(df_temp[date_cols[0]], errors='coerce')
                date_range = df_temp[date_cols[0]].dropna()
                if len(date_range) > 0:
                    relevant_data["date_range"] = {
                        "start": date_range.min().isoformat(),
                        "end": date_range.max().isoformat(),
                        "span_days": (date_range.max() - date_range.min()).days
                    }
            except:
                pass
        
        # Extract amount/revenue columns
        amount_cols = [col for col in df.columns if any(keyword in col.lower() 
                      for keyword in ['amount', 'price', 'total', 'revenue', 'cost', 'value', 'sales'])]
        if amount_cols:
            relevant_data["amount_columns"] = amount_cols
            relevant_data["financial_summary"] = {}
            for col in amount_cols:
                if pd.api.types.is_numeric_dtype(df[col]):
                    relevant_data["financial_summary"][col] = {
                        "total": df[col].sum(),
                        "average": df[col].mean(),
                        "median": df[col].median(),
                        "min": df[col].min(),
                        "max": df[col].max()
                    }
        
        return relevant_data
    
    def _build_conversation_context(self) -> Dict[str, Any]:
        """Build context from conversation history"""
        
        if not self.conversation_history:
            return {"previous_questions": [], "context_continuity": False}
        
        # Get last 3 questions for context
        recent_questions = [q for q in self.conversation_history[-6:] if q["type"] == "user"]
        recent_answers = [a for a in self.conversation_history[-6:] if a["type"] == "assistant"]
        
        return {
            "previous_questions": [q["content"] for q in recent_questions[-3:]],
            "previous_answers": [a["content"][:200] + "..." if len(a["content"]) > 200 else a["content"] 
                               for a in recent_answers[-3:]],
            "context_continuity": len(recent_questions) > 0,
            "conversation_length": len(self.conversation_history)
        }
    
    def _handle_data_overview_question_enhanced(self, question: str, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced data overview with sophisticated prompt engineering"""
        
        # Build comprehensive prompt for AI
        prompt_context = {
            "role": "You are DataGenie, an expert business data analyst with deep expertise in data interpretation and business intelligence.",
            "task": "Provide a comprehensive, insightful overview of the uploaded business data",
            "context": {
                "business_type": context["business_type"],
                "data_scale": f"{context['data_summary']['total_records']:,} records across {context['data_summary']['total_columns']} columns",
                "data_quality_score": context["data_quality"]["quality_score"],
                "key_insights": context["business_insights"]["key_metrics"],
                "quick_facts": context["quick_facts"][:5]
            },
            "user_question": question,
            "conversation_context": context["conversation_context"],
            "sample_data": context["sample_data"][:3]
        }
        
        try:
            # Generate sophisticated AI response
            ai_response = self._generate_sophisticated_response(prompt_context, "data_overview")
            
            # Format response with rich structure
            answer = f"### 📊 **Comprehensive Data Overview**\n\n"
            answer += f"**Business Type:** {context['business_type'].title()}\n"
            answer += f"**Data Scale:** {context['data_summary']['total_records']:,} records across {context['data_summary']['total_columns']} columns\n"
            answer += f"**Data Quality Score:** {context['data_quality']['quality_score']}/100\n\n"
            
            answer += f"**🧠 AI Analysis:**\n{ai_response}\n\n"
            
            # Add structured insights
            answer += "**📈 Key Insights:**\n"
            for metric, value in context["business_insights"]["key_metrics"].items():
                answer += f"• **{metric.replace('_', ' ').title()}:** {value}\n"
            
            answer += "\n**💡 Quick Facts:**\n"
            for fact in context["quick_facts"][:5]:
                answer += f"• {fact}\n"
            
            return {
                "answer": answer,
                "data_used": {
                    "records_analyzed": context['data_summary']['total_records'],
                    "columns_analyzed": context['data_summary']['total_columns'],
                    "ai_analysis": True
                },
                "confidence": 0.95
            }
            
        except Exception as e:
            # Fallback to structured overview
            answer = f"### 📊 **Data Overview**\n\n"
            answer += f"**Business Type:** {context['business_type'].title()}\n"
            answer += f"**Dataset Size:** {context['data_summary']['total_records']:,} records, {context['data_summary']['total_columns']} columns\n"
            answer += f"**Data Quality:** {context['data_quality']['quality_score']}/100\n\n"
            
            answer += "**Key Metrics:**\n"
            for metric, value in context["business_insights"]["key_metrics"].items():
                answer += f"• {metric.replace('_', ' ').title()}: {value}\n"
            
            return {
                "answer": answer,
                "data_used": {"records_analyzed": context['data_summary']['total_records']},
                "confidence": 0.8
            }
    
    def _handle_statistical_question_enhanced(self, question: str, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced statistical analysis with sophisticated prompts"""
        
        numeric_data = context["relevant_data"].get("numeric_summary", {})
        financial_data = context["relevant_data"].get("financial_summary", {})
        
        if not numeric_data and not financial_data:
            return {
                "answer": "❌ **No Numeric Data Found**\n\nI couldn't find any numeric columns in your dataset for statistical analysis. Please ensure your data contains numeric fields like amounts, prices, quantities, or counts.",
                "confidence": 0.1
            }
        
        # Build sophisticated statistical prompt
        prompt_context = {
            "role": "You are DataGenie, a statistical analysis expert specializing in business data interpretation.",
            "task": "Provide detailed statistical analysis with business context and actionable insights",
            "context": {
                "business_type": context["business_type"],
                "question": question,
                "statistical_data": numeric_data,
                "financial_data": financial_data,
                "data_scale": f"{context['data_summary']['total_records']:,} records"
            },
            "analysis_requirements": [
                "Provide clear statistical interpretations",
                "Explain business implications",
                "Identify patterns and outliers",
                "Suggest actionable insights",
                "Use professional business language"
            ]
        }
        
        try:
            ai_response = self._generate_sophisticated_response(prompt_context, "statistical_analysis")
            
            answer = f"### 📈 **Advanced Statistical Analysis**\n\n"
            answer += f"**Business Context:** {context['business_type'].title()} Analysis\n"
            answer += f"**Data Points:** {context['data_summary']['total_records']:,} records\n\n"
            
            answer += f"**🧠 AI Statistical Interpretation:**\n{ai_response}\n\n"
            
            # Add detailed statistics
            if financial_data:
                answer += "**💰 Financial Summary:**\n"
                for col, stats in financial_data.items():
                    answer += f"**{col.title()}:**\n"
                    answer += f"• Total: ${stats['total']:,.2f}\n"
                    answer += f"• Average: ${stats['average']:,.2f}\n"
                    answer += f"• Median: ${stats['median']:,.2f}\n"
                    answer += f"• Range: ${stats['min']:,.2f} - ${stats['max']:,.2f}\n\n"
            
            return {
                "answer": answer,
                "data_used": {
                    "numeric_columns": list(numeric_data.keys()) if numeric_data else [],
                    "financial_columns": list(financial_data.keys()) if financial_data else [],
                    "ai_analysis": True
                },
                "confidence": 0.9
            }
            
        except Exception as e:
            # Fallback statistical analysis
            answer = f"### 📈 **Statistical Analysis**\n\n"
            if financial_data:
                for col, stats in financial_data.items():
                    answer += f"**{col.title()}:**\n"
                    answer += f"• Total: ${stats['total']:,.2f}\n"
                    answer += f"• Average: ${stats['average']:,.2f}\n"
                    answer += f"• Median: ${stats['median']:,.2f}\n\n"
            
            return {
                "answer": answer,
                "data_used": {"statistical_analysis": True},
                "confidence": 0.7
            }
    
    def _handle_business_insights_question(self, question: str, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle business insights questions with sophisticated analysis"""
        
        # Build comprehensive business analysis prompt
        prompt_context = {
            "role": "You are DataGenie, a senior business analyst with expertise in strategic business intelligence and data-driven decision making.",
            "task": "Provide strategic business insights and recommendations based on the data analysis",
            "context": {
                "business_type": context["business_type"],
                "question": question,
                "business_metrics": context["business_insights"]["key_metrics"],
                "data_quality": context["data_quality"]["quality_score"],
                "financial_summary": context["relevant_data"].get("financial_summary", {}),
                "conversation_history": context["conversation_context"]
            },
            "analysis_framework": [
                "SWOT analysis perspective",
                "Strategic recommendations",
                "Risk assessment",
                "Opportunity identification",
                "Performance benchmarking",
                "Actionable next steps"
            ]
        }
        
        try:
            ai_response = self._generate_sophisticated_response(prompt_context, "business_insights")
            
            answer = f"### 🎯 **Strategic Business Insights**\n\n"
            answer += f"**Business Type:** {context['business_type'].title()}\n"
            answer += f"**Analysis Date:** {datetime.now().strftime('%Y-%m-%d')}\n\n"
            
            answer += f"**🧠 AI Strategic Analysis:**\n{ai_response}\n\n"
            
            # Add key metrics
            answer += "**📊 Key Performance Indicators:**\n"
            for metric, value in context["business_insights"]["key_metrics"].items():
                answer += f"• **{metric.replace('_', ' ').title()}:** {value}\n"
            
            return {
                "answer": answer,
                "data_used": {
                    "business_metrics": context["business_insights"]["key_metrics"],
                    "strategic_analysis": True
                },
                "confidence": 0.9
            }
            
        except Exception as e:
            return {
                "answer": f"### 🎯 **Business Insights**\n\nBased on your {context['business_type']} data:\n\n{context['business_insights']['key_metrics']}\n\nFor deeper insights, please ask more specific questions about your business performance.",
                "confidence": 0.6
            }
    
    def _handle_customer_analysis_question(self, question: str, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle customer analysis questions with sophisticated prompts"""
        
        # Extract customer-related data
        customer_cols = [col for col in df.columns if any(keyword in col.lower() 
                       for keyword in ['customer', 'client', 'user', 'buyer', 'patron'])]
        
        prompt_context = {
            "role": "You are DataGenie, a customer analytics expert specializing in customer behavior analysis and customer relationship management.",
            "task": "Provide comprehensive customer analysis with actionable insights for customer retention and growth",
            "context": {
                "business_type": context["business_type"],
                "question": question,
                "customer_columns": customer_cols,
                "data_scale": f"{context['data_summary']['total_records']:,} customer records",
                "categorical_summary": context["relevant_data"].get("categorical_summary", {}),
                "financial_summary": context["relevant_data"].get("financial_summary", {})
            },
            "analysis_focus": [
                "Customer segmentation",
                "Behavioral patterns",
                "Value analysis",
                "Retention strategies",
                "Growth opportunities"
            ]
        }
        
        try:
            ai_response = self._generate_sophisticated_response(prompt_context, "customer_analysis")
            
            answer = f"### 👥 **Customer Analytics**\n\n"
            answer += f"**Business Type:** {context['business_type'].title()}\n"
            answer += f"**Customer Records:** {context['data_summary']['total_records']:,}\n\n"
            
            answer += f"**🧠 AI Customer Analysis:**\n{ai_response}\n\n"
            
            return {
                "answer": answer,
                "data_used": {
                    "customer_columns": customer_cols,
                    "customer_analysis": True
                },
                "confidence": 0.85
            }
            
        except Exception as e:
            return {
                "answer": f"### 👥 **Customer Analysis**\n\nAnalyzing {context['data_summary']['total_records']:,} customer records for your {context['business_type']} business.\n\nFor detailed customer insights, please ask specific questions about customer behavior, segmentation, or retention.",
                "confidence": 0.6
            }
    
    def _handle_product_analysis_question(self, question: str, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle product analysis questions with sophisticated prompts"""
        
        # Extract product-related data
        product_cols = [col for col in df.columns if any(keyword in col.lower() 
                       for keyword in ['product', 'item', 'service', 'menu', 'dish', 'sku'])]
        
        prompt_context = {
            "role": "You are DataGenie, a product analytics expert specializing in product performance analysis and inventory optimization.",
            "task": "Provide comprehensive product analysis with actionable insights for product strategy and optimization",
            "context": {
                "business_type": context["business_type"],
                "question": question,
                "product_columns": product_cols,
                "data_scale": f"{context['data_summary']['total_records']:,} product records",
                "categorical_summary": context["relevant_data"].get("categorical_summary", {}),
                "financial_summary": context["relevant_data"].get("financial_summary", {})
            },
            "analysis_focus": [
                "Product performance ranking",
                "Revenue contribution analysis",
                "Inventory optimization",
                "Product lifecycle insights",
                "Strategic recommendations"
            ]
        }
        
        try:
            ai_response = self._generate_sophisticated_response(prompt_context, "product_analysis")
            
            answer = f"### 📦 **Product Analytics**\n\n"
            answer += f"**Business Type:** {context['business_type'].title()}\n"
            answer += f"**Product Records:** {context['data_summary']['total_records']:,}\n\n"
            
            answer += f"**🧠 AI Product Analysis:**\n{ai_response}\n\n"
            
            return {
                "answer": answer,
                "data_used": {
                    "product_columns": product_cols,
                    "product_analysis": True
                },
                "confidence": 0.85
            }
            
        except Exception as e:
            return {
                "answer": f"### 📦 **Product Analysis**\n\nAnalyzing {context['data_summary']['total_records']:,} product records for your {context['business_type']} business.\n\nFor detailed product insights, please ask specific questions about product performance, top sellers, or inventory optimization.",
                "confidence": 0.6
            }
    
    def _handle_general_question_enhanced(self, question: str, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced general question handling with sophisticated prompts"""
        
        prompt_context = {
            "role": "You are DataGenie, an intelligent business data analyst with expertise across multiple business domains and data analysis techniques.",
            "task": "Provide comprehensive, insightful analysis for any business question using available data",
            "context": {
                "business_type": context["business_type"],
                "question": question,
                "data_summary": context["data_summary"],
                "available_data": context["relevant_data"],
                "conversation_context": context["conversation_context"],
                "quick_facts": context["quick_facts"]
            },
            "response_requirements": [
                "Provide clear, actionable insights",
                "Use business-appropriate language",
                "Include relevant data points",
                "Suggest follow-up questions",
                "Maintain professional tone"
            ]
        }
        
        try:
            ai_response = self._generate_sophisticated_response(prompt_context, "general_analysis")
            
            answer = f"### 🤖 **AI-Powered Analysis**\n\n"
            answer += f"**Business Type:** {context['business_type'].title()}\n"
            answer += f"**Data Context:** {context['data_summary']['total_records']:,} records, {context['data_summary']['total_columns']} columns\n\n"
            
            answer += f"**🧠 AI Analysis:**\n{ai_response}\n\n"
            
            # Add quick facts if relevant
            if context["quick_facts"]:
                answer += "**💡 Quick Facts:**\n"
                for fact in context["quick_facts"][:3]:
                    answer += f"• {fact}\n"
            
            return {
                "answer": answer,
                "data_used": {
                    "general_analysis": True,
                    "ai_powered": True
                },
                "confidence": 0.8
            }
            
        except Exception as e:
            return {
                "answer": f"### 🤖 **General Analysis**\n\nBased on your question: '{question}'\n\nYour {context['business_type']} dataset contains {context['data_summary']['total_records']:,} records with {context['data_summary']['total_columns']} columns.\n\nFor more specific insights, please ask detailed questions about your data, business performance, or specific metrics you'd like to explore.",
                "confidence": 0.6
            }
    
    def _generate_sophisticated_response(self, prompt_context: Dict[str, Any], analysis_type: str) -> str:
        """Generate sophisticated AI response using enhanced prompts with real data analysis"""
        
        # Build comprehensive analysis data with actual results
        analysis_data = {
            "question": prompt_context['context']['question'],
            "business_type": prompt_context['context']['business_type'],
            "data_scale": prompt_context['context'].get('data_scale', 'N/A'),
            "analysis_type": analysis_type,
            "role": prompt_context['role'],
            "task": prompt_context['task']
        }
        
        # Add specific data based on analysis type
        if analysis_type == "statistical_analysis":
            analysis_data.update({
                "statistical_data": prompt_context['context'].get('statistical_data', {}),
                "financial_data": prompt_context['context'].get('financial_data', {}),
                "data_points": prompt_context['context'].get('data_scale', 'N/A')
            })
        elif analysis_type == "trend_analysis":
            analysis_data.update({
                "date_range": prompt_context['context'].get('date_range', {}),
                "financial_data": prompt_context['context'].get('financial_data', {}),
                "trend_direction": "analyzing trends over time"
            })
        elif analysis_type == "data_overview":
            analysis_data.update({
                "data_summary": prompt_context['context'].get('data_summary', {}),
                "key_insights": prompt_context['context'].get('key_insights', {}),
                "quick_facts": prompt_context['context'].get('quick_facts', [])
            })
        elif analysis_type == "business_insights":
            analysis_data.update({
                "business_metrics": prompt_context['context'].get('business_metrics', {}),
                "financial_summary": prompt_context['context'].get('financial_summary', {}),
                "data_quality": prompt_context['context'].get('data_quality', {})
            })
        
        # Add analysis requirements
        analysis_data["analysis_requirements"] = prompt_context.get('analysis_requirements', prompt_context.get('response_requirements', []))
        
        try:
            # Use the enhanced GenAI client with real data
            response = generate_business_insights(analysis_data, prompt_context['context']['business_type'], analysis_type)
            
            # Clean up any HTML artifacts
            response = self._clean_response(response)
            
            return response
        except Exception as e:
            print(f"DEBUG: GenAI Error - {str(e)}")
            # Fallback to basic analysis with actual data
            return self._generate_fallback_response(prompt_context, analysis_type)
    
    def _clean_response(self, response: str) -> str:
        """Clean up response to remove HTML artifacts and formatting issues"""
        # Remove common HTML artifacts
        response = response.replace('</div>', '').replace('<div>', '')
        response = response.replace('</p>', '').replace('<p>', '')
        response = response.replace('</span>', '').replace('<span>', '')
        response = response.replace('&nbsp;', ' ')
        response = response.replace('&amp;', '&')
        response = response.replace('&lt;', '<')
        response = response.replace('&gt;', '>')
        
        # Clean up extra whitespace
        response = ' '.join(response.split())
        
        return response
    
    def _generate_fallback_response(self, prompt_context: Dict[str, Any], analysis_type: str) -> str:
        """Generate intelligent fallback response with actual data"""
        
        context = prompt_context['context']
        business_type = context['business_type']
        question = context['question']
        
        if analysis_type == "statistical_analysis":
            financial_data = context.get('financial_data', {})
            if financial_data:
                response = f"### 📈 Statistical Analysis for {business_type.title()}\n\n"
                response += f"**Question:** {question}\n\n"
                response += "**Key Financial Metrics:**\n"
                for col, stats in financial_data.items():
                    response += f"• **{col.title()}:** Total ${stats['total']:,.2f}, Average ${stats['average']:,.2f}\n"
                response += f"\n**Analysis:** Your {business_type} business shows strong performance with total revenue of ${sum(s['total'] for s in financial_data.values()):,.2f}. "
                response += f"The average transaction value of ${sum(s['average'] for s in financial_data.values())/len(financial_data):,.2f} indicates healthy customer spending patterns.\n\n"
                response += "**Recommendations:**\n• Monitor transaction trends for seasonal patterns\n• Analyze customer segments for targeted marketing\n• Track key performance indicators monthly"
                return response
        
        elif analysis_type == "trend_analysis":
            date_data = context.get('date_range', {})
            financial_data = context.get('financial_data', {})
            if date_data:
                response = f"### 📈 Trend Analysis for {business_type.title()}\n\n"
                response += f"**Question:** {question}\n\n"
                response += f"**Analysis Period:** {date_data.get('span_days', 'N/A')} days\n"
                if financial_data:
                    total_revenue = sum(s['total'] for s in financial_data.values())
                    response += f"**Total Revenue:** ${total_revenue:,.2f}\n"
                response += f"\n**Trend Insights:** Based on your {business_type} data over {date_data.get('span_days', 'N/A')} days, "
                response += "I can identify key patterns and growth opportunities. The data shows consistent performance with potential for optimization.\n\n"
                response += "**Key Findings:**\n• Revenue patterns show business stability\n• Customer engagement metrics indicate growth potential\n• Seasonal trends suggest strategic planning opportunities\n\n"
                response += "**Next Steps:**\n• Implement monthly trend monitoring\n• Develop seasonal marketing strategies\n• Set up automated reporting dashboards"
                return response
        
        elif analysis_type == "data_overview":
            data_summary = context.get('data_summary', {})
            key_insights = context.get('key_insights', {})
            response = f"### 📊 Data Overview for {business_type.title()}\n\n"
            response += f"**Dataset:** {data_summary.get('total_records', 'N/A')} records, {data_summary.get('total_columns', 'N/A')} columns\n"
            response += f"**Business Type:** {business_type.title()}\n\n"
            response += "**Key Insights:**\n"
            for metric, value in key_insights.items():
                response += f"• **{metric.replace('_', ' ').title()}:** {value}\n"
            response += f"\n**Analysis:** Your {business_type} dataset provides comprehensive insights into business performance. "
            response += "The data quality and structure enable detailed analysis across multiple dimensions.\n\n"
            response += "**Recommendations:**\n• Regular data quality monitoring\n• Automated insight generation\n• Strategic decision support systems"
            return response
        
        # Default fallback
        return f"### 🤖 AI Analysis for {business_type.title()}\n\n**Question:** {question}\n\nBased on your {business_type} data analysis, I can provide insights about your business performance. The dataset contains valuable information for strategic decision-making.\n\nFor more detailed analysis, please ask specific questions about metrics, trends, or comparisons you'd like to explore."
    
    def _handle_trend_question_enhanced(self, question: str, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced trend analysis with sophisticated prompts"""
        
        date_data = context["relevant_data"].get("date_range", {})
        financial_data = context["relevant_data"].get("financial_summary", {})
        
        if not date_data:
            return {
                "answer": "❌ **No Date Data Found**\n\nI couldn't find any date columns in your dataset for trend analysis. Please ensure your data contains date/time fields like purchase dates, order dates, or timestamps.",
                "confidence": 0.1
            }
        
        prompt_context = {
            "role": "You are DataGenie, a time series analysis expert specializing in business trend analysis and forecasting.",
            "task": "Provide comprehensive trend analysis with business implications and future projections",
            "context": {
                "business_type": context["business_type"],
                "question": question,
                "date_range": date_data,
                "financial_data": financial_data,
                "data_scale": f"{context['data_summary']['total_records']:,} records"
            },
            "analysis_requirements": [
                "Identify key trends and patterns",
                "Explain business implications of trends",
                "Provide growth rate calculations",
                "Suggest trend-based strategies",
                "Include seasonal analysis if applicable"
            ]
        }
        
        try:
            ai_response = self._generate_sophisticated_response(prompt_context, "trend_analysis")
            
            answer = f"### 📈 **Advanced Trend Analysis**\n\n"
            answer += f"**Business Type:** {context['business_type'].title()}\n"
            answer += f"**Analysis Period:** {date_data.get('span_days', 'N/A')} days\n"
            answer += f"**Data Points:** {context['data_summary']['total_records']:,} records\n\n"
            
            answer += f"**🧠 AI Trend Analysis:**\n{ai_response}\n\n"
            
            if financial_data:
                answer += "**💰 Financial Trends:**\n"
                for col, stats in financial_data.items():
                    answer += f"• **{col.title()}:** Total ${stats['total']:,.2f}, Avg ${stats['average']:,.2f}\n"
            
            return {
                "answer": answer,
                "data_used": {
                    "date_analysis": True,
                    "trend_calculation": True,
                    "ai_analysis": True
                },
                "confidence": 0.9
            }
            
        except Exception as e:
            return {
                "answer": f"### 📈 **Trend Analysis**\n\nAnalyzing trends in your {context['business_type']} data over {date_data.get('span_days', 'N/A')} days.\n\nFor detailed trend insights, please ask specific questions about growth rates, seasonal patterns, or performance over time.",
                "confidence": 0.7
            }
    
    def _handle_comparison_question_enhanced(self, question: str, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced comparison analysis with sophisticated prompts"""
        
        prompt_context = {
            "role": "You are DataGenie, a comparative analysis expert specializing in business performance benchmarking and competitive analysis.",
            "task": "Provide comprehensive comparison analysis with actionable insights and recommendations",
            "context": {
                "business_type": context["business_type"],
                "question": question,
                "data_summary": context["data_summary"],
                "categorical_summary": context["relevant_data"].get("categorical_summary", {}),
                "financial_summary": context["relevant_data"].get("financial_summary", {})
            },
            "analysis_requirements": [
                "Identify comparison dimensions",
                "Calculate performance metrics",
                "Provide ranking and benchmarking",
                "Suggest improvement strategies",
                "Include competitive insights"
            ]
        }
        
        try:
            ai_response = self._generate_sophisticated_response(prompt_context, "comparison_analysis")
            
            answer = f"### ⚖️ **Advanced Comparison Analysis**\n\n"
            answer += f"**Business Type:** {context['business_type'].title()}\n"
            answer += f"**Comparison Context:** {context['data_summary']['total_records']:,} records\n\n"
            
            answer += f"**🧠 AI Comparison Analysis:**\n{ai_response}\n\n"
            
            return {
                "answer": answer,
                "data_used": {
                    "comparison_analysis": True,
                    "ai_analysis": True
                },
                "confidence": 0.85
            }
            
        except Exception as e:
            return {
                "answer": f"### ⚖️ **Comparison Analysis**\n\nAnalyzing comparisons in your {context['business_type']} data.\n\nFor detailed comparison insights, please ask specific questions about comparing products, customers, time periods, or performance metrics.",
                "confidence": 0.7
            }
    
    def _handle_prediction_question_enhanced(self, question: str, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced prediction analysis with sophisticated prompts"""
        
        date_data = context["relevant_data"].get("date_range", {})
        financial_data = context["relevant_data"].get("financial_summary", {})
        
        if not date_data:
            return {
                "answer": "❌ **Insufficient Data for Prediction**\n\nPrediction analysis requires historical data with date information. Please ensure your dataset contains date/time fields for trend-based forecasting.",
                "confidence": 0.1
            }
        
        prompt_context = {
            "role": "You are DataGenie, a predictive analytics expert specializing in business forecasting and future planning.",
            "task": "Provide comprehensive prediction analysis with confidence intervals and strategic recommendations",
            "context": {
                "business_type": context["business_type"],
                "question": question,
                "historical_data": {
                    "date_range": date_data,
                    "financial_summary": financial_data,
                    "data_points": context['data_summary']['total_records']
                }
            },
            "analysis_requirements": [
                "Calculate trend-based projections",
                "Provide confidence levels",
                "Identify key assumptions",
                "Suggest risk mitigation strategies",
                "Include scenario planning"
            ]
        }
        
        try:
            ai_response = self._generate_sophisticated_response(prompt_context, "prediction_analysis")
            
            answer = f"### 🔮 **Advanced Prediction Analysis**\n\n"
            answer += f"**Business Type:** {context['business_type'].title()}\n"
            answer += f"**Historical Data:** {date_data.get('span_days', 'N/A')} days, {context['data_summary']['total_records']:,} records\n\n"
            
            answer += f"**🧠 AI Prediction Analysis:**\n{ai_response}\n\n"
            
            answer += "⚠️ **Disclaimer:** Predictions are based on historical trends and should be used as guidance. External factors may significantly impact actual results."
            
            return {
                "answer": answer,
                "data_used": {
                    "prediction_analysis": True,
                    "trend_based": True,
                    "ai_analysis": True
                },
                "confidence": 0.8
            }
            
        except Exception as e:
            return {
                "answer": f"### 🔮 **Prediction Analysis**\n\nBased on {date_data.get('span_days', 'N/A')} days of historical data for your {context['business_type']} business.\n\nFor detailed forecasting, please ask specific questions about future performance, growth projections, or seasonal predictions.",
                "confidence": 0.6
            }
    
    def _handle_data_quality_question_enhanced(self, question: str, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced data quality analysis with sophisticated prompts"""
        
        quality_data = context["data_quality"]
        
        prompt_context = {
            "role": "You are DataGenie, a data quality expert specializing in data governance and data management best practices.",
            "task": "Provide comprehensive data quality assessment with actionable improvement recommendations",
            "context": {
                "business_type": context["business_type"],
                "question": question,
                "data_quality": quality_data,
                "data_summary": context["data_summary"]
            },
            "analysis_requirements": [
                "Assess data completeness and accuracy",
                "Identify data quality issues",
                "Provide improvement recommendations",
                "Suggest data governance practices",
                "Include data cleaning strategies"
            ]
        }
        
        try:
            ai_response = self._generate_sophisticated_response(prompt_context, "data_quality_analysis")
            
            answer = f"### 🔍 **Advanced Data Quality Assessment**\n\n"
            answer += f"**Business Type:** {context['business_type'].title()}\n"
            answer += f"**Overall Quality Score:** {quality_data['quality_score']}/100\n"
            answer += f"**Dataset Size:** {context['data_summary']['total_records']:,} records\n\n"
            
            answer += f"**🧠 AI Quality Analysis:**\n{ai_response}\n\n"
            
            if quality_data['issues']:
                answer += "**⚠️ Issues Identified:**\n"
                for issue in quality_data['issues']:
                    answer += f"• {issue}\n"
                answer += "\n"
            
            if quality_data['recommendations']:
                answer += "**💡 Recommendations:**\n"
                for rec in quality_data['recommendations']:
                    answer += f"• {rec}\n"
            
            return {
                "answer": answer,
                "data_used": {
                    "quality_analysis": True,
                    "ai_analysis": True
                },
                "confidence": 0.95
            }
            
        except Exception as e:
            # Fallback quality analysis
            answer = f"### 🔍 **Data Quality Assessment**\n\n"
            answer += f"**Quality Score:** {quality_data['quality_score']}/100\n\n"
            
            if quality_data['issues']:
                answer += "**Issues Found:**\n"
                for issue in quality_data['issues']:
                    answer += f"• {issue}\n"
                answer += "\n"
            
            if quality_data['recommendations']:
                answer += "**Recommendations:**\n"
                for rec in quality_data['recommendations']:
                    answer += f"• {rec}\n"
            
            return {
                "answer": answer,
                "data_used": {"quality_analysis": True},
                "confidence": 0.8
            }
    
    def _handle_data_overview_question(self, question: str, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data overview questions"""
        
        # Prepare comprehensive overview
        overview_data = {
            "question": question,
            "business_type": self.data_context["metadata"]["business_type"],
            "data_summary": {
                "total_records": len(df),
                "total_columns": len(df.columns),
                "column_names": df.columns.tolist(),
                "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()}
            },
            "quick_facts": self.data_context["quick_facts"],
            "key_metrics": self.data_context["business_insights"]["key_metrics"],
            "data_quality": self.data_context["data_quality"]
        }
        
        try:
            # Generate AI-powered overview
            ai_response = generate_business_insights(overview_data, self.data_context["metadata"]["business_type"], "data_overview")
            answer = f"### 📊 Data Overview\n\n{ai_response}"
        except Exception as e:
            answer = f"### 📊 Data Overview\n\nYour dataset contains **{len(df):,} records** across **{len(df.columns)} columns**.\n\n"
            answer += f"**Quick Facts:**\n"
            for fact in self.data_context["quick_facts"][:5]:
                answer += f"• {fact}\n"
        
        return {
            "answer": answer,
            "data_used": {"records_analyzed": len(df), "columns_analyzed": len(df.columns)},
            "confidence": 0.9
        }
    
    def _handle_statistical_question(self, question: str, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle statistical questions"""
        
        # Extract relevant columns
        relevant_cols = context.get("relevant_columns", [])
        
        if not relevant_cols:
            # Try to find numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            relevant_cols = numeric_cols[:3]  # Take first 3 numeric columns
        
        if not relevant_cols:
            return {
                "answer": "❌ No numeric columns found for statistical analysis. Please ask about categorical data or data overview.",
                "confidence": 0.1
            }
        
        # Calculate statistics
        stats_data = {}
        for col in relevant_cols:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                stats_data[col] = {
                    "count": df[col].count(),
                    "mean": df[col].mean(),
                    "median": df[col].median(),
                    "std": df[col].std(),
                    "min": df[col].min(),
                    "max": df[col].max(),
                    "sum": df[col].sum()
                }
        
        # Prepare context for AI
        analysis_data = {
            "question": question,
            "statistics": stats_data,
            "business_type": self.data_context["metadata"]["business_type"],
            "column_analysis": {col: self.data_context["column_analysis"].get(col, {}) for col in relevant_cols}
        }
        
        try:
            ai_response = generate_business_insights(analysis_data, self.data_context["metadata"]["business_type"], "statistical_analysis")
            answer = f"### 📈 Statistical Analysis\n\n{ai_response}"
        except Exception as e:
            answer = f"### 📈 Statistical Analysis\n\n"
            for col, stats in stats_data.items():
                answer += f"**{col}:**\n"
                answer += f"• Average: {stats['mean']:.2f}\n"
                answer += f"• Median: {stats['median']:.2f}\n"
                answer += f"• Total: {stats['sum']:,.2f}\n"
                answer += f"• Range: {stats['min']:.2f} - {stats['max']:.2f}\n\n"
        
        return {
            "answer": answer,
            "data_used": {"columns_analyzed": relevant_cols, "statistics_calculated": len(stats_data)},
            "confidence": 0.8
        }
    
    def _handle_trend_question(self, question: str, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle trend analysis questions"""
        
        # Find date column
        date_cols = [col for col in df.columns if any(keyword in col.lower() 
                    for keyword in ['date', 'time', 'created', 'purchase', 'order'])]
        
        if not date_cols:
            return {
                "answer": "❌ No date column found for trend analysis. Please ensure your data has a date/time column.",
                "confidence": 0.1
            }
        
        date_col = date_cols[0]
        
        # Find amount column
        amount_cols = [col for col in df.columns if any(keyword in col.lower() 
                      for keyword in ['amount', 'price', 'total', 'revenue', 'cost', 'value'])]
        
        try:
            # Convert date column
            df_temp = df.copy()
            df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
            df_temp = df_temp.dropna(subset=[date_col])
            
            if len(df_temp) == 0:
                return {
                    "answer": "❌ Unable to parse date column for trend analysis.",
                    "confidence": 0.1
                }
            
            # Calculate trends
            if amount_cols:
                amount_col = amount_cols[0]
                monthly_trends = df_temp.groupby(df_temp[date_col].dt.to_period('M'))[amount_col].sum()
            else:
                monthly_trends = df_temp.groupby(df_temp[date_col].dt.to_period('M')).size()
            
            # Prepare trend data
            trend_data = {
                "question": question,
                "date_column": date_col,
                "amount_column": amount_cols[0] if amount_cols else None,
                "trend_data": monthly_trends.to_dict(),
                "trend_direction": "increasing" if monthly_trends.iloc[-1] > monthly_trends.iloc[0] else "decreasing",
                "total_months": len(monthly_trends),
                "business_type": self.data_context["metadata"]["business_type"]
            }
            
            try:
                ai_response = generate_business_insights(trend_data, self.data_context["metadata"]["business_type"], "trend_analysis")
                answer = f"### 📈 Trend Analysis\n\n{ai_response}"
            except Exception as e:
                answer = f"### 📈 Trend Analysis\n\n"
                answer += f"Analyzing trends in **{date_col}**"
                if amount_cols:
                    answer += f" for **{amount_cols[0]}**"
                answer += f"\n\n**Trend Direction:** {trend_data['trend_direction'].title()}\n"
                answer += f"**Analysis Period:** {trend_data['total_months']} months\n"
                answer += f"**Data Points:** {len(df_temp)} records\n"
            
            return {
                "answer": answer,
                "data_used": {"date_column": date_col, "records_analyzed": len(df_temp), "months_analyzed": len(monthly_trends)},
                "confidence": 0.8
            }
            
        except Exception as e:
            return {
                "answer": f"❌ Error analyzing trends: {str(e)}",
                "confidence": 0.1
            }
    
    def _handle_comparison_question(self, question: str, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle comparison questions"""
        
        # Extract comparison targets from question
        comparison_data = {
            "question": question,
            "business_type": self.data_context["metadata"]["business_type"],
            "data_summary": {
                "total_records": len(df),
                "columns": df.columns.tolist()
            }
        }
        
        # Try to identify what to compare
        if 'product' in question.lower() or 'item' in question.lower():
            product_cols = [col for col in df.columns if any(keyword in col.lower() 
                          for keyword in ['product', 'item', 'sku', 'menu', 'dish'])]
            if product_cols:
                product_col = product_cols[0]
                amount_cols = [col for col in df.columns if any(keyword in col.lower() 
                              for keyword in ['amount', 'price', 'total', 'revenue'])]
                if amount_cols:
                    amount_col = amount_cols[0]
                    comparison = df.groupby(product_col)[amount_col].sum().sort_values(ascending=False).head(10)
                    comparison_data["product_comparison"] = comparison.to_dict()
        
        try:
            ai_response = generate_business_insights(comparison_data, self.data_context["metadata"]["business_type"], "comparison_analysis")
            answer = f"### ⚖️ Comparison Analysis\n\n{ai_response}"
        except Exception as e:
            answer = f"### ⚖️ Comparison Analysis\n\nBased on your question: '{question}'\n\n"
            answer += "I can help you compare different aspects of your data. Please be more specific about what you'd like to compare (e.g., products, customers, time periods)."
        
        return {
            "answer": answer,
            "data_used": {"comparison_type": "general", "records_analyzed": len(df)},
            "confidence": 0.7
        }
    
    def _handle_prediction_question(self, question: str, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle prediction/forecasting questions"""
        
        # Simple trend-based prediction
        date_cols = [col for col in df.columns if any(keyword in col.lower() 
                    for keyword in ['date', 'time', 'created', 'purchase', 'order'])]
        amount_cols = [col for col in df.columns if any(keyword in col.lower() 
                      for keyword in ['amount', 'price', 'total', 'revenue', 'cost', 'value'])]
        
        if not date_cols or not amount_cols:
            return {
                "answer": "❌ Prediction requires both date and amount columns. Please ensure your data has these fields.",
                "confidence": 0.1
            }
        
        try:
            # Simple linear trend calculation
            df_temp = df.copy()
            df_temp[date_cols[0]] = pd.to_datetime(df_temp[date_cols[0]], errors='coerce')
            df_temp = df_temp.dropna(subset=[date_cols[0]])
            
            monthly_data = df_temp.groupby(df_temp[date_cols[0]].dt.to_period('M'))[amount_cols[0]].sum()
            
            if len(monthly_data) < 3:
                return {
                    "answer": "❌ Need at least 3 months of data for prediction.",
                    "confidence": 0.1
                }
            
            # Simple trend calculation
            x = range(len(monthly_data))
            y = monthly_data.values
            slope = (len(x) * sum(x[i] * y[i] for i in range(len(x))) - sum(x) * sum(y)) / (len(x) * sum(x[i]**2 for i in range(len(x))) - sum(x)**2)
            
            prediction_data = {
                "question": question,
                "business_type": self.data_context["metadata"]["business_type"],
                "current_trend": slope,
                "trend_direction": "increasing" if slope > 0 else "decreasing",
                "data_points": len(monthly_data),
                "last_value": monthly_data.iloc[-1],
                "prediction_confidence": "low" if abs(slope) < 100 else "medium" if abs(slope) < 1000 else "high"
            }
            
            try:
                ai_response = generate_business_insights(prediction_data, self.data_context["metadata"]["business_type"], "prediction_analysis")
                answer = f"### 🔮 Prediction Analysis\n\n{ai_response}"
            except Exception as e:
                answer = f"### 🔮 Prediction Analysis\n\n"
                answer += f"Based on {len(monthly_data)} months of data:\n"
                answer += f"• **Current Trend:** {prediction_data['trend_direction'].title()}\n"
                answer += f"• **Last Value:** {prediction_data['last_value']:,.2f}\n"
                answer += f"• **Confidence:** {prediction_data['prediction_confidence'].title()}\n\n"
                answer += "⚠️ This is a simple trend-based prediction. For more accurate forecasts, consider using advanced time series models."
            
            return {
                "answer": answer,
                "data_used": {"months_analyzed": len(monthly_data), "trend_calculated": True},
                "confidence": 0.6
            }
            
        except Exception as e:
            return {
                "answer": f"❌ Error generating prediction: {str(e)}",
                "confidence": 0.1
            }
    
    def _handle_data_quality_question(self, question: str, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data quality questions"""
        
        quality_data = self.data_context["data_quality"]
        
        answer = f"### 🔍 Data Quality Assessment\n\n"
        answer += f"**Overall Quality Score:** {quality_data['quality_score']}/100\n\n"
        
        if quality_data['issues']:
            answer += "**Issues Found:**\n"
            for issue in quality_data['issues']:
                answer += f"• {issue}\n"
            answer += "\n"
        
        if quality_data['recommendations']:
            answer += "**Recommendations:**\n"
            for rec in quality_data['recommendations']:
                answer += f"• {rec}\n"
        
        return {
            "answer": answer,
            "data_used": {"quality_metrics": quality_data},
            "confidence": 0.9
        }
    
    def _handle_general_question(self, question: str, df: pd.DataFrame, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general questions"""
        
        # Prepare general context
        general_data = {
            "question": question,
            "business_type": self.data_context["metadata"]["business_type"],
            "data_summary": {
                "total_records": len(df),
                "total_columns": len(df.columns),
                "column_names": df.columns.tolist()
            },
            "sample_data": df.head(3).to_dict('records'),
            "quick_facts": self.data_context["quick_facts"]
        }
        
        try:
            ai_response = generate_business_insights(general_data, self.data_context["metadata"]["business_type"], "general_analysis")
            answer = f"### 🤖 AI Analysis\n\n{ai_response}"
        except Exception as e:
            answer = f"### 🤖 General Analysis\n\n"
            answer += f"Based on your question: '{question}'\n\n"
            answer += f"Your dataset contains {len(df):,} records with {len(df.columns)} columns.\n"
            answer += "Here are some quick facts:\n"
            for fact in self.data_context["quick_facts"][:3]:
                answer += f"• {fact}\n"
            answer += "\nFeel free to ask more specific questions about your data!"
        
        return {
            "answer": answer,
            "data_used": {"general_analysis": True, "records_analyzed": len(df)},
            "confidence": 0.7
        }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.conversation_history
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        if 'datagenie_history' in st.session_state:
            st.session_state.datagenie_history = []
