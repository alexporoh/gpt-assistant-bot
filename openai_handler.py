from openai import OpenAI
from config import OPENAI_KEY
from database import get_prompt

client = OpenAI(api_key=OPENAI_KEY)

def chat_with_gpt(user_input):
    system_prompt = get_prompt()

    print("📤 [GPT] Исходящий запрос:")
    print(f"[SYSTEM]: {system_prompt}")
    print(f"[USER]: {user_input}")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]
        )
        answer = response.choices[0].message.content.strip()
        print(f"✅ [GPT] Ответ: {answer}")
        return answer
    except Exception as e:
        print(f"❌ [GPT ERROR]: {e}")
        return "Ошибка при обращении к GPT"