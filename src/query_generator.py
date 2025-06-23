"""
SQL query generator using Langchain and OpenAI.
This module translates natural language questions into SQL queries.
"""

import os
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains import create_sql_query_chain
from langchain.utilities import SQLDatabase
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from src.db_connection import get_db_connection

# Load environment variables
load_dotenv()

class SQLQueryGenerator:
    """
    A class to generate SQL queries from natural language questions.
    """

    def __init__(self, db_connection=None, temperature=0):
        """
        Initialize SQL query generator.

        Args:
            db_connection: Database connection object
            temperature (float): Temperature for OpenAI model
        """
        # Get database connection if not provided
        if db_connection is None:
            db_connection = get_db_connection()

        # Connect to database
        engine = db_connection.connect()

        # Create SQLDatabase object
        self.db = SQLDatabase(engine)

        # Create OpenAI language model
        self.llm = ChatOpenAI(temperature=temperature, model_name="gpt-4.1-nano")

        # Create SQL query chain
        self.chain = create_sql_query_chain(self.llm, self.db)

        # Define table schema for context
        self.table_schema = """
        Table users {
            user_id INTEGER [pk]
            name TEXT [not null]
            email TEXT [unique]
            registration_date TEXT [not null]
            is_active INTEGER [default: 1]
            is_dormant INTEGER [default: 0]
            is_cancelled INTEGER [default: 0]
            last_activity_date TEXT
        }

        Table categories {
            category_id INTEGER [pk]
            category_name TEXT [not null, unique]
        }

        Table purchases {
            purchase_id INTEGER [pk]
            user_id INTEGER [ref: > users.user_id, not null]
            amount REAL [not null]
            purchase_date TEXT [not null]
            category_id INTEGER [ref: > categories.category_id, not null]
        }

        Note:
        - is_active: 1 for active, 0 for inactive (do not use this flag to determine if a user is active)
        - is_dormant: 1 for dormant, 0 for not dormant (do not use this flag to determine if a user is dormant)
        - is_cancelled: 1 for cancelled, 0 for not cancelled
        - Active users: Users who have made at least one purchase in the specified time period and are not cancelled
        - Dormant users: Users who have not made any purchases in the specified time period (e.g., 90 days) and are not cancelled
        - Cancelled users: is_cancelled=1
        - purchase_date and registration_date format: 'YYYY-MM-DD'
        """

        # Define custom prompt template for SQL generation
        self.custom_prompt = PromptTemplate(
            input_variables=["question", "table_schema"],
            template="""
            You are a SQL expert. Given the following database schema and a question, 
            generate a SQL query that answers the question.

            Database Schema:
            {table_schema}

            Question: {question}

            Important guidelines:
            1. Always exclude cancelled users (is_cancelled=1) unless explicitly asked to include them.
            2. For time-based queries, use date functions like date(), datetime(), strftime().
            3. For "active users", count users on a month-by-month basis. An active user in a given month is someone who:
               a) Has not cancelled by the end of that month (is_cancelled=0)
               b) Made at least one credit card payment during that specific month

               This means a user could be active in April, dormant in May, and active again in June.

               Example query for monthly active users over the past 6 months:
               ```
               WITH month_list AS (
                 SELECT 
                   date(date('now', 'start of month', '-5 months'), 'start of month') AS month_start,
                   date(date('now', 'start of month', '-5 months'), 'start of month', '+1 month', '-1 day') AS month_end
                 UNION ALL SELECT 
                   date(date('now', 'start of month', '-4 months'), 'start of month'),
                   date(date('now', 'start of month', '-4 months'), 'start of month', '+1 month', '-1 day')
                 UNION ALL SELECT 
                   date(date('now', 'start of month', '-3 months'), 'start of month'),
                   date(date('now', 'start of month', '-3 months'), 'start of month', '+1 month', '-1 day')
                 UNION ALL SELECT 
                   date(date('now', 'start of month', '-2 months'), 'start of month'),
                   date(date('now', 'start of month', '-2 months'), 'start of month', '+1 month', '-1 day')
                 UNION ALL SELECT 
                   date(date('now', 'start of month', '-1 months'), 'start of month'),
                   date(date('now', 'start of month', '-1 months'), 'start of month', '+1 month', '-1 day')
                 UNION ALL SELECT 
                   date(date('now', 'start of month'), 'start of month'),
                   date(date('now', 'start of month', '+1 month', '-1 day'))
               )
               SELECT 
                 strftime('%Y-%m', m.month_start) AS month,
                 COUNT(DISTINCT p.user_id) AS active_users
               FROM 
                 month_list m
               LEFT JOIN 
                 purchases p ON p.purchase_date >= m.month_start AND p.purchase_date <= m.month_end
               JOIN 
                 users u ON u.user_id = p.user_id AND u.is_cancelled = 0
               GROUP BY 
                 month
               ORDER BY 
                 month;
               ```
               Note that this query does NOT filter by is_active=1 because we're defining active users based on their purchase activity in each specific month, not their status flag.

               Example query for calculating monthly average purchase amount for active users over the past 6 months:
               ```
               WITH month_ranges AS (
                 SELECT 
                   date(date('now', 'start of month', '-5 months'), 'start of month') AS month_start,
                   date(date('now', 'start of month', '-5 months'), 'start of month', '+1 month', '-1 day') AS month_end
                 UNION ALL SELECT 
                   date(date('now', 'start of month', '-4 months'), 'start of month'),
                   date(date('now', 'start of month', '-4 months'), 'start of month', '+1 month', '-1 day')
                 UNION ALL SELECT 
                   date(date('now', 'start of month', '-3 months'), 'start of month'),
                   date(date('now', 'start of month', '-3 months'), 'start of month', '+1 month', '-1 day')
                 UNION ALL SELECT 
                   date(date('now', 'start of month', '-2 months'), 'start of month'),
                   date(date('now', 'start of month', '-2 months'), 'start of month', '+1 month', '-1 day')
                 UNION ALL SELECT 
                   date(date('now', 'start of month', '-1 months'), 'start of month'),
                   date(date('now', 'start of month', '-1 months'), 'start of month', '+1 month', '-1 day')
                 UNION ALL SELECT 
                   date(date('now', 'start of month'), 'start of month'),
                   date(date('now', 'start of month', '+1 month', '-1 day'))
               )
               SELECT 
                 strftime('%Y-%m', mr.month_start) AS month,
                 CASE 
                   WHEN COUNT(DISTINCT p.user_id) = 0 THEN 0
                   ELSE ROUND(SUM(p.amount) / COUNT(DISTINCT p.user_id), 2)
                 END AS avg_purchase_amount
               FROM 
                 month_ranges mr
               LEFT JOIN 
                 purchases p ON p.purchase_date >= mr.month_start AND p.purchase_date <= mr.month_end
               JOIN 
                 users u ON u.user_id = p.user_id AND u.is_cancelled = 0
               GROUP BY 
                 month
               ORDER BY 
                 month;
               ```
               This query calculates the average purchase amount per active user for each month by dividing the total purchase amount by the number of distinct active users in that month.
            4. For "dormant users", define them as users who have not made any purchases in a specific time period (typically 90 days) and are not cancelled (is_cancelled=0). Do NOT use the is_dormant flag.
               Example query for dormant users:
               ```
               SELECT 
                 COUNT(DISTINCT u.user_id) AS dormant_users
               FROM 
                 users u
               WHERE 
                 u.is_cancelled = 0
                 AND NOT EXISTS (
                   SELECT 1 
                   FROM purchases p 
                   WHERE p.user_id = u.user_id 
                   AND p.purchase_date >= date('now', '-90 days')
                 )
               ```
            5. For queries about "high/medium/low spenders", define appropriate thresholds based on the data.
            6. For queries about user preferences, look at their purchase categories.
            7. Always qualify column names with table names or aliases in all contexts, including:
               - When joining tables (e.g., users.user_id, purchases.user_id)
               - In WHERE clauses (e.g., users.is_cancelled = 0)
               - In aggregate functions (e.g., COUNT(user_purchase_total.user_id))
               - In GROUP BY and ORDER BY clauses
            8. IMPORTANT: Use the exact Japanese category names as they appear in the database (e.g., '美容', '旅行', 'ペット'). 
               DO NOT translate category names to English. For example, use '美容' instead of 'Beauty'.
            9. Return only the SQL query without any explanation.

            SQL Query:
            """
        )

        # Create custom LLM chain
        self.custom_chain = LLMChain(
            llm=self.llm,
            prompt=self.custom_prompt
        )

    def generate_query(self, question):
        """
        Generate SQL query from natural language question.

        Args:
            question (str): Natural language question

        Returns:
            str: SQL query
        """
        # For queries about active users, always use our custom prompt
        if "アクティブ" in question or "active" in question.lower():
            query = self.custom_chain.run(question=question, table_schema=self.table_schema)
            return query

        try:
            # Try using the Langchain SQL chain first for other queries
            query = self.chain.invoke(question)
            return query
        except Exception as e:
            # Fall back to custom chain if there's an error
            query = self.custom_chain.run(question=question, table_schema=self.table_schema)
            return query

    def execute_query(self, query):
        """
        Execute SQL query and return results.

        Args:
            query (str): SQL query

        Returns:
            list: Query results
        """
        try:
            return self.db.run(query)
        except Exception as e:
            return f"Error executing query: {str(e)}"
