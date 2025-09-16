#!/usr/bin/env python3
"""
Unified Configuration Management for Business Insights Pro
Centralized configuration for domains, fields, and analysis capabilities
"""

from typing import Dict, List, Any, Optional
import json
import os

class BusinessInsightsConfig:
    """Centralized configuration management"""
    
    def __init__(self):
        self.domains = self._load_domains()
        self.analysis_modules = self._load_analysis_modules()
        self.ui_config = self._load_ui_config()
    
    def _load_domains(self) -> Dict[str, Any]:
        """Load domain configurations"""
        return {
            "retail": {
                "name": "Retail & E-commerce",
                "icon": "🛒",
                "description": "Sales, inventory, customer analytics for retail businesses",
                "tiers": {
                    "tier1_essential": {
                        "fields": ["Date", "Product", "Amount"],
                        "description": "Basic sales analysis",
                        "capabilities": ["sales_trends", "top_products", "revenue_analysis"]
                    },
                    "tier2_enhanced": {
                        "fields": ["CustomerID", "Location", "Channel"],
                        "description": "Customer and location insights",
                        "capabilities": ["customer_analysis", "location_performance", "channel_optimization"]
                    },
                    "tier3_advanced": {
                        "fields": ["OrderID", "StoreID", "Gender", "Age", "Cost", "Inventory", "IsReturned", "Feedback"],
                        "description": "Comprehensive business intelligence",
                        "capabilities": ["profitability", "inventory_management", "sentiment_analysis", "churn_prediction"]
                    }
                },
                "sample_file": "sample_retail_data.csv"
            },
            "real_estate": {
                "name": "Real Estate",
                "icon": "🏠",
                "description": "Property sales, market trends, agent performance",
                "tiers": {
                    "tier1_essential": {
                        "fields": ["SaleDate", "Suburb", "SalePrice"],
                        "description": "Basic property analysis",
                        "capabilities": ["price_trends", "top_suburbs", "sales_volume"]
                    },
                    "tier2_enhanced": {
                        "fields": ["Agent", "PropertyType"],
                        "description": "Agent and property type insights",
                        "capabilities": ["agent_performance", "property_type_analysis"]
                    },
                    "tier3_advanced": {
                        "fields": ["Bedrooms", "Bathrooms", "LandSize", "YearBuilt", "BuyerID"],
                        "description": "Detailed property intelligence",
                        "capabilities": ["market_segmentation", "investment_analysis", "buyer_behavior"]
                    }
                },
                "sample_file": "sample_real_estate_data.csv"
            },
            "restaurant": {
                "name": "Restaurant & Food Service",
                "icon": "🍽️",
                "description": "Menu performance, customer satisfaction, operational metrics",
                "tiers": {
                    "tier1_essential": {
                        "fields": ["Date", "MenuItem", "Amount"],
                        "description": "Basic sales analysis",
                        "capabilities": ["menu_performance", "sales_trends", "revenue_analysis"]
                    },
                    "tier2_enhanced": {
                        "fields": ["CustomerID", "TimeSlot", "TableID"],
                        "description": "Customer and timing insights",
                        "capabilities": ["customer_behavior", "peak_hours", "table_utilization"]
                    },
                    "tier3_advanced": {
                        "fields": ["OrderID", "Category", "Cost", "Rating", "WaitTime"],
                        "description": "Comprehensive restaurant intelligence",
                        "capabilities": ["profitability", "customer_satisfaction", "operational_efficiency"]
                    }
                },
                "sample_file": "sample_restaurant_data.csv"
            }
        }
    
    def _load_analysis_modules(self) -> Dict[str, Any]:
        """Load analysis module configurations"""
        return {
            "sales_analysis": {
                "modules": ["sales_trend", "top_products", "bottom_products", "seasonality"],
                "description": "Sales performance and trends",
                "icon": "📈"
            },
            "customer_analysis": {
                "modules": ["churn", "cltv", "customer_clusters", "cohort", "repeat_rate"],
                "description": "Customer behavior and value",
                "icon": "👥"
            },
            "operational_analysis": {
                "modules": ["inventory", "stockout_risk", "returns", "profit_margin"],
                "description": "Operations and profitability",
                "icon": "⚙️"
            },
            "marketing_analysis": {
                "modules": ["promo", "sentiment", "acquisition", "basket_analysis"],
                "description": "Marketing effectiveness",
                "icon": "📢"
            },
            "advanced_analysis": {
                "modules": ["forecasting", "pricing", "custom"],
                "description": "Advanced analytics and predictions",
                "icon": "🔮"
            }
        }
    
    def _load_ui_config(self) -> Dict[str, Any]:
        """Load UI configuration"""
        return {
            "tabs": {
                "smart_dashboard": {
                    "name": "📊 Smart Dashboard",
                    "description": "Auto-generated insights and data upload",
                    "priority": 1
                },
                "datagenie": {
                    "name": "🧞‍♂️ DataGenie Chat",
                    "description": "AI-powered natural language Q&A",
                    "priority": 2
                },
                "domain_analysis": {
                    "name": "Domain Analysis",
                    "description": "Specialized analysis for your business type",
                    "priority": 3
                }
            },
            "features": {
                "focus_mode": True,
                "tabbed_answers": True,
                "progressive_disclosure": True,
                "sample_questions_dropdown": True
            },
            "styling": {
                "primary_color": "#667eea",
                "secondary_color": "#764ba2",
                "success_color": "#28a745",
                "warning_color": "#ffc107",
                "error_color": "#dc3545"
            }
        }
    
    def get_domain_config(self, domain_key: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific domain"""
        return self.domains.get(domain_key)
    
    def get_required_fields(self, domain_key: str, tier: str = "tier1_essential") -> List[str]:
        """Get required fields for a domain and tier"""
        domain = self.get_domain_config(domain_key)
        if domain and tier in domain.get("tiers", {}):
            return domain["tiers"][tier]["fields"]
        return []
    
    def get_analysis_capabilities(self, domain_key: str, tier: str = "tier1_essential") -> List[str]:
        """Get analysis capabilities for a domain and tier"""
        domain = self.get_domain_config(domain_key)
        if domain and tier in domain.get("tiers", {}):
            return domain["tiers"][tier]["capabilities"]
        return []
    
    def determine_analysis_tier(self, domain_key: str, available_fields: List[str]) -> str:
        """Determine the analysis tier based on available fields"""
        domain = self.get_domain_config(domain_key)
        if not domain:
            return "tier1_essential"
        
        # Check tiers in reverse order (most advanced first)
        for tier in ["tier3_advanced", "tier2_enhanced", "tier1_essential"]:
            if tier in domain["tiers"]:
                required_fields = domain["tiers"][tier]["fields"]
                if all(field in available_fields for field in required_fields):
                    return tier
        
        return "tier1_essential"
    
    def get_available_analyses(self, domain_key: str, tier: str) -> List[str]:
        """Get available analysis modules for a domain and tier"""
        capabilities = self.get_analysis_capabilities(domain_key, tier)
        available_analyses = []
        
        for category, config in self.analysis_modules.items():
            for capability in capabilities:
                if capability in config["description"].lower() or capability in config["modules"]:
                    available_analyses.extend(config["modules"])
        
        return list(set(available_analyses))  # Remove duplicates
    
    def export_config(self, filepath: str = "config_export.json"):
        """Export current configuration to JSON file"""
        config_data = {
            "domains": self.domains,
            "analysis_modules": self.analysis_modules,
            "ui_config": self.ui_config
        }
        
        with open(filepath, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        return filepath

# Global configuration instance
config = BusinessInsightsConfig()

def get_config() -> BusinessInsightsConfig:
    """Get the global configuration instance"""
    return config
