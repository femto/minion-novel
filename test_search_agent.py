from google_search_agent.agent import root_agent

def main():
    print("Google Search Agent Test")
    print("========================")
    
    # Test some search queries
    test_prompts = [
        "What is the capital of France?",
        "Who won the last FIFA World Cup?",
        "What are the latest developments in AI?",
        "What is the weather like in Tokyo today?",
        "Tell me about the history of the internet."
    ]
    
    for prompt in test_prompts:
        print(f"\nUser: {prompt}")
        response = root_agent.run(prompt)
        print(f"Agent: {response}")

if __name__ == "__main__":
    main()
