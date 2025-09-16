import difflib
import pandas as pd
import io

def load_config():
    """
    Returns a dictionary with global app config.
    Add domains, colors, question banks, etc.
    """
    return {
        "domains": [
            {"label": "Retail / Sales", "key": "retail"},
            {"label": "Real Estate", "key": "real_estate"}
            # Add more domains here
        ]
    }

def get_required_fields_for_domain(domain):
    """
    Returns a list of required + optional fields needed for all questions in the given domain.
    This ensures that the column mapping UI includes every field needed for full functionality.
    """
    if domain == "retail":
        return [
            # Required for most questions
            "Date",          # Purchase date
            "Product",       # Product name/category
            "Amount",        # Transaction amount

            # Optional but needed for extended analysis
            "CustomerID",    # For churn, LTV, clustering
            "OrderID",       # For repeat purchase, AOV
            "StoreID",       # For location-based trends
            "Location",      # Alt. to StoreID
            "Channel",       # Sales channel (Online/In-Store)
            "Gender",        # For demographic insights
            "Age",           # For customer segmentation
            "Cost",          # For profit margin calculations
            "Inventory",     # For stockout risk detection
            "IsReturned",    # For return/refund rate
            "Feedback"       # For sentiment analysis
        ]
    elif domain == "real_estate":
        return [
            "SaleDate", "Suburb", "SalePrice", "Agent"
        ]
    else:
        return []

def get_mandatory_fields_for_question(question_id, domain):
    """
    Return required fields for specific business questions.
    Used to dynamically validate if question can be run.
    """
    # Retail-specific logic
    if domain == "retail":
        return {
            "top_products": ["Product", "Amount"],
            "bottom_products": ["Product", "Amount"],
            "sales_trend": ["Date", "Amount"],
            "seasonality": ["Date", "Amount"],
            "avg_order_value": ["OrderID", "Amount"],
            "sales_by_location": ["Location", "Amount"],
            "sales_by_channel": ["Channel", "Amount"],
            "customer_clusters": ["CustomerID", "Amount"],
            "repeat_rate": ["CustomerID", "OrderID"],
            "basket_analysis": ["OrderID", "Product"],
            "churn_prediction": ["CustomerID"],
            "sales_forecast": ["Date", "Amount"],
            "promo_effect": ["Amount"],
            "price_elasticity": ["Product", "Amount"],
            "cost_profit": ["Cost", "Amount"],
            "stock_alerts": ["Inventory", "Product"],
            "sentiment_reviews": ["Feedback"],
            "return_rate": ["Product", "IsReturned"],
            "lifetime_value": ["CustomerID", "Amount", "Date"],
            "next_best_action": ["CustomerID", "Product", "Amount"],
        }.get(question_id, [])
    
    # Real estate-specific logic
    elif domain == "real_estate":
        return {
            "top_suburbs": ["Suburb", "SalePrice"],
            "price_trend": ["SaleDate", "SalePrice"],
            "volume_trend": ["SaleDate"],
            "agent_performance": ["Agent", "SalePrice"],
            "time_on_market": ["Suburb"],
            "price_distribution": ["SalePrice"],
            "property_type_split": ["PropertyType"],
            "revenue_per_property_type": ["PropertyType", "SalePrice"],
            "price_clusters": ["SalePrice"],
            "price_forecast": ["SaleDate", "SalePrice"],
            "agent_churn": ["Agent"],
            "buyer_segments": ["BuyerID", "SalePrice"],
            "promotion_effect": ["PromoCode", "SalePrice"],
            "outlier_sales": ["SalePrice"],
            "price_elasticity": ["SalePrice"],
            "investment_risk": ["LiquidityScore"],
            "sentiment_feedback": ["Feedback"],
            "next_best_listing": ["Suburb", "SalePrice"],
            "mortgage_default": ["LoanAmount", "Defaulted"],
            "portfolio_value": ["PortfolioID", "SalePrice", "SaleDate"],
        }.get(question_id, [])
    
    return []


def get_sample_file(domain):
    """
    Returns a sample file with the basic required structure for each domain.
    """
    if domain == "retail":
        sample = pd.DataFrame({
            "Date": ["2024-06-01", "2024-06-02"],
            "Product": ["Coffee", "Tea"],
            "Amount": [230, 170],
            "CustomerID": [101, 102],
            "OrderID": [1001, 1002],
            "StoreID": [1, 2],
            "Channel": ["Online", "In-Store"],
            "Gender": ["Male", "Female"],
            "Age": [34, 28],
            "Cost": [120, 90],
            "Inventory": [50, 20],
            "IsReturned": [False, True],
            "Feedback": ["Loved it!", "Was okay"]
        })
        buffer = io.StringIO()
        sample.to_csv(buffer, index=False)
        return {
            "data": buffer.getvalue(),
            "file_name": "retail_sample.csv",
            "mime": "text/csv"
        }

    elif domain == "real_estate":
        sample = pd.DataFrame({
            "SaleDate": ["2024-06-01", "2024-06-02"],
            "Suburb": ["Ponsonby", "Mt Eden"],
            "SalePrice": [1300000, 900000],
            "Agent": ["Alice Smith", "John Lee"]
        })
        buffer = io.StringIO()
        sample.to_csv(buffer, index=False)
        return {
            "data": buffer.getvalue(),
            "file_name": "real_estate_sample.csv",
            "mime": "text/csv"
        }
    return None

def fuzzy_column_match(field, user_columns):
    """
    Finds the closest user column to a standard field name using fuzzy matching.
    """
    user_columns = list(user_columns)
    if len(user_columns) == 0:
        return None
    matches = difflib.get_close_matches(field.lower(), [c.lower() for c in user_columns], n=1, cutoff=0.6)
    if matches:
        for c in user_columns:
            if c.lower() == matches[0]:
                return c
    return None
def get_mandatory_fields_for_domain(domain):
    """
    Returns only the absolutely essential fields needed for basic analysis.
    This allows businesses with minimal data to still get insights.
    """
    if domain == "retail":
        return ["Date", "Product", "Amount"]  # Just the basics
    elif domain == "real_estate":
        return ["SaleDate", "Suburb", "SalePrice"]  # Just the basics
    else:
        return []

def get_analysis_capabilities(available_fields, domain="retail"):
    """
    Determines what analysis capabilities are available based on mapped fields.
    Returns a dictionary with available analysis types and their requirements.
    """
    if domain == "retail":
        capabilities = {
            "basic_sales_analysis": {
                "required": ["Date", "Product", "Amount"],
                "available": all(field in available_fields for field in ["Date", "Product", "Amount"]),
                "description": "Basic sales trends, top products, revenue analysis"
            },
            "customer_analysis": {
                "required": ["CustomerID"],
                "available": "CustomerID" in available_fields,
                "description": "Customer segmentation, repeat purchase analysis, churn prediction"
            },
            "location_analysis": {
                "required": ["Location"],
                "available": "Location" in available_fields,
                "description": "Sales by location, regional performance"
            },
            "channel_analysis": {
                "required": ["Channel"],
                "available": "Channel" in available_fields,
                "description": "Online vs in-store performance, channel optimization"
            },
            "profitability_analysis": {
                "required": ["Cost"],
                "available": "Cost" in available_fields,
                "description": "Profit margins, cost analysis, pricing optimization"
            },
            "inventory_analysis": {
                "required": ["Inventory"],
                "available": "Inventory" in available_fields,
                "description": "Stock levels, stockout risk, inventory optimization"
            },
            "sentiment_analysis": {
                "required": ["Feedback"],
                "available": "Feedback" in available_fields,
                "description": "Customer satisfaction, feedback analysis"
            },
            "return_analysis": {
                "required": ["IsReturned"],
                "available": "IsReturned" in available_fields,
                "description": "Return rates, product quality analysis"
            }
        }
    else:
        capabilities = {
            "basic_sales_analysis": {
                "required": ["SaleDate", "Suburb", "SalePrice"],
                "available": all(field in available_fields for field in ["SaleDate", "Suburb", "SalePrice"]),
                "description": "Basic property sales trends, top suburbs, price analysis"
            }
        }
    
    return capabilities
