#!/usr/bin/env python3
"""
Smart Universal Analytics Engine
Automatically detects business type, data structure, and provides instant insights
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, List, Tuple, Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from genai_client import generate_business_insights

class SmartAnalyticsEngine:
    """Universal analytics engine that adapts to any business data"""
    
    def __init__(self):
        self.business_patterns = {
            "retail_ecommerce": {
                "keywords": ["product", "item", "sku", "order", "customer", "amount", "price", "quantity", "sale", "purchase"],
                "date_patterns": ["date", "time", "created", "purchase", "order"],
                "amount_patterns": ["amount", "price", "total", "revenue", "cost", "value"],
                "customer_patterns": ["customer", "client", "user", "buyer", "id"],
                "location_patterns": ["location", "region", "city", "state", "country", "store", "branch"]
            },
            "real_estate": {
                "keywords": ["property", "house", "apartment", "sale", "price", "agent", "suburb", "bedroom", "bathroom"],
                "date_patterns": ["saledate", "date", "listed", "sold"],
                "amount_patterns": ["price", "value", "amount", "cost"],
                "customer_patterns": ["agent", "buyer", "seller", "client"],
                "location_patterns": ["suburb", "location", "address", "city", "region"]
            },
            "restaurant_food": {
                "keywords": ["menu", "dish", "food", "order", "customer", "table", "waiter", "kitchen"],
                "date_patterns": ["date", "time", "order", "service"],
                "amount_patterns": ["amount", "total", "bill", "price", "cost"],
                "customer_patterns": ["customer", "guest", "table", "party"],
                "location_patterns": ["table", "section", "area", "zone"]
            },
            "healthcare": {
                "keywords": ["patient", "doctor", "appointment", "treatment", "diagnosis", "medical", "health"],
                "date_patterns": ["date", "appointment", "visit", "treatment"],
                "amount_patterns": ["cost", "fee", "charge", "amount", "bill"],
                "customer_patterns": ["patient", "client", "id"],
                "location_patterns": ["department", "clinic", "room", "ward"]
            },
            "education": {
                "keywords": ["student", "course", "grade", "teacher", "class", "enrollment", "tuition"],
                "date_patterns": ["date", "enrollment", "graduation", "semester"],
                "amount_patterns": ["tuition", "fee", "cost", "amount"],
                "customer_patterns": ["student", "learner", "id"],
                "location_patterns": ["campus", "building", "room", "department"]
            }
        }
        
        self.analysis_templates = {
            "retail_ecommerce": {
                "top_products": "Which products generate the most revenue?",
                "sales_trends": "How have sales changed over time?",
                "customer_behavior": "What are the customer buying patterns?",
                "seasonal_analysis": "Are there seasonal trends in sales?",
                "profitability": "What is the profitability analysis?"
            },
            "real_estate": {
                "top_locations": "Which locations have the highest property values?",
                "price_trends": "How have property prices changed over time?",
                "agent_performance": "Which agents have the best performance?",
                "market_analysis": "What is the market trend analysis?"
            },
            "restaurant_food": {
                "popular_items": "Which menu items are most popular?",
                "revenue_trends": "How has revenue changed over time?",
                "customer_patterns": "What are the customer dining patterns?",
                "table_analysis": "Which tables/sections perform best?"
            },
            "healthcare": {
                "patient_volume": "What is the patient volume analysis?",
                "treatment_trends": "How have treatments changed over time?",
                "department_performance": "Which departments are most active?",
                "cost_analysis": "What is the cost analysis?"
            },
            "education": {
                "enrollment_trends": "How has enrollment changed over time?",
                "course_popularity": "Which courses are most popular?",
                "student_performance": "What is the student performance analysis?",
                "revenue_analysis": "What is the revenue analysis?"
            }
        }
    
    def detect_business_type(self, df: pd.DataFrame) -> Tuple[str, float]:
        """Detect business type based on column names and data patterns"""
        column_names = [col.lower() for col in df.columns]
        text_data = ' '.join(column_names)
        
        scores = {}
        for business_type, patterns in self.business_patterns.items():
            score = 0
            total_patterns = 0
            
            # Check keywords
            for keyword in patterns["keywords"]:
                total_patterns += 1
                if keyword in text_data:
                    score += 1
            
            # Check specific patterns
            for pattern_type, pattern_list in patterns.items():
                if pattern_type != "keywords":
                    for pattern in pattern_list:
                        total_patterns += 1
                        if any(re.search(pattern, col, re.IGNORECASE) for col in column_names):
                            score += 1
            
            if total_patterns > 0:
                scores[business_type] = score / total_patterns
        
        if scores:
            best_match = max(scores.items(), key=lambda x: x[1])
            return best_match[0], best_match[1]
        
        return "general_business", 0.0
    
    def auto_map_columns(self, df: pd.DataFrame, business_type: str) -> Dict[str, str]:
        """Automatically map columns to standard schema"""
        column_names = [col.lower() for col in df.columns]
        mapping = {}
        
        # Get business-specific patterns
        patterns = self.business_patterns.get(business_type, {})
        
        # Map date columns
        date_cols = [col for col in df.columns if any(re.search(pattern, col, re.IGNORECASE) 
                    for pattern in patterns.get("date_patterns", ["date", "time"]))]
        if date_cols:
            mapping["Date"] = date_cols[0]
        
        # Map amount columns
        amount_cols = [col for col in df.columns if any(re.search(pattern, col, re.IGNORECASE) 
                      for pattern in patterns.get("amount_patterns", ["amount", "price", "total"]))]
        if amount_cols:
            mapping["Amount"] = amount_cols[0]
        
        # Map customer columns
        customer_cols = [col for col in df.columns if any(re.search(pattern, col, re.IGNORECASE) 
                         for pattern in patterns.get("customer_patterns", ["customer", "client", "id"]))]
        if customer_cols:
            mapping["CustomerID"] = customer_cols[0]
        
        # Map location columns
        location_cols = [col for col in df.columns if any(re.search(pattern, col, re.IGNORECASE) 
                         for pattern in patterns.get("location_patterns", ["location", "region", "city"]))]
        if location_cols:
            mapping["Location"] = location_cols[0]
        
        # Map product/item columns
        product_keywords = ["product", "item", "sku", "menu", "dish", "course", "treatment", "property"]
        product_cols = [col for col in df.columns if any(keyword in col.lower() for keyword in product_keywords)]
        if product_cols:
            mapping["Product"] = product_cols[0]
        
        return mapping
    
    def generate_smart_questions(self, df: pd.DataFrame, business_type: str, mapping: Dict[str, str]) -> List[Dict]:
        """Generate relevant questions based on available data and business type"""
        available_fields = list(mapping.keys())
        questions = []
        
        # Get business-specific question templates
        templates = self.analysis_templates.get(business_type, {})
        
        # Generate questions based on available data
        if "Date" in available_fields and "Amount" in available_fields:
            if "Product" in available_fields:
                questions.append({
                    "id": "top_items",
                    "text": templates.get("top_products", "Which items generate the most revenue?"),
                    "desc": "Analyze top-performing items by revenue",
                    "required_fields": ["Date", "Product", "Amount"]
                })
            
            questions.append({
                "id": "trend_analysis",
                "text": templates.get("sales_trends", "How have sales changed over time?"),
                "desc": "Analyze trends over time",
                "required_fields": ["Date", "Amount"]
            })
        
        if "CustomerID" in available_fields:
            questions.append({
                "id": "customer_analysis",
                "text": templates.get("customer_behavior", "What are the customer patterns?"),
                "desc": "Analyze customer behavior and patterns",
                "required_fields": ["CustomerID", "Amount"]
            })
        
        if "Location" in available_fields:
            questions.append({
                "id": "location_analysis",
                "text": templates.get("top_locations", "Which locations perform best?"),
                "desc": "Analyze performance by location",
                "required_fields": ["Location", "Amount"]
            })
        
        # Add general business questions
        questions.extend([
            {
                "id": "summary_stats",
                "text": "What are the key business metrics?",
                "desc": "Get a comprehensive business overview",
                "required_fields": ["Amount"]
            },
            {
                "id": "data_insights",
                "text": "What insights can we extract from this data?",
                "desc": "AI-powered data exploration",
                "required_fields": []
            }
        ])
        
        return questions
    
    def generate_instant_insights(self, df: pd.DataFrame, business_type: str, mapping: Dict[str, str]) -> str:
        """Generate instant insights without complex analysis"""
        try:
            # Prepare data context
            data_context = {
                "business_type": business_type,
                "data_shape": {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "column_names": df.columns.tolist()
                },
                "mapped_fields": mapping,
                "sample_data": df.head(3).to_dict('records'),
                "data_types": df.dtypes.to_dict()
            }
            
            # Generate basic statistics
            if "Amount" in mapping:
                amount_col = mapping["Amount"]
                if amount_col in df.columns:
                    total_revenue = df[amount_col].sum()
                    avg_transaction = df[amount_col].mean()
                    data_context["revenue_stats"] = {
                        "total_revenue": total_revenue,
                        "avg_transaction": avg_transaction,
                        "transaction_count": len(df)
                    }
            
            # Generate AI insights
            insights = generate_business_insights(data_context, business_type, "instant_analysis")
            return insights
            
        except Exception as e:
            return f"Instant analysis completed. Dataset contains {len(df)} records with {len(df.columns)} columns. Ready for detailed analysis."
    
    def create_analysis_plan(self, df: pd.DataFrame) -> Dict:
        """Create a comprehensive analysis plan for the business"""
        business_type, confidence = self.detect_business_type(df)
        mapping = self.auto_map_columns(df, business_type)
        questions = self.generate_smart_questions(df, business_type, mapping)
        instant_insights = self.generate_instant_insights(df, business_type, mapping)
        
        return {
            "business_type": business_type,
            "confidence": confidence,
            "auto_mapping": mapping,
            "available_questions": questions,
            "instant_insights": instant_insights,
            "analysis_level": self._determine_analysis_level(mapping),
            "recommendations": self._generate_recommendations(df, business_type, mapping)
        }
    
    def _determine_analysis_level(self, mapping: Dict[str, str]) -> str:
        """Determine the analysis level based on available fields"""
        essential_fields = ["Date", "Amount"]
        enhanced_fields = ["CustomerID", "Location", "Product"]
        
        if all(field in mapping for field in essential_fields):
            if all(field in mapping for field in enhanced_fields):
                return "Advanced"
            elif any(field in mapping for field in enhanced_fields):
                return "Enhanced"
            else:
                return "Basic"
        return "Limited"
    
    def _generate_recommendations(self, df: pd.DataFrame, business_type: str, mapping: Dict[str, str]) -> List[str]:
        """Generate recommendations for improving data quality"""
        recommendations = []
        
        if "Date" not in mapping:
            recommendations.append("Add a date column to enable trend analysis")
        
        if "Amount" not in mapping:
            recommendations.append("Add an amount/price column to enable revenue analysis")
        
        if "CustomerID" not in mapping:
            recommendations.append("Add customer identification to enable customer analysis")
        
        if len(df) < 100:
            recommendations.append("Collect more data (100+ records) for better insights")
        
        return recommendations

# Global instance
def get_smart_analytics_engine():
    """Get smart analytics engine instance"""
    return SmartAnalyticsEngine()
