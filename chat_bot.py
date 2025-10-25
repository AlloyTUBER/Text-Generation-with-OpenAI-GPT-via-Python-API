from openai import OpenAI
import json
import os
import hashlib
from dotenv import load_dotenv

load_dotenv() 
client = OpenAI(api_key = os.getenv("API_KEY"))
    
CACHE_FILE = "cache.json" # File Containing unique API keys of prompts

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        cache = json.load(f)
else:
    cache = {} # Dictionary Containing unique API keys of prompts

class ChatBot:
    def __init__(self):
        self.temp = ''
        self.question = ''

    def save_cache(self): # Saves Data into the Cache file
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f)

    def clear_cache(self): # Clears Dictionary data
        cache.clear()

    def generate_text(self, prompt,token=1000): # Generates text based on prompt
        # Checking is prompt was asked previously
        key = hashlib.sha256(prompt.encode()).hexdigest()
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

        # Storing prompts API key
        cache[key] = result
        self.save_cache()
        return result

    def context(self, prompt1, prompt2): # Checks for context between the present and previous prompt(s).
        check = self.generate_text(f'Does "{prompt2}" and "{prompt1}" share any context?',token=80)
        return 'yes' in check.lower()

    def run(self):
        print('=========IF YOU WANT TO EXIT CHAT, ENTER: "Exit".=========')
        print("Hi! I'm your GPT-4.0-mini based AI assistant. How may I assist?\n")
        
        # First prompt
        prompt = input('Prompt: ')
        if prompt.strip().lower() == 'exit':
            print('Thank you for using me!')
            return

        self.temp = prompt
        print('\n' + self.generate_text(prompt,token=1000))

        # Subsequent prompts
        while True:
            prompt = input('Prompt: ')
            if prompt.strip().lower() == 'exit':
                print('Thank you for using me!')
                break

            if self.context(self.temp, prompt):
                question = f"{self.temp} {prompt}"
                print('\n' + self.generate_text(question,token=1000))
            else:
                print('\n' + self.generate_text(prompt,token=1000))
            self.temp = prompt

if __name__ == "__main__":
    bot = ChatBot()
    try:
        bot.run()
    finally:
        bot.clear_cache()