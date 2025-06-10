from simple_adk_agent.agent import root_agent

def main():
    print("Calculator Agent Test")
    print("=====================")
    
    # Test some calculations
    test_prompts = [
        "What is 5 plus 3?",
        "Can you multiply 7 and 6?",
        "Divide 10 by 2 please",
        "What is 15 minus 7?",
        "If I have 100 and divide it by 0, what happens?"
    ]
    
    for prompt in test_prompts:
        print(f"\nUser: {prompt}")
        response = root_agent.run(prompt)
        print(f"Agent: {response}")

if __name__ == "__main__":
    main()
