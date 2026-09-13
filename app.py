import streamlit as st
from ask_ai import ask_ai_for_sql, run_query, get_insight_summary, get_chart_suggestion, build_chart_figure

st.set_page_config(page_title="E-commerce AI Analyst", layout="centered")

st.title("🛒 E-commerce AI Analyst")
st.write("Ask a question about your e-commerce data in plain English.")

question = st.text_input("Your question", placeholder="e.g. What is the total amount spent per traffic source?")

if st.button("Ask") and question:
    with st.spinner("Generating SQL..."):
        sql = ask_ai_for_sql(question)

    st.subheader("Generated SQL")
    st.code(sql, language="sql")

    try:
        with st.spinner("Running query..."):
            df = run_query(sql)

        if df.empty:
            st.warning("The query ran successfully but returned no results.")
        else:
            st.subheader("Insight")
            with st.spinner("Analyzing results..."):
                insight = get_insight_summary(question, df)
            st.write(insight)

            st.subheader("Visualization")
            with st.spinner("Building chart..."):
                chart_info = get_chart_suggestion(question, df)
                fig = build_chart_figure(df, chart_info)

            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No chart was suitable for this result.")

            st.subheader("Raw Data")
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Error running query: {e}")