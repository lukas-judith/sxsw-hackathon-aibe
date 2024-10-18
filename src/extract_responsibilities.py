import os
from dotenv import load_dotenv

load_dotenv()

from typing import List, Optional, Tuple

from pydantic import BaseModel
from groq import Groq
import dspy
import json

from src.data_models import ExtractResponsibilitiesOutput

# client = Groq(
#     api_key=os.environ.get("GROQ_API_KEY"),
# )

# chat_completion = client.chat.completions.create(
#     messages=[
#         {
#             "role": "user",
#             "content": "Explain the importance of fast language models",
#         }
#     ],
#     model="llama3-8b-8192",
# )

# # import pdb

# # pdb.set_trace()

# print(chat_completion.choices[0].message.content)


# import dspy


lm = dspy.LM("groq/llama3-8b-8192")

dspy.configure(lm=lm)


example_job_description = """
We are looking for a software engineer to join our team. The ideal candidate will have experience with Python, Django, and React. Responsibilities include developing new features, fixing bugs, and writing tests.
"""


class ExtractResponsibilities(dspy.Signature):
    """
    From a text document, which may be a job description or any other note written
    by the manager or company, extract the responsibilities of the role in a structured format.
    """

    input_text: str = dspy.InputField(
        desc="The text document from which to extract the responsibilities."
    )
    output_responsibilities: ExtractResponsibilitiesOutput = dspy.OutputField(
        desc=f"The extracted responsibilities of the role, fitting the schema {json.dumps(ExtractResponsibilitiesOutput.schema(), indent=2)}",
    )


resp_extractor = dspy.ChainOfThought(
    ExtractResponsibilities,
)


def extract_responsibilities(
    input_text: str,
) -> Tuple[ExtractResponsibilitiesOutput, str]:

    output = resp_extractor(input_text=input_text)
    output_responsibilities = output.output_responsibilities
    reasoning = output.reasoning

    return output_responsibilities, reasoning
