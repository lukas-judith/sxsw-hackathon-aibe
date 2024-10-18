"""
Main script running the fastapi server exposing the AI backend logic.
"""

import os
import fastapi
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pyngrok import ngrok


from dotenv import load_dotenv

load_dotenv()


from extract_responsibilities import (
    extract_responsibilities,
    check_responsibilities,
)
from data_models import (
    ExtractResponsibilitiesRequest,
    ExtractResponsibilitiesResponse,
    CheckResponsibilitiesRequest,
    CheckResponsibilitiesResponse,
)


NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")
PORT = 8000

# # set up ngrok for local development
# ngrok.set_auth_token(NGROK_AUTH_TOKEN)

# # open a HTTP tunnel on the default port 80
# # <NgrokTunnel: "https://<public_sub>.ngrok.io" -> "http://localhost:PORT">
# http_tunnel = ngrok.connect(
#     addr="http://localhost:8000",
#     proto="http",
#     name="http_tunnel",
#     hostname="myapp.ngrok.io.ngrok-free.dev",
# )

# print(f"Public URL: {http_tunnel.public_url}")

# # # Open a named tunnel from the config file
# # named_tunnel = ngrok.connect(
# #     name="my_tunnel_name",
# # )


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


@app.post("/extract_responsibilities_plaintext")
def extract_responsibilities_handler(
    extract_responsibilities_request: ExtractResponsibilitiesRequest,
):
    output, reasoning = extract_responsibilities(extract_responsibilities_request.text)

    return ExtractResponsibilitiesResponse(
        responsibilities=output.responsibilities, reasoning=reasoning
    )


@app.post("/extract_responsibilities")
async def extract_responsibilities_handler(file: UploadFile = File(...)):
    try:
        # Read the file contents
        file_content = await file.read()  # Reads the file as binary data (bytes)
        text_data = file_content.decode("utf-8")  # Decode the bytes to a string (UTF-8)

        # Call the extract_responsibilities function with the decoded text
        output, reasoning = extract_responsibilities(text_data)

        # Return the result in JSON format
        return ExtractResponsibilitiesResponse(
            responsibilities=output.responsibilities, reasoning=reasoning
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/check_responsibilities")
async def check_responsibilities_handler(
    check_responsibility_request: CheckResponsibilitiesRequest,
):
    responsibilities_fulfilled, reasoning = check_responsibilities(
        check_responsibility_request.all_responsibilities,
        check_responsibility_request.transcript,
    )

    return CheckResponsibilitiesResponse(
        responsibilities_fulfilled=responsibilities_fulfilled,
        reasoning=reasoning,
    )


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Run the FastAPI server.")

    parser.add_argument(
        "--port",
        type=int,
        default=PORT,
        help="The port to run the FastAPI server on.",
    )

    args = parser.parse_args()

    uvicorn.run(app, host="0.0.0.0", port=args.port)
