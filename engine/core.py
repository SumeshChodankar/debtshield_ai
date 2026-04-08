# import json
# import os
# from openai import OpenAI
# from .models import Observation, Action, Reward, Tactic
# from dotenv import load_dotenv

# # Load .env BEFORE anything else
# load_dotenv()

# from openai import OpenAI

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# # Use mandated environment variables
# client = OpenAI(
#     api_key=os.getenv("HF_TOKEN"), 
#     base_url=os.getenv("API_BASE_URL")
# )
# MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")

# class DebtNegotiationEnv:
#     def __init__(self, task_level="easy", initial_data=None):
#         self.task_level = task_level
#         self.reset(initial_data)

#     def reset(self, initial_data=None):
#         if initial_data:
#             self.state = initial_data
#         else:
#             if self.task_level == "easy":
#                 self.state = {"apr": 24.0, "fee": 35.0, "bal": 1000.0, "min": 50.0, "floor_apr": 24.0, "floor_fee": 0.0}
#             elif self.task_level == "medium":
#                 self.state = {"apr": 28.0, "fee": 0.0, "bal": 5000.0, "min": 150.0, "floor_apr": 18.0, "floor_fee": 0.0}
#             else:
#                 self.state = {"apr": 29.0, "fee": 100.0, "bal": 12000.0, "min": 300.0, "floor_apr": 12.0, "floor_fee": 0.0}
#         self.turn = 0
#         self.mood = "Stubborn"
#         return self.state_to_obs()

#     def state(self):
#         return self.state_to_obs()

#     def state_to_obs(self):
#         return Observation(
#             turn=self.turn,
#             current_apr=self.state["apr"],
#             current_fee=self.state["fee"],
#             balance=self.state["bal"],
#             monthly_min=self.state["min"],
#             creditor_mood=self.mood,
#             last_creditor_message="Waiting for proposal..."
#         )

#     def _get_bank_response(self, action: Action):
#         bank_prompt = (
#             f"You are a Bank Manager. Current APR: {self.state['apr']}%. Floor: {self.state['floor_apr']}%. "
#             f"User: {action.message}. Requested APR: {action.requested_apr}%. "
#             f"Reply ONLY JSON: {{'accepted': bool, 'response': 'text', 'new_apr': float, 'new_fee': float}}"
#         )
#         res = client.chat.completions.create(
#             model=MODEL_NAME,
#             messages=[{"role": "system", "content": bank_prompt}],
#             response_format={ "type": "json_object" }
#         )
#         return json.loads(res.choices[0].message.content)

#     def step(self, action: Action):
#         self.turn += 1
#         bank_decision = self._get_bank_response(action)
        
#         reward_val = 0.0
#         if bank_decision['accepted']:
#             self.state["apr"] = bank_decision.get('new_apr', self.state["apr"])
#             self.state["fee"] = bank_decision.get('new_fee', self.state["fee"])
#             reward_val = 0.5
#             msg = bank_decision['response']
#         else:
#             reward_val = -0.1
#             msg = bank_decision['response']

#         done = (self.turn >= 5) or (self.state["apr"] <= self.state["floor_apr"])
#         return self.state_to_obs(), Reward(score=reward_val, details=msg), done, {}




import json
import os
import asyncio
from openai import OpenAI
from .models import Observation, Action, Reward, Tactic
from dotenv import load_dotenv

# Load .env BEFORE anything else
load_dotenv()
# Use mandated environment variables
client = OpenAI(
    api_key=os.getenv("HF_TOKEN"), 
    base_url=os.getenv("API_BASE_URL")
)
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")

class DebtNegotiationEnv:
    def __init__(self, task_level="easy", initial_data=None):
        self.task_level = task_level
        self.initial_data = initial_data # Store for reset
        # REMOVED self.reset() from here to fix RuntimeWarning

    async def reset(self, initial_data=None): 
        # Use provided data or the one passed during __init__
        data = initial_data or self.initial_data
        
        if data:
            self.state = data
        else:
            if self.task_level == "easy":
                self.state = {"apr": 24.0, "fee": 35.0, "bal": 1000.0, "min": 50.0, "floor_apr": 24.0, "floor_fee": 0.0}
            elif self.task_level == "medium":
                self.state = {"apr": 28.0, "fee": 0.0, "bal": 5000.0, "min": 150.0, "floor_apr": 18.0, "floor_fee": 0.0}
            else:
                self.state = {"apr": 29.0, "fee": 100.0, "bal": 12000.0, "min": 300.0, "floor_apr": 12.0, "floor_fee": 0.0}
        
        self.turn = 0
        self.mood = "Stubborn"
        return self.state_to_obs()

    def state(self):
        return self.state_to_obs()

    def state_to_obs(self):
        return Observation(
            turn=self.turn,
            current_apr=self.state["apr"],
            current_fee=self.state["fee"],
            balance=self.state["bal"],
            monthly_min=self.state["min"],
            creditor_mood=self.mood,
            last_creditor_message="Waiting for proposal..."
        )

    async def _get_bank_response(self, action: Action):
        bank_prompt = (
            f"You are a Bank Manager. Current APR: {self.state['apr']}%. Floor: {self.state['floor_apr']}%. "
            f"User: {action.message}. Requested APR: {action.requested_apr}%. "
            f"Reply ONLY JSON: {{'accepted': bool, 'response': 'text', 'new_apr': float, 'new_fee': float}}"
        )
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": bank_prompt}],
            response_format={ "type": "json_object" }
        )
        return json.loads(res.choices[0].message.content)

    async def step(self, action: Action):
        self.turn += 1
        bank_decision = await self._get_bank_response(action)
        
        reward_val = 0.0
        if bank_decision['accepted']:
            self.state["apr"] = bank_decision.get('new_apr', self.state["apr"])
            self.state["fee"] = bank_decision.get('new_fee', self.state["fee"])
            reward_val = 0.5
            msg = bank_decision['response']
        else:
            reward_val = -0.1
            msg = bank_decision['response']

        done = (self.turn >= 5) or (self.state["apr"] <= self.state["floor_apr"])
        return self.state_to_obs(), Reward(score=reward_val, details=msg), done, {}

    async def close(self):
        pass