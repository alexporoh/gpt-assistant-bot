import openai
from config import OPENAI_KEY
from database import get_prompt

openai.api_key = OPENAI_KEY

def chat_with_gpt(user_input):
    system_prompt = get_prompt()
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return "Ошибка при обращении к GPT"