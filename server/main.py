# from fastapi import FastAPI
# from engine.core import DebtNegotiationEnv
# import uvicorn

# app = FastAPI()
# env = DebtNegotiationEnv(task_level="easy")

# # CHANGE THIS FROM .get TO .post
# @app.post("/reset") 
# def reset():
#     obs = env.reset()
#     return {"observation": obs.model_dump(), "status": "success"}

# @app.get("/state")
# def state():
#     return {"observation": env.state().model_dump()}

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=7860)

import sys
import os
from pathlib import Path
from fastapi import FastAPI
import uvicorn

# Add the project root to the python path so server/main.py can find engine/
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from engine.core import DebtNegotiationEnv

app = FastAPI()
env = DebtNegotiationEnv(task_level="easy")

@app.post("/reset") 
async def reset(): 
    try:
        obs = await env.reset() 
        return {"observation": obs.model_dump(), "status": "success"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}, 500

@app.get("/state")
async def state(): 
    try:
        obs = env.state() 
        return {"observation": obs.model_dump(), "status": "success"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}, 500

# THIS IS THE FUNCTION THE VALIDATOR IS LOOKING FOR
def main():
    """Entry point to start the server."""
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()