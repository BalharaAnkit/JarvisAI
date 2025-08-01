import os
import pygame
from groq import Groq
from config import GROQ_API_KEY
import asyncio
from CoreTask.speech_utils import speak

# Initialize pygame mixer
pygame.mixer.init()

# Initialize Groq API client
client = Groq(api_key=GROQ_API_KEY)

# Global state for chat
chatStr = ""
current_ai_task = None
ai_task_lock = asyncio.Lock()

async def chat(query, language, display_response=None):
    global current_ai_task
    async with ai_task_lock:
        if current_ai_task is not None:
            current_ai_task.cancel()
            try:
                await current_ai_task
            except asyncio.CancelledError:
                pass

        current_ai_task = asyncio.create_task(process_chat(query, language, display_response))
        response = await current_ai_task  # Await the task and get the response
        await asyncio.to_thread(speak, response, language)  # Speak the response
        return response  # Return the response

async def process_chat(query, language, display_response=None):
    global chatStr
    chatStr += f"User: {query}\n"
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": chatStr}],
            model="llama-3.1-70b-versatile",
            temperature=0.7,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        response_text = response.choices[0].message.content.strip()
        chatStr += f"{response_text}\n"

        # Update GUI display with the response if display_response is provided
        if display_response:
            display_response(response_text)

        return response_text  # Return response before speaking

    except Exception as e:
        await asyncio.to_thread(speak, "An unexpected error occurred.", language)
        print(f"Unexpected Error: {e}")
        return "An error occurred."

async def chat_terminal(user_query, language):
    """
    Handles chat interactions in terminal mode.
    This function sends the user query to the AI model and gets the response.
    """
    response = await process_chat(user_query, language)  # Use process_chat for terminal response
    await asyncio.to_thread(speak, response, language)  # Speak the response here
    print(f"Jarvis: {response}")  # Print response in terminal


async def ai(prompt, language):
    global current_ai_task
    async with ai_task_lock:
        if current_ai_task is not None:
            current_ai_task.cancel()
            try:
                await current_ai_task
            except asyncio.CancelledError:
                pass

        current_ai_task = asyncio.create_task(process_ai(prompt, language))
        await current_ai_task

async def process_ai(prompt, language):
    text = f"Groq response for Prompt: {prompt} \n *************************\n\n"
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-70b-versatile",
            temperature=0.7,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        response_text = response.choices[0].message.content.strip()
        text += response_text
        await asyncio.to_thread(speak, response_text, language)

        if not os.path.exists("GroqResponses"):
            os.mkdir("GroqResponses")
        filename = f"GroqResponses/{''.join(prompt.split('intelligence')[1:]).strip()}.txt"
        with open(filename, "w") as f:
            f.write(text)
    except Exception as e:
        await asyncio.to_thread(speak, "An unexpected error occurred.", language)
        print(f"Unexpected Error: {e}")