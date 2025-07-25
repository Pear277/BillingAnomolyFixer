from crewai import LLM

llm = LLM(model="ollama/llama3.2:1b")


if __name__ == "__main__":
    # Test the LLM first
    print("Testing LLM...")
    try:
        test_response = llm.call([{"role": "user", "content": "What model are you?"}])
        print("LLM Response:", test_response)
    except Exception as e:
        print("LLM Error:", e)
    
    # Check if Ollama is running
    import subprocess
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        print("Ollama models:", result.stdout)
    except:
        print("Ollama not found or not running")