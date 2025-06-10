from google.adk.agents import Agent

def calculator(operation: str, a: float, b: float) -> dict:
    """Performs basic arithmetic operations.
    
    Args:
        operation (str): The operation to perform (add, subtract, multiply, divide).
        a (float): The first number.
        b (float): The second number.
        
    Returns:
        dict: Status and result or error message.
    """
    operation = operation.lower()
    
    if operation == "add":
        result = a + b
        return {"status": "success", "result": f"{a} + {b} = {result}"}
    elif operation == "subtract":
        result = a - b
        return {"status": "success", "result": f"{a} - {b} = {result}"}
    elif operation == "multiply":
        result = a * b
        return {"status": "success", "result": f"{a} * {b} = {result}"}
    elif operation == "divide":
        if b == 0:
            return {"status": "error", "error_message": "Cannot divide by zero."}
        result = a / b
        return {"status": "success", "result": f"{a} / {b} = {result}"}
    else:
        return {
            "status": "error", 
            "error_message": f"Unknown operation: {operation}. Please use add, subtract, multiply, or divide."
        }

root_agent = Agent(
    name="calculator_agent",
    model="gemini-2.0-flash",
    description="Agent that can perform basic arithmetic operations.",
    instruction="You are a helpful calculator agent that can perform basic arithmetic operations like addition, subtraction, multiplication, and division.",
    tools=[calculator],
)
