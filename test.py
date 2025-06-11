from dotenv import load_dotenv
load_dotenv()

from google import genai

client = genai.Client()

print("List of models that support generateContent:\n")
for m in client.models.list():
    for action in m.supported_actions:
        if action == "generateContent":
            print(m.name)

print("List of models that support embedContent:\n")
for m in client.models.list():
    for action in m.supported_actions:
        if action == "embedContent":
            print(m.name)

print("\nList of models that support bidiGenerateContent:\n")
for m in client.models.list():
    for action in m.supported_actions:
        if action == "bidiGenerateContent":
            print(m.name)