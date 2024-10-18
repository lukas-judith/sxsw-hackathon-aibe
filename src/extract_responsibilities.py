import os
from concurrent.futures import ThreadPoolExecutor

from typing import List, Optional, Tuple, Dict

from pydantic import BaseModel
from groq import Groq
import dspy
import json


from src.data_models import (
    ExtractResponsibilitiesOutput,
    Responsibility,
    ResponsibilitiesFullfilledStatus,
)


from dotenv import load_dotenv

load_dotenv()

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
        desc=f"The extracted responsibilities of the role, fitting the schema {json.dumps(ExtractResponsibilitiesOutput.schema(), indent=2)} (you do not need to fill in the ids).",
    )


class CheckResponsibilities(dspy.Signature):
    """
    You are presented with the transcript of an interaction bewteen employee and manager,
    and with a list of all the responsibilities of the employee.
    Decide which of the responsibilities the employee is fulfilling, and which they are not.
    You must evaluate every responsibility and decide on whether it is fulfilled or not (or if status is null because it is not applicable).
    """

    input_transcript: str = dspy.InputField(
        desc="The transcript of the interaction between employee and manager."
    )
    all_responsibilities: List[Responsibility] = dspy.InputField(
        desc="All the responsibilities of the employee."
    )
    responsibilities_fulfilled: List[ResponsibilitiesFullfilledStatus] = (
        dspy.OutputField(
            desc=f"A list of status dictionaries including the id of the responsibility, whether it is fulfilled, and a comment explaining the reasoning, in this format: {json.dumps(ResponsibilitiesFullfilledStatus.schema(), indent=2)}.",
        )
    )


resp_extractor = dspy.ChainOfThought(
    ExtractResponsibilities,
)

resp_checker = dspy.ChainOfThought(
    CheckResponsibilities,
)


def extract_responsibilities(
    input_text: str,
) -> Tuple[ExtractResponsibilitiesOutput, str]:

    output = resp_extractor(input_text=input_text)
    output_responsibilities = output.output_responsibilities
    reasoning = output.reasoning

    return output_responsibilities, reasoning


def check_responsibilities(
    responsibilities: List[
        "Responsibility"
    ],  # Replace with your Responsibility class/type
    transcript: str,
) -> List[Tuple[ResponsibilitiesFullfilledStatus, str]]:

    output = resp_checker(
        input_transcript=transcript, all_responsibilities=responsibilities
    )

    return output.responsibilities_fulfilled, output.reasoning


if __name__ == "__main__":
    output, reasoning = extract_responsibilities(example_job_description)

    print(output)
    print(reasoning)
    # print(check_responsibilities(output.responsibilities, "The employee did a great job!"))

    example = {
        "transcript": "the product manager did build good roadmaps and managed technology projects, but they did not engage with the cross-functional teams well",
        "all_responsibilities": [
            {
                "id": "82babcf9-0562-4568-acf8-3d78b8cd98ea",
                "name": "Work with cross-functional teams",
                "description": "Product Managers work with cross-functional teams of engineers, designers, data scientists and researchers to build products.",
            },
            {
                "id": "26ae187a-48ff-4989-b83b-2c00b1dc7382",
                "name": "Identify significant opportunities and drive product vision, strategies, and roadmaps",
                "description": "It is the primary driver for identifying significant opportunities and driving product vision, strategies, and roadmaps for the company (B2B SaaS).",
            },
            {
                "id": "dda57472-f690-43d6-8eb3-603006d34aaf",
                "name": "Inform product strategies and roadmaps with data, research, and market analysis",
                "description": "Incorporate data, research, and market analysis to inform product strategies and roadmaps.",
            },
            {
                "id": "592176ec-4d18-4777-8b2f-4740073d7827",
                "name": "Plan, initiate, and manage technology projects",
                "description": "Plan, initiate, and manage technology projects for web-based products in our AI-driven platform.",
            },
        ],
    }
    from src.data_models import CheckResponsibilitiesRequest

    example_request = CheckResponsibilitiesRequest(
        transcript=example["transcript"],
        all_responsibilities=[
            Responsibility(**resp) for resp in example["all_responsibilities"]
        ],
    )

    checks, reasoning = check_responsibilities(
        example_request.all_responsibilities, example_request.transcript
    )

    import pdb

    pdb.set_trace()

    for responsibility, (fulfilled, reasoning) in zip(output.responsibilities, checks):
        print(f"Responsibility: {responsibility.name}")
        print(f"Fulfilled: {fulfilled}")
        print(f"Reasoning: {reasoning}")
        print()
