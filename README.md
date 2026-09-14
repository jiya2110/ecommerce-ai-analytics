\# 🛒 E-commerce AI Analyst



An AI-powered analytics tool that turns plain-English questions into SQL queries, real-time insights, and auto-generated charts — no SQL knowledge required to use it.



🔗 \*\*Live app:\*\* https://ecommerce-ai-analytics-mgpxvvk5ctwpvdg6ay3rw5.streamlit.app/

💻 \*\*Tech stack:\*\* Python · SQLAlchemy · Groq (LLM) · Plotly · Streamlit · MySQL (Aiven)



\---



\## The Business Problem



E-commerce teams generate huge volumes of behavioral data (page views, cart additions, checkouts, purchases) across multiple traffic sources — but most of that data sits unused because answering a simple question like \*"why are we losing customers?"\* requires someone who knows SQL to write, test, and interpret a query.



This creates two problems for a business:

1\. \*\*Bottleneck\*\* — non-technical stakeholders (marketing, product, leadership) have to wait on an analyst for every question, no matter how simple.

2\. \*\*Missed insight\*\* — data that could inform decisions in real time instead sits in dashboards nobody has time to dig into.



This project solves both: it lets anyone ask a question in plain English and get back a real, correct answer — SQL, insight, and visualization — in seconds.



\## Dataset



The dataset (`user\_events`) simulates e-commerce user behavior with the following event types tracked per user:

`page\_view → add\_to\_cart → checkout\_start → payment\_info → purchase`



Each event includes a timestamp, associated user, product, transaction amount (for purchases), and traffic source (organic, paid ads, email, social).



\## Phase 1: Original SQL Analysis



Before adding AI, I did a full manual analysis of the funnel using SQL — CTEs, conditional aggregation, and time-based calculations. Full queries: \[`sql/funnel\_analysis.sql`](sql/funnel\_analysis.sql)



\*\*Key findings:\*\*

\- \*\*Conversion funnel:\*\* Built a 5-stage funnel (view → cart → checkout → payment → purchase) using CTEs and conditional `COUNT(DISTINCT CASE WHEN...)` logic to calculate stage-by-stage conversion rates.

\- \*\*Biggest drop-off point:\*\* The largest user loss happens between \*page view\* and \*add to cart\* — not at checkout, as is commonly assumed. This points to a product-discovery/browsing experience problem rather than a checkout-friction problem.

\- \*\*Funnel by traffic source:\*\* Compared cart and purchase conversion rates across organic, paid ads, email, and social to see which channels bring higher-intent traffic, not just more traffic.

\- \*\*Time-to-conversion:\*\* Measured average minutes between browsing, cart addition, and purchase completion for users who did convert.

\- \*\*Revenue funnel:\*\* Calculated total revenue, average order value, revenue per buyer, and revenue per visitor — then benchmarked average order value (\~$107) against an assumed customer acquisition cost (\~$50), confirming the unit economics are profitable.



\## Phase 2: AI Integration



The manual SQL analysis above answers \*specific\* questions I thought to ask. But it only covers those questions — anyone with a new question still needs someone who knows SQL. So I built an AI layer on top that generalizes this: \*\*ask anything, in plain English, and get the same quality of analysis on demand.\*\*



\### How it works



1\. \*\*Schema-aware prompting\*\* — the app reads the live database schema (table and column names) and includes it in the prompt, so the AI generates SQL that matches the actual database structure rather than guessing.

2\. \*\*Natural language → SQL\*\* — a user's question (e.g. \*"What is the total amount spent per traffic source?"\*) is sent to an LLM (Groq, running Llama/GPT-OSS models) along with the schema, and the model returns a working SQL query.

3\. \*\*Query execution\*\* — the generated SQL runs directly against the live MySQL database (hosted on Aiven), and results are loaded into a DataFrame.

4\. \*\*AI-written insight\*\* — the result set is sent back to the LLM with a prompt asking it to synthesize a 2-3 sentence, plain-English takeaway — not just restate numbers, but identify the key pattern.

5\. \*\*Auto-visualization\*\* — a third LLM call analyzes the shape of the result data (column types, number of rows) and decides the best chart type (bar, line, pie, scatter), which is then rendered with Plotly.

6\. \*\*Streamlit interface\*\* — everything is wrapped in a simple web UI: type a question, click Ask, get SQL + insight + chart + raw data, all on one page.



\### Why this matters (business value)



This turns a one-off SQL analysis into a \*\*reusable, self-serve analytics tool\*\*. A marketing manager can now ask "which channel has the best ROI?" without waiting on a data team — and get a genuinely correct, data-backed answer with a visual, in under 10 seconds.





\## Running it locally



```bash

git clone https://github.com/jiya2110/ecommerce-ai-analytics.git

cd ecommerce-ai-analytics

pip install -r requirements.txt

```



Create a `.env` file with:
GROQ\_API\_KEY=your\_key

DB\_HOST=your\_host

DB\_PORT=your\_port

DB\_USER=your\_user

DB\_PASSWORD=your\_password

DB\_NAME=your\_database



Then run:

```bash

streamlit run app.py

```



\## What's next



\- Support for multi-turn conversations (follow-up questions that build on previous results)

\- Caching repeated queries to reduce API calls

\- User authentication and saved/favorite queries

\- Support for more complex multi-table joins as the schema grows



\---



\*Built by Jiya Jain — \[GitHub](https://github.com/jiya2110)\*

