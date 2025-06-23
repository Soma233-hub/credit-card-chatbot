"""
Chatbot for credit card user database queries.
This module handles the conversation flow and response generation.
"""

import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import io
import base64
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from src.query_generator import SQLQueryGenerator

# Load environment variables
load_dotenv()

class CreditCardChatbot:
    """
    A chatbot for answering questions about credit card user data.
    """
    
    def __init__(self, temperature=0):
        """
        Initialize chatbot.
        
        Args:
            temperature (float): Temperature for OpenAI model
        """
        # Create SQL query generator
        self.query_generator = SQLQueryGenerator(temperature=temperature)
        
        # Create OpenAI language model for response generation
        self.llm = ChatOpenAI(temperature=temperature, model_name="gpt-3.5-turbo")
        
        # Define prompt template for response generation
        self.response_prompt = PromptTemplate(
            input_variables=["question", "sql_query", "query_result"],
            template="""
            あなたはクレジットカード会社のマーケティング部門向けのアシスタントです。
            ユーザーの質問に対して、SQLクエリを実行した結果を元に、日本語で丁寧に回答してください。
            
            ユーザーの質問: {question}
            
            実行したSQLクエリ: {sql_query}
            
            クエリの結果: {query_result}
            
            以下のガイドラインに従って回答を作成してください：
            1. 結果を明確に説明し、重要な数値や傾向を強調してください。
            2. マーケティングの観点から、結果の意味や示唆を提供してください。
            3. 必要に応じて、追加の分析や次のステップを提案してください。
            4. 専門用語は避け、わかりやすい言葉で説明してください。
            5. 回答は日本語で提供してください。
            
            回答:
            """
        )
        
        # Create response generation chain
        self.response_chain = LLMChain(
            llm=self.llm,
            prompt=self.response_prompt
        )
    
    def process_question(self, question):
        """
        Process user question and generate response.
        
        Args:
            question (str): User question
            
        Returns:
            dict: Response containing answer, SQL query, and any visualizations
        """
        # Generate SQL query
        sql_query = self.query_generator.generate_query(question)
        
        # Execute query
        query_result = self.query_generator.execute_query(sql_query)
        
        # Check if query execution resulted in an error
        if isinstance(query_result, str) and query_result.startswith("Error"):
            return {
                "answer": f"申し訳ありません。クエリの実行中にエラーが発生しました: {query_result}",
                "sql_query": sql_query,
                "visualization": None
            }
        
        # Generate visualization if appropriate
        visualization = self._generate_visualization(question, query_result)
        
        # Generate response
        response = self.response_chain.run(
            question=question,
            sql_query=sql_query,
            query_result=str(query_result)
        )
        
        return {
            "answer": response,
            "sql_query": sql_query,
            "visualization": visualization
        }
    
    def _generate_visualization(self, question, query_result):
        """
        Generate visualization based on query result if appropriate.
        
        Args:
            question (str): User question
            query_result: Query result
            
        Returns:
            str or None: Base64 encoded image if visualization is generated, None otherwise
        """
        # Convert query result to DataFrame if it's not already
        if not isinstance(query_result, pd.DataFrame):
            try:
                # Try to convert to DataFrame
                if isinstance(query_result, list) and len(query_result) > 0:
                    if isinstance(query_result[0], dict):
                        df = pd.DataFrame(query_result)
                    else:
                        # If it's a list of tuples or lists, we need column names
                        df = pd.DataFrame(query_result, columns=["Value"])
                else:
                    # Not suitable for visualization
                    return None
            except:
                # If conversion fails, return None
                return None
        else:
            df = query_result
        
        # Check if the result is suitable for visualization
        if len(df) <= 1 and len(df.columns) <= 1:
            # Single value, not suitable for visualization
            return None
        
        # Determine the type of visualization based on the question and data
        if "推移" in question or "トレンド" in question or "変化" in question:
            # Time series visualization
            return self._create_time_series_plot(df)
        elif "比較" in question or "割合" in question or "分布" in question:
            # Comparison visualization
            return self._create_comparison_plot(df)
        elif len(df) > 1 and len(df.columns) >= 2:
            # Default to bar chart for multiple values
            return self._create_bar_chart(df)
        
        return None
    
    def _create_time_series_plot(self, df):
        """Create a time series plot."""
        plt.figure(figsize=(10, 6))
        
        # Try to identify date column
        date_cols = [col for col in df.columns if any(kw in col.lower() for kw in ["date", "time", "月", "日", "年"])]
        
        if date_cols:
            date_col = date_cols[0]
            value_cols = [col for col in df.columns if col != date_col]
            
            for col in value_cols:
                plt.plot(df[date_col], df[col], marker='o', label=col)
            
            plt.xlabel(date_col)
            plt.ylabel("値")
            plt.title("時系列データ")
            plt.xticks(rotation=45)
            plt.legend()
            plt.tight_layout()
        else:
            # If no date column is found, use index as x-axis
            for col in df.columns:
                plt.plot(df.index, df[col], marker='o', label=col)
            
            plt.xlabel("インデックス")
            plt.ylabel("値")
            plt.title("時系列データ")
            plt.legend()
            plt.tight_layout()
        
        return self._fig_to_base64()
    
    def _create_comparison_plot(self, df):
        """Create a comparison plot (bar chart or pie chart)."""
        plt.figure(figsize=(10, 6))
        
        if len(df.columns) == 2:
            # If there are two columns, create a pie chart
            labels = df.iloc[:, 0]
            values = df.iloc[:, 1]
            
            plt.pie(values, labels=labels, autopct='%1.1f%%')
            plt.title("割合の比較")
            plt.axis('equal')
        else:
            # Otherwise, create a bar chart
            return self._create_bar_chart(df)
        
        return self._fig_to_base64()
    
    def _create_bar_chart(self, df):
        """Create a bar chart."""
        plt.figure(figsize=(10, 6))
        
        if len(df.columns) == 2:
            # If there are two columns, use first as labels and second as values
            labels = df.iloc[:, 0]
            values = df.iloc[:, 1]
            
            plt.bar(labels, values)
            plt.xlabel(df.columns[0])
            plt.ylabel(df.columns[1])
        else:
            # Otherwise, use index as labels and all columns as series
            df.plot(kind='bar', ax=plt.gca())
            plt.xlabel("カテゴリ")
            plt.ylabel("値")
        
        plt.title("データ比較")
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._fig_to_base64()
    
    def _fig_to_base64(self):
        """Convert matplotlib figure to base64 encoded string."""
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        return img_str
