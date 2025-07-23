import os
import re
import gradio as gr
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import SecretStr
import requests

# Load environment variables
load_dotenv()

# Load Azure OpenAI credentials
AZURE_API_KEY = os.getenv("AZURE_API_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_API_VERSION = os.getenv("AZURE_API_VERSION")
AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL")

# Validate env variables
if not all([AZURE_API_KEY, AZURE_ENDPOINT, AZURE_API_VERSION, AZURE_OPENAI_MODEL]):
    raise ValueError("Missing environment variables. Please check your .env file or environment settings.")

# Initialize Azure OpenAI LLM
llm = AzureChatOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_version=AZURE_API_VERSION,
    azure_deployment=AZURE_OPENAI_MODEL,
    api_key=SecretStr(AZURE_API_KEY) if AZURE_API_KEY else None,
    temperature=0.7,
)

# Conversation history
conversation_history = []


class CalculatorTool:
    """Simple calculator for +, -, *, / only."""

    def detect_arithmetic_intent(self, text):
        # Detect if the text is a simple arithmetic question
        pattern = r"^\s*([-+]?\d+(?:\.\d+)?)(?:\s*([+\-*/])\s*([-+]?\d+(?:\.\d+)?))\s*$"
        if re.search(pattern, text.strip()):
            return True
        # Also allow: What is 2 + 2? Calculate 3 * 4, etc.
        keywords = [
            "add",
            "plus",
            "minus",
            "subtract",
            "times",
            "multiplied",
            "divide",
            "divided",
            "+",
            "-",
            "*",
            "/",
        ]
        if any(k in text.lower() for k in keywords):
            return True
        return False

    def extract_expression(self, text):
        # Try to extract a simple arithmetic expression
        # Accepts: 2 + 2, What is 2 + 2?, Calculate 3 * 4, etc.
        expr = re.findall(r"([-+]?\d+(?:\.\d+)?|[+\-*/])", text)
        if not expr or len(expr) < 3:
            return None
        # Try to build a valid expression: number op number
        try:
            a = float(expr[0])
            op = expr[1]
            b = float(expr[2])
            if op not in "+-*/":
                return None
            return a, op, b
        except Exception:
            return None

    def calculate(self, a, op, b):
        try:
            if op == "+":
                return True, a + b
            elif op == "-":
                return True, a - b
            elif op == "*":
                return True, a * b
            elif op == "/":
                if b == 0:
                    return False, "Division by zero is not allowed."
                return True, a / b
            else:
                return False, "Unsupported operation."
        except Exception as e:
            return False, f"Calculation error: {str(e)}"

    def process(self, text):
        expr = self.extract_expression(text)
        if not expr:
            return (
                False,
                "Sorry, I could not understand the arithmetic expression. Please use the format: number operator number (e.g., 2 + 2).",
            )
        a, op, b = expr
        success, result = self.calculate(a, op, b)
        if success:
            return True, f"Result: {a} {op} {b} = {result}"
        else:
            return False, f"Error: {result}"


calculator = CalculatorTool()


def detect_intent(user_input):
    if calculator.detect_arithmetic_intent(user_input):
        return "calculator"
    elif "product" in user_input.lower():
        return "product_query"
    elif "outlet" in user_input.lower() or "store" in user_input.lower():
        return "outlet_query"
    else:
        return "general_conversation"


def plan_and_execute(user_input):
    global conversation_history
    intent = detect_intent(user_input)

    if intent == "calculator":
        print("Using calculator tool...")
        success, result = calculator.process(user_input)
        return f"Initializing Calculator Tool...\n\n{result}"
    elif intent == "product_query":
        print("Using product API...")
        try:
            response = requests.get("http://127.0.0.1:8000/api/products", params={"query": user_input})
            response.raise_for_status()
            return response.json()["summary"]
        except requests.exceptions.RequestException as e:
            return f"Sorry, the service is currently down. Please try again later. (Error: {e})"
    elif intent == "outlet_query":
        print("Using outlet API...")
        try:
            response = requests.get("http://127.0.0.1:8000/api/outlets", params={"query": user_input})
            response.raise_for_status()
            
            data = response.json().get("result", {})
            if data and data.get("success"):
                results = data.get("results")
                if results:
                    reply = "I found the following outlets:\n\n"
                    for outlet in results:
                        reply += f"**{outlet.get('name', 'N/A')}**\n"
                        reply += f"Address: {outlet.get('address', 'N/A')}\n"
                        reply += f"Hours: {outlet.get('hours', 'N/A')}\n"
                        reply += f"Services: {outlet.get('services', 'N/A')}\n\n"
                    return reply
                else:
                    return "I couldn't find any outlets matching your query."
            else:
                error_msg = data.get('error', 'An unknown error occurred.')
                return f"Sorry, I encountered an error while searching for outlets: {error_msg}"

        except requests.exceptions.RequestException:
            return "Sorry, I can't connect to the service right now. Please try again in a bit."

    # Step 1: Plan (for non-calculation requests)
    planning_prompt = f"""
You are a helpful AI agent. When the user gives a message, plan the steps required to respond clearly.
User Message: "{user_input}"
What is your plan?
Respond in this format:
PLAN: <brief plan>
THINK: <your reasoning>
ACTION: <what to do now>
    """
    plan_response = llm.invoke([HumanMessage(content=planning_prompt)])
    plan_text = plan_response.content
    # Step 2: Act (simplified controller – just continues the conversation)
    action_prompt = f"""
You have planned the following:
{plan_text}

Now execute the response for the user based on your plan.
User: {user_input}
Assistant:"""
    final_response = llm.invoke([HumanMessage(content=action_prompt)])
    return final_response.content


def respond(message, history):
    try:
        ai_reply = plan_and_execute(message)
        conversation_history.append(HumanMessage(content=message))
        conversation_history.append(AIMessage(content=ai_reply))
        return ai_reply
    except Exception as e:
        return f"Error: {str(e)}"


def clear_memory():
    global conversation_history
    conversation_history = []
    return []


def handle_message(message, history):
    if not message.strip():
        return history, ""
    reply = respond(message, history)
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})
    return history, ""


def handle_clear():
    clear_memory()
    return [], ""


with gr.Blocks(title="ZUS Assistant") as demo:
    gr.Markdown("ZUS Assistant")
    chatbot = gr.Chatbot(height=400, type="messages")
    msg = gr.Textbox(placeholder="Type your message here...", label="Message")
    with gr.Row():
        submit_btn = gr.Button("Send", variant="primary")
        clear_btn = gr.Button("Clear History")
    msg.submit(handle_message, [msg, chatbot], [chatbot, msg])
    submit_btn.click(handle_message, [msg, chatbot], [chatbot, msg])
    clear_btn.click(handle_clear, [], [chatbot, msg])

if __name__ == "__main__":
    demo.launch(share=True) 