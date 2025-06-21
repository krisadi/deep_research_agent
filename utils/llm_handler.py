import os
from openai import AzureOpenAI, APIConnectionError, RateLimitError, APIStatusError
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Global variable for the client, initialized once
_azure_openai_client = None
_client_error = None

def _initialize_azure_openai_client():
    """
    Initializes the AzureOpenAI client using Azure AD authentication.
    This function is called once to set up the global client.
    """
    global _azure_openai_client, _client_error
    if _azure_openai_client is not None or _client_error is not None: # Already attempted initialization
        return

    try:
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        if not azure_endpoint:
            _client_error = "Azure OpenAI endpoint (AZURE_OPENAI_ENDPOINT) is not set."
            print(f"Error: {_client_error}")
            return

        # DefaultAzureCredential will attempt various auth methods (env vars, managed identity, Azure CLI)
        # The scope "https://cognitiveservices.azure.com/.default" is standard for Azure Cognitive Services.
        credential = DefaultAzureCredential()
        token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")

        _azure_openai_client = AzureOpenAI(
            azure_endpoint=azure_endpoint,
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"), # Use env var or a recent default
            azure_ad_token_provider=token_provider,
        )
        print("AzureOpenAI client initialized successfully with AD authentication.")
    except Exception as e:
        _client_error = f"Failed to initialize Azure OpenAI client: {e}"
        print(f"Error: {_client_error}")

def get_llm_response(prompt_text, system_prompt="You are a helpful research assistant."):
    """
    Interacts with Azure OpenAI to get a response for the given prompt using Chat Completions.
    Uses Azure AD authentication.
    
    Args:
        prompt_text (str): The user's prompt to send to the LLM.
        system_prompt (str): The system message to set the context for the LLM.
                                         
    Returns:
        str: The response content from the LLM.
             Returns an error message string if interaction fails or client isn't initialized.
    """
    _initialize_azure_openai_client() # Ensure client is initialized

    if _client_error:
        return f"Error: Azure OpenAI client not available. {_client_error}"
    if not _azure_openai_client:
         return "Error: Azure OpenAI client is not initialized and no client error was recorded. This is unexpected."


    azure_deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    if not azure_deployment_name:
        return "Error: Azure OpenAI deployment name (AZURE_OPENAI_DEPLOYMENT_NAME) is not set."

    print(f"Sending prompt to Azure OpenAI deployment: {azure_deployment_name}")

    # Default parameters
    model_params = {
        "temperature": 0.7,
        "max_tokens": 1500
    }
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt_text}
    ]

    # Check if deployment name suggests o3-mini model for specific settings
    if azure_deployment_name and "o3-mini" in azure_deployment_name.lower():
        print(f"Applying o3-mini specific settings for deployment: {azure_deployment_name}")
        # Override/set specific parameters for o3-mini with high reasoning effort
        # Remove temperature if not applicable, or set to a value appropriate for high reasoning
        model_params = { 
            "reasoning_effort": "high",
            "max_completion_tokens": 5000 
            # Add temperature here if 'o3-mini' also expects it, e.g., temperature: 0.3
        }
        # Change system message role to "developer"
        messages = [
            {"role": "developer", "content": system_prompt}, # System prompt content is still used
            {"role": "user", "content": prompt_text}
        ]
        # If 'temperature' is not part of o3-mini's specific parameters, 
        # ensure it's not passed by removing it from model_params or not adding it.
        # The example snippet did not include temperature with reasoning_effort.
        # If 'temperature' is still desired, it should be added to model_params above.
        # For now, assuming temperature is not used when reasoning_effort is present.
        if "temperature" in model_params and "reasoning_effort" in model_params:
            # Decide if temperature should be removed or if it's compatible
            # For now, let's assume it might not be needed with reasoning_effort
            # model_params.pop("temperature", None) 
            # Based on snippet, temperature is not used with reasoning_effort, so we won't explicitly set it.
            # The create call will use the defaults of the model if not specified.
            # However, to be safe, let's ensure no conflicting params are sent if not specified in the snippet.
            # The snippet used `max_completion_tokens` not `max_tokens`.
            # The snippet did not include `temperature`.
            pass # model_params is already set correctly for o3-mini case

    else:
        print(f"Using default LLM settings for deployment: {azure_deployment_name}")


    try:
        response = _azure_openai_client.chat.completions.create(
            model=azure_deployment_name, # This is the deployment name
            messages=messages,
            **model_params # Unpack the dictionary of parameters
        )
        content = response.choices[0].message.content
        return content.strip() if content else "LLM returned an empty response."
    except APIConnectionError as e:
        error_msg = f"Azure OpenAI API Connection Error: {e}"
        print(error_msg)
        return error_msg
    except RateLimitError as e:
        error_msg = f"Azure OpenAI API Rate Limit Exceeded: {e}"
        print(error_msg)
        return error_msg
    except APIStatusError as e: # Catches other API errors like 4xx, 5xx
        error_msg = f"Azure OpenAI API Status Error (Status: {e.status_code}): {e.message}"
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"An unexpected error occurred while interacting with Azure OpenAI: {e}"
        print(error_msg)
        return error_msg

if __name__ == '__main__':
    # For local testing of this module:
    # 1. Ensure you are logged in via Azure CLI (`az login`) if using CLI credentials.
    # 2. Set required environment variables:
    #    export AZURE_OPENAI_ENDPOINT="your_endpoint"
    #    export AZURE_OPENAI_DEPLOYMENT_NAME="your_chat_deployment_name"
    #    export AZURE_OPENAI_API_VERSION="2024-02-15-preview" # or your preferred version
    #    (If using Service Principal, also set AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET)
    print("Testing LLM Handler...")
    
    if not os.getenv("AZURE_OPENAI_ENDPOINT") or not os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"):
        print("Skipping test: AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_DEPLOYMENT_NAME not set.")
    else:
        test_prompt = "What is the capital of France? Explain briefly."
        print(f"\nSending test prompt: '{test_prompt}'")
        response = get_llm_response(test_prompt)
        print(f"\nLLM Response:\n{response}")

        print("\n--- Testing with a different system prompt ---")
        response_poet = get_llm_response(
            "Tell me about large language models.",
            system_prompt="You are a poet. Respond in the style of Shakespeare."
        )
        print(f"\nLLM Poet Response:\n{response_poet}")

        print("\n--- Testing error case: missing deployment name (temporarily unset) ---")
        original_deployment_name = os.environ.pop("AZURE_OPENAI_DEPLOYMENT_NAME", None)
        response_error = get_llm_response("This should fail.")
        print(f"\nLLM Error Response:\n{response_error}")
        if original_deployment_name: # Restore if it was set
             os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = original_deployment_name
