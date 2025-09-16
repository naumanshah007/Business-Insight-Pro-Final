import streamlit as st
import pandas as pd
from utils import (
    get_required_fields_for_domain,
    get_mandatory_fields_for_domain,
    fuzzy_column_match,
)
import sys
import os

# Add parent directory to path to import genai_client
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from genai_client import profile_data_intelligently

def profile_and_map_columns(df, domain="retail"):
    st.markdown("### 🧩 Step 2: Column Mapping")
    st.write(
        "Map your **data columns** to the standard business schema expected by our analysis engine."
        "<br>💡 Only **mandatory fields** must be selected. You may skip optional ones.",
        unsafe_allow_html=True
    )

    if df is None or df.empty:
        st.error("❌ No data found. Please upload a file first.")
        return None, None

    with st.expander("🔍 Show Data Profile", expanded=False):
        st.markdown("#### Column Types")
        st.dataframe(pd.DataFrame(df.dtypes, columns=["Data Type"]))
        st.markdown("#### Missing Values")
        st.dataframe(pd.DataFrame(df.isnull().sum(), columns=["Missing"]))
        
        # 🤖 AI-Powered Data Quality Assessment
        try:
            data_profile = {
                "columns": df.columns.tolist(),
                "row_count": len(df),
                "data_types": df.dtypes.to_dict(),
                "missing_values": df.isnull().sum().to_dict(),
                "numeric_columns": df.select_dtypes(include=['number']).columns.tolist(),
                "categorical_columns": df.select_dtypes(include=['object']).columns.tolist(),
                "date_columns": [col for col in df.columns if 'date' in col.lower()],
                "unique_values": {col: df[col].nunique() for col in df.columns},
                "sample_data": df.head(3).to_dict('records')
            }
            
            ai_profile = profile_data_intelligently(data_profile, domain)
            
            if ai_profile and "quality_assessment" in ai_profile:
                st.markdown("#### 🤖 AI Data Quality Assessment")
                st.info(ai_profile["quality_assessment"])
                
                if "recommendations" in ai_profile and ai_profile["recommendations"]:
                    st.markdown("#### 💡 AI Recommendations")
                    for rec in ai_profile["recommendations"]:
                        st.markdown(f"• {rec}")
                        
        except Exception as e:
            st.markdown("#### 🤖 AI Data Quality Assessment")
            st.warning("AI-powered data profiling temporarily unavailable. Showing basic analysis.")

    # Get tiered field requirements
    field_tiers = get_required_fields_for_domain(domain)
    mandatory_fields = get_mandatory_fields_for_domain(domain)

    if not field_tiers or not mandatory_fields:
        st.error("⚠️ Required or mandatory fields are not defined for this domain.")
        return None, None

    # Display tiered field information
    st.info(f"🛑 **Essential fields (minimum required):** {', '.join(mandatory_fields)}")
    
    with st.expander("📊 Analysis Capabilities Based on Available Fields", expanded=False):
        st.markdown("**Tier 1 - Essential Fields:**")
        st.markdown(f"- {', '.join(field_tiers['tier1_essential'])}")
        st.markdown("- *Enables:* Basic sales trends, top products, revenue analysis")
        
        st.markdown("**Tier 2 - Enhanced Fields:**")
        st.markdown(f"- {', '.join(field_tiers['tier2_enhanced'])}")
        st.markdown("- *Enables:* Customer analysis, location insights, channel performance")
        
        st.markdown("**Tier 3 - Advanced Fields:**")
        st.markdown(f"- {', '.join(field_tiers['tier3_advanced'])}")
        st.markdown("- *Enables:* Profitability, inventory, sentiment, return analysis")
    
    # Flatten all fields for mapping interface
    all_fields = field_tiers['tier1_essential'] + field_tiers['tier2_enhanced'] + field_tiers['tier3_advanced']

    st.markdown("---")
    st.markdown("#### 🔗 Map Your Columns")
    
    # 🤖 AI-Powered Column Mapping Suggestions
    ai_mapping_suggestions = {}
    try:
        data_profile = {
            "columns": df.columns.tolist(),
            "required_fields": all_fields,
            "sample_data": df.head(3).to_dict('records'),
            "data_types": df.dtypes.to_dict(),
            "unique_values": {col: df[col].nunique() for col in df.columns}
        }
        
        ai_profile = profile_data_intelligently(data_profile, domain)
        if ai_profile and "mapping_suggestions" in ai_profile:
            ai_mapping_suggestions = ai_profile["mapping_suggestions"]
            
    except Exception as e:
        pass  # Continue with basic mapping if AI fails

    cols = st.columns(3)
    user_mapping = {}

    for idx, field in enumerate(all_fields):
        # Try AI suggestion first, then fuzzy matching
        ai_guess = ai_mapping_suggestions.get(field) if ai_mapping_suggestions else None
        fuzzy_guess = fuzzy_column_match(field, df.columns)
        guess = ai_guess if ai_guess and ai_guess in df.columns else fuzzy_guess
        
        with cols[idx % 3]:
            # Add AI suggestion indicator
            label = f"Map: `{field}`"
            if ai_guess and ai_guess in df.columns:
                label += " 🤖"
            
            user_mapping[field] = st.selectbox(
                label,
                options=["-- None --"] + list(df.columns),
                index=(df.columns.get_loc(guess) + 1) if guess else 0,
                key=f"{domain}_{field}_map"
            )

    # 🔎 Validate mandatory fields
    unmapped_mandatory = [
        f for f in mandatory_fields if user_mapping.get(f, "-- None --") == "-- None --"
    ]
    if unmapped_mandatory:
        st.warning(f"⚠️ Please map all mandatory fields: {', '.join(unmapped_mandatory)}")
        return None, None

    # 🧯 Check for duplicates
    selected_columns = [col for col in user_mapping.values() if col != "-- None --"]
    if len(set(selected_columns)) != len(selected_columns):
        st.error("⚠️ Each field must be mapped to a unique column (excluding unselected ones).")
        return None, None

    # ✅ Final mapping
    mapping = {field: col for field, col in user_mapping.items() if col != "-- None --"}

    try:
        mapped_df = df.rename(columns={v: k for k, v in mapping.items()})
    except Exception as e:
        st.error(f"❌ Error during renaming: {e}")
        return None, None

    # Show analysis capabilities based on mapped fields
    available_fields = list(mapping.keys())
    capabilities = get_analysis_capabilities(available_fields, domain)
    
    st.success("✅ Mapping successful! Here's a preview of your standardized dataset:")
    st.dataframe(mapped_df.head(8), use_container_width=True)
    
    # Display available analysis capabilities
    st.markdown("---")
    st.markdown("#### 🎯 Available Analysis Capabilities")
    
    available_analyses = []
    unavailable_analyses = []
    
    for analysis_type, info in capabilities.items():
        if info["available"]:
            available_analyses.append(f"✅ **{analysis_type.replace('_', ' ').title()}**: {info['description']}")
        else:
            missing_fields = [f for f in info["required"] if f not in available_fields]
            unavailable_analyses.append(f"❌ **{analysis_type.replace('_', ' ').title()}**: Missing {', '.join(missing_fields)}")
    
    if available_analyses:
        st.markdown("**Available Analyses:**")
        for analysis in available_analyses:
            st.markdown(f"- {analysis}")
    
    if unavailable_analyses:
        with st.expander("🔒 Additional Analyses Available with More Data", expanded=False):
            st.markdown("**To unlock these analyses, add the missing fields:**")
            for analysis in unavailable_analyses:
                st.markdown(f"- {analysis}")
    
    # Show tier level achieved
    tier_level = 1
    if all(field in available_fields for field in field_tiers['tier2_enhanced']):
        tier_level = 2
    if all(field in available_fields for field in field_tiers['tier3_advanced']):
        tier_level = 3
    
    st.info(f"🎯 **Analysis Level Achieved: Tier {tier_level}** - {'Basic' if tier_level == 1 else 'Enhanced' if tier_level == 2 else 'Advanced'} analysis capabilities")

    return mapped_df, mapping
