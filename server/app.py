# import streamlit as st
# import json
# import os
# import fitz  # PyMuPDF
# from openai import OpenAI
# from dotenv import load_dotenv
# from engine.core import DebtNegotiationEnv
# from engine.models import Action

# # Load environment variables from .env file
# load_dotenv()

# # Initialize OpenAI Client
# # Use HF_TOKEN or OPENAI_API_KEY depending on your environment
# api_key = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
# client = OpenAI(api_key=api_key)

# # Load Legal Knowledge Base for RAG
# try:
#     with open("knowledge_base.json", "r") as f:
#         LEGAL_KB = json.load(f)
# except FileNotFoundError:
#     LEGAL_KB = {"Error": "Knowledge base file not found."}

# # Page Configuration
# st.set_page_config(page_title="DebtShield AI", page_icon="🛡️", layout="wide")

# st.title("🛡️ DebtShield AI")
# st.markdown("### Professional Debt Restructuring & Negotiation Framework")

# # --- SIDEBAR ---
# with st.sidebar:
#     st.header("System Status")
#     if api_key:
#         st.success("API Key Loaded")
#     else:
#         st.error("API Key Missing! Please check your .env file.")
    
#     st.divider()
#     st.markdown("**Framework:** OpenEnv v1.0\n\n**Engine:** Multi-Agent Adversarial")

# # --- STEP 1: DATA EXTRACTION (OCR) ---
# st.header("1. Upload Statement")
# uploaded_file = st.file_uploader("Upload your credit card statement (PDF)", type="pdf")

# if uploaded_file:
#     with st.spinner("Analyzing document with AI..."):
#         try:
#             # Extract text from PDF using PyMuPDF
#             doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
#             text = " ".join([page.get_text() for page in doc])
            
#             # IMPROVED EXTRACTION PROMPT to prevent KeyErrors
#             analysis_prompt = (
#                 f"Extract the following financial details from this text. "
#                 f"If a value is not found, set it to 0.0. "
#                 f"Return ONLY a JSON object with these exact keys: "
#                 f"{{'apr': float, 'bal': float, 'fee': float, 'min': float}}\n\n"
#                 f"TEXT: {text}"
#             )
            
#             res = client.chat.completions.create(
#                 model="gpt-4o", 
#                 messages=[
#                     {"role": "system", "content": "You are a precise financial data extractor. Output only valid JSON."},
#                     {"role": "user", "content": analysis_prompt}
#                 ], 
#                 response_format={"type": "json_object"}
#             )
#             data = json.loads(res.choices[0].message.content)
#             st.success("Data Extracted Successfully!")
            
#         except Exception as e:
#             st.error(f"OCR Error: {e}")
#             data = {}

#     # --- SAFE INPUTS (Human-in-the-Loop) ---
#     # We use .get() with a default of 0.0 to prevent the KeyError: 'apr' crash
#     if data:
#         st.markdown("#### Verify Extracted Data")
#         col1, col2, col3, col4 = st.columns(4)
        
#         with col1:
#             apr = st.number_input("APR %", value=float(data.get('apr', 0.0)))
#         with col2:
#             bal = st.number_input("Balance ($)", value=float(data.get('bal', 0.0)))
#         with col3:
#             fee = st.number_input("Late Fees ($)", value=float(data.get('fee', 0.0)))
#         with col4:
#             min_pay = st.number_input("Min Payment ($)", value=float(data.get('min', 0.0)))
        
#         # Initialize the RL Environment with verified user data
#         # We add floor_apr and floor_fee for the internal adversarial logic
#         user_data = {
#             "apr": apr, 
#             "bal": bal, 
#             "fee": fee, 
#             "min": min_pay, 
#             "floor_apr": 10.0, 
#             "floor_fee": 0.0
#         }
#         env = DebtNegotiationEnv(initial_data=user_data)

#         # --- STEP 2: STRATEGY GENERATION ---
#         st.divider()
#         st.header("2. Negotiation Strategy")
        
#         if st.button("Generate Optimal Strategy"):
#             with st.spinner("Consulting Legal KB & Simulating Outcomes..."):
#                 obs = env.reset()
                
#                 # Strategy Prompt incorporating the Knowledge Base (RAG)
#                 prompt = (
#                     f"Current State: {obs.model_dump_json()}\n"
#                     f"Legal Knowledge Base: {json.dumps(LEGAL_KB)}\n"
#                     f"Goal: Lower APR and fees while maintaining a professional relationship.\n"
#                     f"Respond in JSON: {{'thought_process': 'Explain your strategy', 'tactic': 'pick from [appeal_history, cite_hardship, competing_offer, polite_request, firm_demand]', 'requested_apr': float, 'requested_fee': float, 'message': 'Your message to the bank'}}"
#                 )
                
#                 res = client.chat.completions.create(
#                     model="gpt-4o", 
#                     messages=[
#                         {"role": "system", "content": "You are a Senior Debt Negotiator. Use the provided legal KB to strengthen your arguments."}, 
#                         {"role": "user", "content": prompt}
#                     ], 
#                     response_format={"type": "json_object"}
#                 )
#                 st.session_state['action'] = json.loads(res.choices[0].message.content)

#         # --- STEP 3: REVIEW AND EXECUTE ---
#         if 'action' in st.session_state:
#             act = st.session_state['action']
            
#             with st.expander("🧠 AI Internal Reasoning", expanded=True):
#                 st.write(act.get('thought_process', 'No reasoning provided.'))
            
#             st.info(f"**Selected Tactic:** {act.get('tactic', 'Unknown').upper()}")
            
#             # Editable message box
#             final_message = st.text_area("Proposed Message to Creditor:", value=act.get('message', ''), height=200)
            
#             if st.button("🚀 Approve & Send Message"):
#                 with st.spinner("Executing negotiation..."):
#                     # Update the action with the edited message from the user
#                     act['message'] = final_message
                    
#                     # Pass the action to the RL engine for validation
#                     try:
#                         action_obj = Action(**act)
#                         obs, reward, done, _ = env.step(action_obj)
                        
#                         st.success(f"Message Sent! \n\n**Creditor Response:** {reward.details}")
#                         st.metric("Reward Score", f"{reward.score:.2f}")
#                         st.write(f"**Updated State:** APR: {obs.current_apr}% | Fees: ${obs.current_fee}")
#                     except Exception as e:
#                         st.error(f"Execution Error: {e}")
#     else:
#         st.warning("Please upload a valid PDF statement to begin.")

import streamlit as st
import json
import os
import fitz  # PyMuPDF
from openai import OpenAI
from dotenv import load_dotenv
from engine.core import DebtNegotiationEnv
from engine.models import Action

load_dotenv()
client = OpenAI(api_key=os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY"))

with open("knowledge_base.json", "r") as f:
    LEGAL_KB = json.load(f)

def main():
    """
    Main entry point for the Streamlit application.
    This function is required by the OpenEnv validator.
    """
    st.set_page_config(page_title="DebtShield AI", page_icon="🛡️", layout="wide")
    st.title("🛡️ DebtShield AI")
    st.markdown("### Professional Debt Restructuring & Negotiation Framework")

    uploaded_file = st.file_uploader("Upload Statement (PDF)", type="pdf")

    if uploaded_file:
        with st.spinner("Analyzing document..."):
            try:
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                text = " ".join([page.get_text() for page in doc])
                analysis_prompt = (
                    f"Extract JSON from: {text}. {{'apr': float, 'bal': float, 'fee': float, 'min': float}}"
                )
                res = client.chat.completions.create(
                    model="gpt-4o", 
                    messages=[{"role": "user", "content": analysis_prompt}], 
                    response_format={"type": "json_object"}
                )
                data = json.loads(res.choices[0].message.content)
                st.success("Data Extracted!")
            except Exception as e:
                st.error(f"OCR Error: {e}")
                data = {}

        if data:
            col1, col2, col3, col4 = st.columns(4)
            apr = col1.number_input("APR %", value=float(data.get('apr', 0.0)))
            bal = col2.number_input("Balance ($)", value=float(data.get('bal', 0.0)))
            fee = col3.number_input("Late Fees ($)", value=float(data.get('fee', 0.0)))
            min_pay = col4.number_input("Min Payment ($)", value=float(data.get('min', 0.0)))
            
            env = DebtNegotiationEnv(initial_data={"apr": apr, "bal": bal, "fee": fee, "min": min_pay, "floor_apr": 10.0, "floor_fee": 0.0})

            if st.button("Generate Optimal Strategy"):
                obs = env.reset()
                prompt = f"State: {obs.model_dump_json()}. KB: {json.dumps(LEGAL_KB)}. JSON: {{'thought_process': '...', 'tactic': '...', 'requested_apr': float, 'requested_fee': float, 'message': '...'}}"
                res = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"})
                st.session_state['action'] = json.loads(res.choices[0].message.content)

            if 'action' in st.session_state:
                act = st.session_state['action']
                with st.expander("🧠 AI Internal Reasoning"):
                    st.write(act.get('thought_process', ''))
                st.info(f"Tactic: {act.get('tactic', '')}")
                final_msg = st.text_area("Message:", value=act.get('message', ''))
                if st.button("🚀 Approve & Send"):
                    act['message'] = final_msg
                    obs, reward, done, _ = env.step(Action(**act))
                    st.success(f"Result: {reward.details}")

# THIS BLOCK IS MANDATORY FOR THE VALIDATOR
if __name__ == "__main__":
    main()