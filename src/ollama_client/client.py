import requests
import json

class OllamaError(Exception):
    """Custom exception for Ollama client errors."""
    pass

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        """Initializes the client with the Ollama base URL."""
        if not base_url:
            raise ValueError("Ollama base URL cannot be empty.")
        self.base_url = base_url.rstrip('/') # Remove trailing slash if present
        self.generate_endpoint = f"{self.base_url}/api/generate"

    def check_connection(self):
        """Checks if the Ollama server is reachable."""
        try:
            response = requests.get(self.base_url, timeout=5) # Short timeout for health check
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            print(f"Successfully connected to Ollama at {self.base_url}")
            return True
        except requests.exceptions.ConnectionError:
            print(f"Connection Error: Could not connect to Ollama at {self.base_url}")
            return False
        except requests.exceptions.Timeout:
            print(f"Timeout Error: Connection to {self.base_url} timed out.")
            return False
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Ollama at {self.base_url}: {e}")
            return False

    def analyze_code(self, code_snippet, user_prompt, model="llama3"):
        """
        Sends the code snippet and prompt to the Ollama API for analysis.

        Args:
            code_snippet (str): The code to analyze.
            user_prompt (str): The user's question or prompt about the code.
            model (str): The name of the Ollama model to use (default: "llama3").

        Returns:
            str: The analysis response from the Ollama model.

        Raises:
            OllamaError: If there's an issue communicating with the API or parsing the response.
        """
        if not self.base_url:
             raise OllamaError("Ollama URL is not configured.")
             
        # Combine the user prompt and the code snippet for the LLM context
        # Using Markdown code block for clarity
        full_prompt = f"{user_prompt}\n\nAnalyze the following code snippet:\n\n```\n{code_snippet}\n```"

        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": False # We want the full response at once
        }

        try:
            print(f"Sending request to {self.generate_endpoint} with model {model}")
            response = requests.post(
                self.generate_endpoint, 
                json=payload, 
                headers={'Content-Type': 'application/json'},
                timeout=60 # Longer timeout for generation
            )
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            response_data = response.json()
            
            if "response" in response_data:
                return response_data["response"].strip()
            elif "error" in response_data:
                 raise OllamaError(f"Ollama API Error: {response_data['error']}")
            else:
                raise OllamaError("Unexpected response format from Ollama API.")

        except requests.exceptions.ConnectionError as e:
            raise OllamaError(f"Connection Error: Could not connect to Ollama at {self.generate_endpoint}. Is it running? Details: {e}")
        except requests.exceptions.Timeout:
            raise OllamaError(f"Timeout Error: Request to {self.generate_endpoint} timed out.")
        except requests.exceptions.RequestException as e:
            raise OllamaError(f"API Request Error: {e}")
        except json.JSONDecodeError:
            raise OllamaError(f"Failed to decode JSON response from {self.generate_endpoint}. Response text: {response.text[:200]}...")
        except Exception as e:
            # Catch any other unexpected errors during the process
            raise OllamaError(f"An unexpected error occurred: {e}")

# Example Usage (for testing)
if __name__ == '__main__':
    # Assumes Ollama is running locally with llama3 model pulled
    client = OllamaClient() 

    if client.check_connection():
        test_code = (
            "func check_debugger() {\n"
            "    if (IsDebuggerPresent()) {\n"
            "        ExitProcess(0);\n"
            "    }\n"
            "}"
        )
        test_prompt = "What does this code do and what is its purpose in malware?"
        
        try:
            print("\nSending analysis request...")
            analysis = client.analyze_code(test_code, test_prompt)
            print("\nAnalysis Result:")
            print(analysis)
        except OllamaError as e:
            print(f"\nError during analysis: {e}")
        except Exception as e:
             print(f"\nAn unexpected error occurred during example execution: {e}")
    else:
        print("\nSkipping analysis test as Ollama connection check failed.")
