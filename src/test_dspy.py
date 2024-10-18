import dspy

# lm = dspy.LM("openai/gpt-4o-mini")

lm = dspy.LM("groq/llama3-8b-8192")

dspy.configure(lm=lm)

print(lm("hello! who am I speaking to?"))
