def get_questions_for_domain(domain):
    if domain == "retail":
        return [
            {
                "id": "top_products",
                "text": "Which products bring in the most money?",
                "desc": "Shows the top 10 products that generate the highest sales.",
                "why_it_matters": "Helps you focus on your best-performing products and increase their visibility."
            },
            {
                "id": "bottom_products",
                "text": "Which products sell the least?",
                "desc": "Displays the 10 lowest-selling products.",
                "why_it_matters": "Useful to decide what to discount, stop selling, or promote differently."
            },
            {
                "id": "sales_trend",
                "text": "How have sales changed month by month?",
                "desc": "Tracks monthly sales for the past year.",
                "why_it_matters": "Helps spot growth or decline trends and plan inventory and marketing."
            },
            {
                "id": "seasonality",
                "text": "Are there seasonal trends in sales?",
                "desc": "Finds patterns in monthly sales over time.",
                "why_it_matters": "Helps prepare for high-demand seasons (like holidays or end-of-year spikes)."
            },
            {
                "id": "avg_order_value",
                "text": "How much do customers spend per order?",
                "desc": "Calculates the average amount spent per customer order.",
                "why_it_matters": "Useful to measure how valuable each order is and track improvements over time."
            },
            {
                "id": "sales_by_location",
                "text": "Where are most of my sales coming from?",
                "desc": "Highlights top-performing locations or branches.",
                "why_it_matters": "Lets you invest more in high-performing areas and fix weak ones."
            },
            {
                "id": "sales_by_channel",
                "text": "Which sales channels are performing better?",
                "desc": "Compares sales from different channels like online vs in-store.",
                "why_it_matters": "Helps you understand where to focus your efforts (website, retail store, etc)."
            },
            {
                "id": "customer_clusters",
                "text": "How are my customers grouped by spend?",
                "desc": "Groups customers into spend levels like low, medium, high.",
                "why_it_matters": "Helps tailor offers for loyal customers or re-engage lower spenders."
            },
            {
                "id": "repeat_rate",
                "text": "How many customers come back again?",
                "desc": "Shows the percentage of customers who placed more than one order.",
                "why_it_matters": "Higher repeat rates show strong brand loyalty. Useful for retention strategies."
            },
            {
                "id": "basket_analysis",
                "text": "Which products are bought together?",
                "desc": "Analyzes popular product combinations (market basket analysis).",
                "why_it_matters": "Helps with upselling or bundling products in promotions."
            },
            {
                "id": "churn_prediction",
                "text": "Which customers are at risk of leaving?",
                "desc": "Predicts customers likely to stop buying using historical data.",
                "why_it_matters": "Helps you take action early (e.g., send offers or follow-ups)."
            },
            {
                "id": "sales_forecast",
                "text": "What will sales look like in the next 3 months?",
                "desc": "Estimates sales using recent trends and patterns.",
                "why_it_matters": "Useful for stock planning and budgeting."
            },
            {
                "id": "promo_effect",
                "text": "Do discounts and promo codes help increase sales?",
                "desc": "Looks at how promotions affect buying behavior.",
                "why_it_matters": "Tells you if promos are working or just cutting profits."
            },
            {
                "id": "price_elasticity",
                "text": "What happens if I raise or lower prices?",
                "desc": "Estimates how price changes affect sales volume.",
                "why_it_matters": "Helps you price products smarter to balance profit and demand."
            },
            {
                "id": "cost_profit",
                "text": "How much profit am I making on each order?",
                "desc": "Uses cost and selling price to calculate profit margins.",
                "why_it_matters": "Vital to know your profitability, not just revenue."
            },
            {
                "id": "stock_alerts",
                "text": "Which products are at risk of running out?",
                "desc": "Flags products with low stock and steady demand.",
                "why_it_matters": "Helps prevent stockouts and missed sales opportunities."
            },
            {
                "id": "sentiment_reviews",
                "text": "How do customers feel about our products?",
                "desc": "Uses AI to analyze positive or negative reviews.",
                "why_it_matters": "Gives a quick idea of customer satisfaction and areas of improvement."
            },
            {
                "id": "return_rate",
                "text": "Which products are returned most often?",
                "desc": "Tracks return/refund rates for each product or category.",
                "why_it_matters": "Highlights product issues or misaligned customer expectations."
            },
            {
                "id": "lifetime_value",
                "text": "What is the lifetime value of a customer?",
                "desc": "Estimates total revenue from a customer over time.",
                "why_it_matters": "Helps you measure the long-term value of loyal customers."
            },
            {
                "id": "next_best_action",
                "text": "What should I offer each customer next?",
                "desc": "Uses AI to recommend products for each customer.",
                "why_it_matters": "Improves cross-sell and upsell by predicting customer needs."
            }
        ]
    elif domain == "real_estate":
        return [
            {
                "id": "top_suburbs",
                "text": "Top-selling suburbs by total value",
                "desc": "Shows the highest-grossing real estate suburbs.",
                "why_it_matters": "Lets agents or investors know where the market is hottest."
            }
        ]
    return []



def get_mandatory_fields_for_question(question_id, domain):
    if domain == "retail":
        mapping = {
            "top_products": ["Product", "Amount"],
            "bottom_products": ["Product", "Amount"],
            "sales_trend": ["Date", "Amount"],
            "seasonality": ["Date", "Amount"],
            "avg_order_value": ["Amount"],
            "sales_by_location": ["Location", "Amount"],
            "sales_by_channel": ["Channel", "Amount"],
            "customer_clusters": ["CustomerID", "Amount"],
            "repeat_rate": ["CustomerID"],
            "basket_analysis": ["CustomerID", "Product"],
            "churn_prediction": ["CustomerID", "Amount", "Churn"],
            "sales_forecast": ["Date", "Amount"],
            "promo_effect": ["Promo", "Amount"],
            "price_elasticity": ["Product", "Amount", "Price"],
            "cost_profit": ["Amount", "Cost"],
            "stock_alerts": ["Product", "Inventory", "Amount", "Date"],
            "sentiment_reviews": ["Feedback"],
            "return_rate": ["Product", "IsReturned"],
            "lifetime_value": ["CustomerID", "Date", "Amount"],
            "next_best_action": ["CustomerID", "Product", "Amount"],
        }
        return mapping.get(question_id, [])
    elif domain == "real_estate":
        return []
    else:
        return []
