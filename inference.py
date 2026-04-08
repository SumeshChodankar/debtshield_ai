# import os
# import json
# from openai import OpenAI
# from engine.core import DebtNegotiationEnv
# from engine.models import Action
# from engine.tasks import DebtGrader

# client = OpenAI(
#     api_key=os.getenv("HF_TOKEN"), 
#     base_url=os.getenv("API_BASE_URL")
# )
# MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")

# def run_task(lvl):
#     env = DebtNegotiationEnv(task_level=lvl)
#     obs = env.reset()
#     initial_obs = obs
#     done = False
#     total_reward = 0
    
#     # STRICT [START] LOG
#     print(f"[START] task_id={lvl} observation={obs.model_dump_json()}")

#     while not done:
#         prompt = f"State: {obs.model_dump_json()}. Tactic list: [appeal_history, cite_hardship, competing_offer, polite_request, firm_demand]. JSON return: {{'thought_process': '...', 'tactic': '...', 'requested_apr': float, 'requested_fee': float, 'message': '...'}}"
        
#         res = client.chat.completions.create(
#             model=MODEL_NAME,
#             messages=[{"role": "user", "content": prompt}],
#             response_format={ "type": "json_object" }
#         )
        
#         action_data = json.loads(res.choices[0].message.content)
#         action = Action(**action_data)
        
#         obs, reward, done, _ = env.step(action)
#         total_reward += reward.score
        
#         # STRICT [STEP] LOG
#         print(f"[STEP] action={action.model_dump_json()} reward={reward.score} observation={obs.model_dump_json()} done={done}")

#     # Final Grading
#     if lvl == "easy": score = DebtGrader.grade_easy(obs, initial_obs)
#     elif lvl == "medium": score = DebtGrader.grade_medium(obs, initial_obs)
#     else: score = DebtGrader.grade_hard(obs, initial_obs)
    
#     # STRICT [END] LOG
#     print(f"[END] task_id={lvl} total_reward={total_reward} final_score={score}")

# if __name__ == "__main__":
#     for lvl in ["easy", "medium", "hard"]:
#         run_task(lvl)


import asyncio
import os
import json
import textwrap
from typing import List, Optional
from openai import OpenAI

from engine.core import DebtNegotiationEnv
from engine.models import Action

# MANDATORY VARIABLES
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL") or "https://api.openai.com/v1"
MODEL_NAME = os.getenv("MODEL_NAME") or "gpt-4o"
TASK_NAME = os.getenv("DEBT_TASK", "medium") 
BENCHMARK = "debt_negotiator"
MAX_STEPS = 5
TEMPERATURE = 0.7
SUCCESS_SCORE_THRESHOLD = 0.1 

SYSTEM_PROMPT = textwrap.dedent(
    """
    You are a professional debt negotiation agent. Your goal is to lower APR and fees.
    You must respond with a JSON object containing:
    - thought_process: your strategic reasoning
    - tactic: one of [appeal_history, cite_hardship, competing_offer, polite_request, firm_demand]
    - requested_apr: float
    - requested_fee: float
    - message: the actual text sent to the creditor
    """
).strip()

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

def get_model_action(client: OpenAI, obs_json: str) -> Action:
    user_prompt = f"Current State: {obs_json}\nProvide the next negotiation action in JSON."
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            response_format={"type": "json_object"},
            stream=False,
        )
        return Action(**json.loads(completion.choices[0].message.content))
    except Exception as exc:
        # IMPORTANT: This will now tell you EXACTLY why the API is failing
        print(f"[DEBUG] API Error: {exc}", flush=True) 
        return Action(thought_process=f"Error: {str(exc)}", tactic="polite_request", message="I request a review.", requested_apr=15.0, requested_fee=0.0)

async def main() -> None:
    if not API_KEY:
        print("[DEBUG] ERROR: HF_TOKEN or API_KEY not found in environment variables!")
        return

    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = DebtNegotiationEnv(task_level=TASK_NAME)

    rewards: List[float] = []
    steps_taken = 0
    success = False

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)

    try:
        obs = await env.reset()
        
        for step in range(1, MAX_STEPS + 1):
            action = get_model_action(client, obs.model_dump_json())
            obs, reward_obj, done, info = await env.step(action)
            
            reward = reward_obj.score
            rewards.append(reward)
            steps_taken = step
            
            log_step(step=step, action=action.model_dump_json(), reward=reward, done=done, error=None)

            if done:
                break

        total_reward = sum(rewards)
        score = min(max(total_reward / 2.5, 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD

    except Exception as e:
        print(f"[DEBUG] Runtime error: {e}", flush=True)
    finally:
        await env.close()
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

if __name__ == "__main__":
    asyncio.run(main())