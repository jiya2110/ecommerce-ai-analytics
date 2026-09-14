import os
from dotenv import load_dotenv
from groq import Groq
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL
import pandas as pd
import plotly.express as px
import json

# Load the API key from .env
load_dotenv()
client = Groq()  # automatically reads GROQ_API_KEY from environment

# --- Database connection (now reads from .env, connects to Aiven with SSL) ---
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_NAME = os.getenv("DB_NAME")

connection_url = URL.create(
    "mysql+mysqlconnector",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
)
engine = create_engine(connection_url, connect_args={"ssl_disabled": False})

# --- Pull schema as text (for the AI prompt) ---
inspector = inspect(engine)
schema_lines = []
for table_name in inspector.get_table_names():
    columns = inspector.get_columns(table_name)
    col_list = ", ".join(f"{col['name']} ({col['type']})" for col in columns)
    schema_lines.append(f"Table {table_name}: {col_list}")
schema_text = "\n".join(schema_lines)


def ask_ai_for_sql(question: str) -> str:
    """Send a natural language question + schema to Groq, get back a SQL query."""
    prompt = f"""You are a MySQL expert. Given this database schema:

{schema_text}

Write a single MySQL query that answers this question: "{question}"

Rules:
- Return ONLY the SQL query, nothing else — no explanation, no markdown code fences.
- Use proper MySQL syntax.
- If the question can't be answered with this schema, return: SELECT 'Cannot answer with available data' AS message;
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    sql_query = response.choices[0].message.content.strip()
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
    return sql_query


def run_query(sql_query: str) -> pd.DataFrame:
    """Execute the SQL query and return results as a DataFrame."""
    with engine.connect() as conn:
        result = pd.read_sql(text(sql_query), conn)
    return result


def get_insight_summary(question: str, df: pd.DataFrame) -> str:
    """Ask the AI to summarize the result in plain English."""
    sample_data = df.head(20).to_string(index=False)

    prompt = f"""A user asked: "{question}"

Here is the query result (showing up to 20 rows):
{sample_data}

Write a 2-3 sentence plain-English summary of what this data shows. Highlight the most important pattern, trend, or standout number. Do not repeat raw numbers row by row — synthesize an insight. Do not use markdown formatting."""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


def get_chart_suggestion(question: str, df: pd.DataFrame) -> dict:
    """Ask the AI what chart type fits this data best."""
    columns_info = ", ".join(f"{col} ({df[col].dtype})" for col in df.columns)
    sample_rows = df.head(5).to_string(index=False)

    prompt = f"""A user asked: "{question}"

The query result has these columns: {columns_info}
Sample rows:
{sample_rows}

Suggest the best chart to visualize this. Respond ONLY with valid JSON, no explanation, no markdown fences, in this exact format:
{{"chart_type": "bar" or "line" or "pie" or "scatter" or "none", "x": "column_name", "y": "column_name", "title": "short chart title"}}

Use "none" if the data doesn't suit a chart (e.g. a single value or text message)."""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def show_chart(df: pd.DataFrame, chart_info: dict):
    """Render the chart based on the AI's suggestion (opens in browser tab — used by the CLI script)."""
    chart_type = chart_info.get("chart_type", "none")
    x = chart_info.get("x")
    y = chart_info.get("y")
    title = chart_info.get("title", "Result")

    if chart_type == "none" or not x or not y:
        print("\n(No chart suggested for this result.)")
        return

    if chart_type == "bar":
        fig = px.bar(df, x=x, y=y, title=title)
    elif chart_type == "line":
        fig = px.line(df, x=x, y=y, title=title)
    elif chart_type == "pie":
        fig = px.pie(df, names=x, values=y, title=title)
    elif chart_type == "scatter":
        fig = px.scatter(df, x=x, y=y, title=title)
    else:
        print("\n(Unrecognized chart type, skipping visualization.)")
        return

    fig.show()


def build_chart_figure(df: pd.DataFrame, chart_info: dict):
    """Same as show_chart, but returns the figure instead of opening a browser tab (used by the Streamlit app)."""
    chart_type = chart_info.get("chart_type", "none")
    x = chart_info.get("x")
    y = chart_info.get("y")
    title = chart_info.get("title", "Result")

    if chart_type == "none" or not x or not y:
        return None

    if chart_type == "bar":
        return px.bar(df, x=x, y=y, title=title)
    elif chart_type == "line":
        return px.line(df, x=x, y=y, title=title)
    elif chart_type == "pie":
        return px.pie(df, names=x, values=y, title=title)
    elif chart_type == "scatter":
        return px.scatter(df, x=x, y=y, title=title)
    else:
        return None


if __name__ == "__main__":
    question = input("Ask a question about your e-commerce data: ")
    sql = ask_ai_for_sql(question)
    print("\nGenerated SQL:\n", sql)

    try:
        df = run_query(sql)
        print("\nResults:\n", df)

        if not df.empty:
            insight = get_insight_summary(question, df)
            print("\nInsight:\n", insight)

            chart_info = get_chart_suggestion(question, df)
            print("\nChart suggestion:", chart_info)
            show_chart(df, chart_info)
    except Exception as e:
        print("\nError running query:", e)