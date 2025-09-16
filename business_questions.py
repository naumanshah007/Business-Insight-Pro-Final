import streamlit as st
from analysis import run_analysis_for_question
from question_bank import get_questions_for_domain, get_mandatory_fields_for_question
import sys
import os

# Add parent directory to path to import genai_client
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from genai_client import generate_smart_questions

def business_questions_workflow(df, mapping, domain="retail"):
    st.markdown("### 🧠 Step 4: Business Insights")
    st.info("Key questions answered from your data with visual and statistical explanations.")

    # Get available analysis capabilities
    available_fields = list(mapping.keys())
    capabilities = get_analysis_capabilities(available_fields, domain)
    
    # Show analysis level achieved
    field_tiers = get_required_fields_for_domain(domain)
    tier_level = 1
    if all(field in available_fields for field in field_tiers['tier2_enhanced']):
        tier_level = 2
    if all(field in available_fields for field in field_tiers['tier3_advanced']):
        tier_level = 3
    
    st.success(f"🎯 **Analysis Level: Tier {tier_level}** - {'Basic' if tier_level == 1 else 'Enhanced' if tier_level == 2 else 'Advanced'} insights available")

    # ✅ Deduplicate questions by ID and filter based on available data
    raw_questions = get_questions_for_domain(domain)
    questions = []
    seen_ids = set()
    
    for q in raw_questions:
        if q["id"] not in seen_ids:
            # Check if this question can be answered with available data
            required_fields = get_mandatory_fields_for_question(q["id"], domain)
            if all(field in available_fields for field in required_fields):
                questions.append(q)
                seen_ids.add(q["id"])
            else:
                # Add to a separate list for unavailable questions
                missing_fields = [f for f in required_fields if f not in available_fields]
                q["missing_fields"] = missing_fields
                q["unavailable"] = True
                questions.append(q)
                seen_ids.add(q["id"])
    
    # 🤖 Generate smart questions based on data structure
    smart_questions_key = f"{domain}_smart_questions"
    if smart_questions_key not in st.session_state:
        try:
            # Prepare data structure for smart question generation
            data_structure = {
                "columns": df.columns.tolist(),
                "row_count": len(df),
                "data_types": df.dtypes.to_dict(),
                "numeric_columns": df.select_dtypes(include=['number']).columns.tolist(),
                "categorical_columns": df.select_dtypes(include=['object']).columns.tolist(),
                "date_columns": [col for col in df.columns if 'date' in col.lower()],
                "sample_values": {col: df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else None 
                                for col in df.columns[:5]}  # Sample first 5 columns
            }
            
            smart_questions = generate_smart_questions(data_structure, domain)
            
            # Convert smart questions to the expected format
            smart_question_objects = []
            for i, question_text in enumerate(smart_questions[:5]):  # Limit to 5 smart questions
                smart_question_objects.append({
                    "id": f"smart_question_{i+1}",
                    "text": question_text,
                    "desc": "AI-generated question based on your data structure",
                    "why_it_matters": "This question was automatically generated to help you discover insights specific to your data."
                })
            
            st.session_state[smart_questions_key] = smart_question_objects
            
        except Exception as e:
            st.session_state[smart_questions_key] = []
            # Don't show error to user, just use standard questions
    
    # Add smart questions to the main questions list
    smart_questions = st.session_state.get(smart_questions_key, [])
    questions.extend(smart_questions)
    
    # Show smart questions section if available
    if smart_questions:
        with st.expander("🤖 AI-Generated Smart Questions", expanded=False):
            st.markdown("**These questions were automatically generated based on your data structure:**")
            for sq in smart_questions:
                st.markdown(f"• {sq['text']}")
            st.markdown("---")
    
    # Separate available and unavailable questions
    available_questions = [q for q in questions if not q.get("unavailable", False)]
    unavailable_questions = [q for q in questions if q.get("unavailable", False)]
    
    # Show unavailable questions with field requirements
    if unavailable_questions:
        with st.expander("🔒 Additional Questions Available with More Data", expanded=False):
            st.markdown("**These questions require additional fields in your data:**")
            for q in unavailable_questions:
                st.markdown(f"• **{q['text']}**")
                st.markdown(f"  *Missing fields: {', '.join(q['missing_fields'])}*")
                st.markdown(f"  *{q.get('desc', '')}*")
            st.markdown("---")
    
    # Update questions list to only include available questions
    questions = available_questions

    # 🧠 Unique identifiers instead of index
    answered_key = f"{domain}_answered_ids"
    results_key = f"{domain}_results"
    current_key = f"{domain}_current_id"

    # ✅ Init session state
    if answered_key not in st.session_state:
        st.session_state[answered_key] = []
    if results_key not in st.session_state:
        st.session_state[results_key] = {}
    if current_key not in st.session_state:
        # start with first unanswered question
        first_unanswered = next((q["id"] for q in questions if q["id"] not in st.session_state[answered_key]), None)
        st.session_state[current_key] = first_unanswered

    # ✅ Developer button to force reset
    if st.button("🧹 Force Clear State", key=f"reset_{domain}"):
        st.session_state[answered_key] = []
        st.session_state[results_key] = {}
        st.session_state[current_key] = questions[0]["id"]
        st.experimental_rerun()

    # ✅ Render previously answered questions
    for q in questions:
        if q["id"] in st.session_state[answered_key]:
            result = st.session_state[results_key].get(q["id"], {})
            with st.expander(f"✅ {q['text']}", expanded=False):
                st.markdown(f"**Question:** {q['text']}")
                st.markdown(f"**Answer:** {result.get('summary', 'No summary.')}")
                if result.get("fig"):
                    st.plotly_chart(result["fig"], use_container_width=True)
                if result.get("table") is not None:
                    st.dataframe(result["table"])

    # ✅ Check if all done
    unanswered = [q for q in questions if q["id"] not in st.session_state[answered_key]]
    if not unanswered:
        st.success("🎉 All questions completed!")
        st.balloons()
        return

    # ✅ Show current question
    current_question = next((q for q in questions if q["id"] == st.session_state[current_key]), None)
    if not current_question:
        st.warning("No valid question selected.")
        return

    st.markdown("---")
    with st.expander(f"🔍 {current_question['text']}", expanded=True):
        st.markdown(f"**Question:** {current_question['text']}")
        st.caption(current_question.get("desc", ""))

        required = get_mandatory_fields_for_question(current_question['id'], domain)
        missing = [f for f in required if f not in df.columns]
        if missing:
            st.warning(f"⚠️ Missing fields: {', '.join(missing)}")
        else:
            extra = {}
            if current_question['id'] in ["automl_classification", "automl_regression", "churn_prediction"]:
                suggested = next(
                    (col for col in df.columns if any(k in col.lower() for k in ["churn", "target", "label", "class", "y"])),
                    df.columns[0]
                )
                target = st.selectbox(
                    "🎯 Select target column:",
                    options=df.columns.tolist(),
                    index=df.columns.get_loc(suggested),
                    key=f"target_{current_question['id']}"
                )
                extra['target'] = target

            result = run_analysis_for_question(df, mapping, current_question, domain, **extra)

            st.markdown(f"**Answer:** {result['summary']}")
            if result.get("fig"):
                st.plotly_chart(result["fig"], use_container_width=True)
            if result.get("table") is not None:
                st.dataframe(result["table"])

            # ✅ Save result & move to next
            st.session_state[answered_key].append(current_question['id'])
            st.session_state[results_key][current_question['id']] = result

    # ✅ Navigation
    st.markdown("---")
    next_question = next((q for q in questions if q["id"] not in st.session_state[answered_key]), None)
    if next_question and st.button("➡️ Next Question", key=f"next_{current_question['id']}"):
        st.session_state[current_key] = next_question["id"]
        st.experimental_rerun()

    st.caption(f"🔗 Powered by Business Insights Pro | Domain: **{domain.title()}**")
