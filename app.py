"""
Chainlit application for credit card user database chatbot.
"""

import os
import chainlit as cl
from src.chatbot import CreditCardChatbot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize chatbot
chatbot = CreditCardChatbot()

@cl.on_chat_start
async def on_chat_start():
    """
    Initialize the chat session.
    """
    # Send welcome message
    welcome = """\
    こんにちは！クレジットカードユーザー分析チャットボットへようこそ。以下のような質問をどうぞ。
    ・ここ半年間の購入額の合計を参考にしてユーザを高額利用者、中額利用者、少額利用者の３カテゴリにわけてそれぞれのカテゴリの人数を出してほしい。退会済みユーザは除外すること。
    ・ここ3ヶ月間で美容カテゴリで1000円以上の購入履歴が一度でもある人数を出してほしい。退会済みユーザは除外すること。
    ・ペットカテゴリユーザを、アクティブと休眠とでそれぞれ人数出して欲しい。退会済みユーザは当然除外すること。
    ・ここ半年間の解約者数の推移を数値で教えて
    ・ここ半年間のアクティブ者数の推移を数値で教えて
    ・ここ半年間のアクティブ者の月別平均購入額の推移を数値で教えて
    """
    await cl.Message(
        content=welcome,
    ).send()

@cl.on_message
async def on_message(message: cl.Message):
    """
    Process user message and generate response.

    Args:
        message: User message
    """
    # Show thinking message
    await cl.Message(content="考え中...").send()

    # Process the question
    response = chatbot.process_question(message.content)

    # Create response message
    msg = cl.Message(content=response["answer"])

    # Add SQL query as formatted text in the message content
    if response["sql_query"]:
        # Format the SQL query as a code block in the message content
        sql_block = f"\n\n```sql\n{response['sql_query']}\n```"
        msg.content += sql_block

    # Add visualization if available
    if response["visualization"]:
        msg.elements.append(
            cl.Image(
                name="Data Visualization",
                content=response["visualization"],
                display="inline"
            )
        )

    # Send the message
    await msg.send()

if __name__ == "__main__":
    # This is used when running locally with `python app.py`
    from chainlit.cli import run_chainlit
    import sys
    # Use port 8001 instead of the default 8000
    sys.argv = ["chainlit", "run", "app.py", "--port", "8001"]
    run_chainlit("app.py")
