import os
import datetime
import webbrowser
import asyncio
import pygame
from groq import Groq
from config import GROQ_API_KEY
from language_handling import wishMe, selectLanguage
from command_handling import takeCommand, getTextInput, search_youtube, extract_search_terms
from ai_interactions import ai, chat_terminal  # Modified import for terminal chat
from speech_utils import speak

# Initialize pygame mixer
pygame.mixer.init()

# Initialize Groq API client
client = Groq(api_key=GROQ_API_KEY)

# Current task
current_task = None
task_lock = asyncio.Lock()


async def handle_command(query, language, is_voice):
    global current_task
    async with task_lock:
        if current_task is not None:
            # Cancel the current task
            current_task.cancel()
            try:
                await current_task
            except asyncio.CancelledError:
                pass

        # Start a new task
        current_task = asyncio.create_task(process_command(query, language, is_voice))
        await current_task


async def process_command(query, language, is_voice):
    handled_command = False

    # Command to open specific websites
    sites = [["youtube", "https://www.youtube.com"], ["wikipedia", "https://www.wikipedia.com"],
             ["google", "https://www.google.com"], ["Twilio", "https://console.twilio.com/"],
             ["Projects", "https://zingsolutions.atlassian.net/jira/projects"],
             ["Cases", "https://zing.lightning.force.com/lightning/o/Case/list?filterName=__Recent"],
             ["Timesheets", "https://hub.zing.dev/"], ["Charlie", "https://zingdevlimited.charliehr.com/"],
             ["Github", "https://github.com/"], ["ChatGpt", "https://chatgpt.com/"]]
    for site in sites:
        if f"Open {site[0]}".lower() in query.lower():
            if language == "hi":
                await asyncio.to_thread(speak, f"{site[0]} खोल रही हूँ...", "hi")
            else:
                await asyncio.to_thread(speak, f"Opening {site[0]} sir...", "en")
            webbrowser.open(site[1])
            handled_command = True
            break

    # YouTube specific handling
    if "using youtube " in query.lower():
        search_terms = query.lower().replace("using youtube", "").strip()
        search_terms = extract_search_terms(search_terms)
        videos = search_youtube(search_terms)
        if videos:
            if language == "hi":
                await asyncio.to_thread(speak, f"आपकी खोज {search_terms} के आधार पर यहां शीर्ष 5 परिणाम हैं।", "hi")
                await asyncio.to_thread(speak, "कृपया बताएं कि मैं कौन सा वीडियो चलाऊँ।", "hi")
            else:
                await asyncio.to_thread(speak, f"Based on your search {search_terms} here are top 5 results.", "en")
                await asyncio.to_thread(speak, "Please select which one to play.")
        if "youtube.com/watch?v=" in search_terms or "youtu.be/" in search_terms:
            # Direct YouTube URL
            video_url = search_terms
            if language == "hi":
                await asyncio.to_thread(speak, "वीडियो चला रही हूँ।", "hi")
            else:
                await asyncio.to_thread(speak, "Playing the video.", "en")
            webbrowser.open(video_url)
            handled_command = True
        elif search_terms:
            # Search for a video
            if language == "hi":
                await asyncio.to_thread(speak, "कृपया नंबर दर्ज करें ।", "hi")
            else:
                await asyncio.to_thread(speak, "Please enter or say the number.", "en")

            # Get the user's choice
            if is_voice:
                user_choice = await takeCommand(language)
            else:
                user_choice = await getTextInput(language)

            # Validate and process the user's choice
            try:
                choice_index = int(user_choice) - 1
                if 0 <= choice_index < len(videos):
                    video_title, video_url = videos[choice_index]
                    if language == "hi":
                        await asyncio.to_thread(speak, f"{video_title} वीडियो चला रही हूँ।", "hi")
                    else:
                        await asyncio.to_thread(speak, f"Playing the video: {video_title}.", "en")
                    webbrowser.open(video_url)
                    handled_command = True
                else:
                    if language == "hi":
                        await asyncio.to_thread(speak, "अमान्य विकल्प। कृपया पुनः प्रयास करें।", "hi")
                    else:
                        await asyncio.to_thread(speak, "Invalid choice. Please try again.", "en")
            except ValueError:
                if language == "hi":
                    await asyncio.to_thread(speak, "अमान्य इनपुट। कृपया एक संख्या दर्ज करें।", "hi")
                else:
                    await asyncio.to_thread(speak, "Invalid input. Please enter a number.", "en")
        else:
            if language == "hi":
                await asyncio.to_thread(speak, "कोई वीडियो नहीं मिला।", "hi")
            else:
                await asyncio.to_thread(speak, "No videos found.", "en")

    # Other commands
    if not handled_command:
        if "what's the time" in query:
            hour = datetime.datetime.now().strftime("%H")
            min = datetime.datetime.now().strftime("%M")
            if language == "hi":
                await asyncio.to_thread(speak, f"साहब, समय {hour} घंटे और {min} मिनट है।", "hi")
            else:
                await asyncio.to_thread(speak, f"Sir, the time is {hour} hours and {min} minutes.", "en")
            handled_command = True

        elif "open vscode".lower() in query.lower():
            if language == "hi":
                await asyncio.to_thread(speak, "VSCode खोल रही हूँ, सर...", "hi")
            else:
                await asyncio.to_thread(speak, "Opening VSCode Sir...", "en")
            os.system("code")
            handled_command = True

        elif "open slack".lower() in query.lower():
            if language == "hi":
                await asyncio.to_thread(speak, "Slack खोल रही हूँ, सर...", "hi")
            else:
                await asyncio.to_thread(speak, "Opening Slack Sir...", "en")
            os.system("Slack")
            handled_command = True

        elif "play music".lower() in query.lower():
            if language == "hi":
                await asyncio.to_thread(speak, "आपका गाना बजा रही हूँ, सर...", "hi")
            else:
                await asyncio.to_thread(speak, "Playing your song, Sir...", "en")
            musicPath = r"C:\Users\AnkitBalhara\Music\Dekha Tenu Pehli Pehli Baar Ve_320(PagalWorld.com.sb).mp3"
            os.system(f'start wmplayer "{musicPath}"')
            handled_command = True

        elif "open chrome".lower() in query.lower():
            if language == "hi":
                await asyncio.to_thread(speak, "Chrome खोल रही हूँ, सर...", "hi")
            else:
                await asyncio.to_thread(speak, "Opening Chrome Sir...", "en")
            os.system("start chrome")
            handled_command = True

        elif "using artificial intelligence".lower() in query.lower():
            await ai(prompt=query, language=language)

        elif "aria quit".lower() in query.lower():
            if language == "hi":
                await asyncio.to_thread(speak, "Aria बंद हो गई। Aria का उपयोग करने के लिए धन्यवाद।", "hi")
            else:
                await asyncio.to_thread(speak, "Aria Quit. Thanks for trying Aria.", "en")
            exit()

        elif "reset chat".lower() in query.lower():
            chatStr = ""
            handled_command = True

        if not handled_command:
            if language == "hi":
                print("चैटिंग...")
            else:
                print("Chatting...")
            await chat_terminal(query, language)  # Updated for terminal-based chat

    # Reset attempt counter after a successful command
    attempt = 0


async def main():
    global chatStr
    chatStr = ""

    # Display and speak the welcome message in both languages
    await asyncio.to_thread(speak, "Welcome to Aria A.I", "en")
    await asyncio.to_thread(speak, "अरिया ए.आई  में आपका स्वागत है", "hi")
    print("Welcome to Aria A.I")
    print("अरिया ए.आई  में आपका स्वागत है")

    # Use wishMe function to greet the user
    language = await selectLanguage()
    await wishMe(language)

    is_voice = None

    while is_voice is None:
        if language == "hi":
            await asyncio.to_thread(speak, "इनपुट विधि चुनें (टेक्स्ट के लिए 1, आवाज़ के लिए 2)", "hi")
            input_method = input("इनपुट विधि चुनें: ").strip()
        else:
            await asyncio.to_thread(speak, "Choose input method (1 for Text, 2 for Voice)", "en")
            input_method = input("Choose input method: ").strip()

        if input_method == "1":
            is_voice = False
            if language == "hi":
                await asyncio.to_thread(speak, "टेक्स्ट सहायक अरिया में आपका स्वागत है, कृपया अपना इनपुट टाइप करें...",
                                        "hi")
            else:
                await asyncio.to_thread(speak, "Welcome to text assisted Aria, Please type your input...", "en")
        elif input_method == "2":
            is_voice = True
            if language == "hi":
                await asyncio.to_thread(speak, "वॉयस सहायक अरिया में आपका स्वागत है, कृपया अपना आदेश बोलें..", "hi")
            else:
                await asyncio.to_thread(speak, "Welcome to voice assisted Aria, Please speak your command...", "en")
        else:
            if language == "hi":
                await asyncio.to_thread(speak, "अमान्य चयन। कृपया 1 या 2 चुनें।", "hi")
            else:
                await asyncio.to_thread(speak, "Invalid choice. Please select 1 or 2.", "en")

    while True:
        if is_voice:
            print("Listening...")
            query = await takeCommand(language)
        else:
            query = await getTextInput(language)

        if query:
            await handle_command(query, language, is_voice)
        else:
            if language == "hi":
                await asyncio.to_thread(speak, "कोई इनपुट नहीं मिला। नया इनपुट का इंतजार कर रही हूँ...", "hi")
            else:
                await asyncio.to_thread(speak, "No input detected. Waiting for new input...", "en")
            # Continue waiting for new input indefinitely


if __name__ == "__main__":
    asyncio.run(main())
