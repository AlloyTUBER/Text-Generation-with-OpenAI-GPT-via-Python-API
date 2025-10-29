from openai import OpenAI
import json
import os
import hashlib
from dotenv import load_dotenv

load_dotenv() 
client = OpenAI(api_key = os.getenv("API_KEY"))
    
CACHE_FILE = "cache.json"

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        cache = json.load(f)
else:
    cache = {}

class ChatBot:
    def __init__(self):
        self.temp = ''
        self.question = ''
        self.last_key = None  # Store the last generated key

    def save_cache(self):
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f)

    def clear_cache(self):
        cache.clear()

    def get_key(self, prompt):
        return hashlib.sha256(prompt.encode()).hexdigest()

    def get_response_by_key(self, key):
        return cache.get(key, None)

    def generate_text(self, prompt, token=1000):
        key = self.get_key(prompt)
        self.last_key = key  # Store the key of the last generated response
        
        if key in cache:
            return cache[key]

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=token,
            temperature=0.7
        )

        result = response.choices[0].message.content.strip()
        cache[key] = result
        self.save_cache()
        return result

    def context(self, prompt1, prompt2):
        key2 = self.get_key(prompt2)
        response2 = cache.get(key2, self.generate_text(prompt2))
        check = self.generate_text(f'Does "{response2}" and "{prompt1}" share any context?', token=80)
        return 'yes' in check.lower()

    def run(self):
        print('=========IF YOU WANT TO EXIT CHAT, ENTER: "Exit".=========')
        print("Hi! I'm your GPT-4.0-mini based AI assistant. How may I assist?\n")
        
        prompt = input('Prompt: ')
        if prompt.strip().lower() in ['exit', 'x']:
            print('Thank you for using me!')
            return

        self.temp = prompt
        response = self.generate_text(prompt, token=1000)
        print(response)

        while True:
            prompt = input('Prompt (or enter a key to retrieve previous response): ')
            if prompt.strip().lower() in ['exit', 'x']:
                print('Thank you for using me!')
                break

            # Check if input is a cached key
            if len(prompt) == 64 and prompt in cache:  # SHA-256 hash is 64 characters
                print('\n' + cache[prompt])
                continue

            if self.context(self.temp, prompt):
                question = f'Answer {prompt} with respect to {cache.get(self.get_key(self.temp))}'
                response = self.generate_text(question, token=1000)
                print(response)
            else:
                response = self.generate_text(prompt, token=1000)
                print(response)
            self.temp = prompt

if __name__ == "__main__":
    bot = ChatBot()
    try:
        bot.run()
    finally:
        bot.clear_cache()
