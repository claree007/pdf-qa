import os
import json
import logging
import requests

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

class OpenAILLM:
    def __init__(self, model: str="gpt-4o-mini"):
        self.url = "https://api.openai.com/v1/chat/completions"
        self.model = model

        if not OPENAI_API_KEY:
            raise ValueError("Please set the OPENAI_API_KEY environment variable.")

        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {OPENAI_API_KEY}'
        }

    def get_llm_response(self, system_message: str, user_message: str, max_tokens: int=None, temperature: float=0.1, seed: int=22, **kwargs):
        payload = json.dumps({
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "seed": seed
        })
        response = requests.request("POST", self.url, headers=self.headers, data=payload)
        logging.debug(f"LLM response: {response.text}")
        response = response.json()
        return response['choices'][0]['message']['content']
    
class OpenAIEmbeddings:
    def __init__(self, model: str="text-embedding-3-small"):
        self.url = "https://api.openai.com/v1/embeddings"
        self.model = model

        if not OPENAI_API_KEY:
            raise ValueError("Please set the OPENAI_API_KEY environment variable.")
        
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {OPENAI_API_KEY}'
        }

    def get_embeddings(self, text: str | list):
        payload = json.dumps({
            "input": text,
            "model": self.model
        })
        response = requests.request("POST", self.url, headers=self.headers, data=payload)
        logging.info(f"openai embedding response: {response.text}")
        response = response.json()
        if isinstance(text, str):
            return response['data'][0]['embedding']
        else:
            return [data['embedding'] for data in response['data']]

if __name__ == '__main__':
    llm = OpenAILLM()
    response = llm.get_llm_response(
        system_message="You are a creature from a magical kingdom.",
        user_message="State your name.",
        max_tokens=25,
        temperature=0.4,
        seed=22
    )
    print(response)

    embeddings = OpenAIEmbeddings()
    text = "Hello, world!"
    embedding = embeddings.get_embeddings(text)
    print(embedding)