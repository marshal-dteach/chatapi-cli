#!/usr/bin/env python3
"""
Example usage of the ChatAPI CLI tool with both OpenAI and Perplexity providers.
"""

from chatapi_cli import ChatAPICLI

def main():
    # Initialize the CLI tool
    cli = ChatAPICLI()
    
    # Example 1: Using OpenAI
    print("=== OpenAI Example ===")
    cli.config['provider'] = 'openai'
    cli.config['openai_api_key'] = 'your-openai-api-key-here'  # Replace with your key
    cli.save_config(cli.config)
    
    # This would work if you have a valid OpenAI API key
    # response = cli.chat("What is the capital of France?")
    # print(f"OpenAI Response: {response}")
    
    # Example 2: Using Perplexity
    print("\n=== Perplexity Example ===")
    cli.config['provider'] = 'perplexity'
    cli.config['perplexity_api_key'] = 'your-perplexity-api-key-here'  # Replace with your key
    cli.save_config(cli.config)
    
    # This would work if you have a valid Perplexity API key
    # response = cli.chat("What is the latest news about AI?")
    # print(f"Perplexity Response: {response}")
    
    print("\nTo use this example:")
    print("1. Replace 'your-openai-api-key-here' with your actual OpenAI API key")
    print("2. Replace 'your-perplexity-api-key-here' with your actual Perplexity API key")
    print("3. Uncomment the response lines to see actual API calls")

if __name__ == "__main__":
    main() 