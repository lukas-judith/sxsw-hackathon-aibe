"""
Main script running the fastapi server exposing the AI backend logic.
"""

import os
import fastapi
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from pyngrok import ngrok


from dotenv import load_dotenv

load_dotenv()


from src.extract_responsibilities import extract_responsibilities
from src.data_models import (
    ExtractResponsibilitiesRequest,
    ExtractResponsibilitiesResponse,
)


NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")
PORT = 8000

# set up ngrok for local development
ngrok.set_auth_token(NGROK_AUTH_TOKEN)

# open a HTTP tunnel on the default port 80
# <NgrokTunnel: "https://<public_sub>.ngrok.io" -> "http://localhost:PORT">
http_tunnel = ngrok.connect(
    addr="http://localhost:8000", proto="http", name="http_tunnel"
)

print(f"Public URL: {http_tunnel.public_url}")

# Open a named tunnel from the config file
named_tunnel = ngrok.connect(name="my_tunnel_name")

app = fastapi.FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/extract_responsibilities")
def extract_responsibilities_handler(
    extract_responsibilities_request: ExtractResponsibilitiesRequest,
):
    output, reasoning = extract_responsibilities(extract_responsibilities_request.text)

    return ExtractResponsibilitiesResponse(
        responsibilities=output.responsibilities, reasoning=reasoning
    )


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=PORT)
