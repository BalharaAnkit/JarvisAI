import threading
import asyncio
import requests
import speech_recognition as sr
from config import YouTube_API_KEY
from speech_utils import speak

# Lock for managing concurrent input tasks
input_task_lock = asyncio.Lock()


async def takeCommand(language="en"):
    max_attempts = 4
    attempt = 0
    base_timeout = 60  # Timeout in seconds

    r = sr.Recognizer()

    while attempt < max_attempts:
        input_event = threading.Event()
        user_input = [None]

        def input_thread():
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)
                try:
                    audio = r.listen(source, timeout=base_timeout)
                    print("Recognizing...")
                    user_input[0] = r.recognize_google(audio, language="hi" if language == "hi" else "en-in")
                    print(f"User said: {user_input[0]}")
                    input_event.set()
                except Exception as e:
                    user_input[0] = None
                    input_event.set()

        input_thread_obj = threading.Thread(target=input_thread)
        input_thread_obj.start()
        input_event.wait(base_timeout)

        if user_input[0] is not None:
            return user_input[0]

        attempt += 1
        if attempt < max_attempts:
            elapsed_minutes = attempt
            if attempt == max_attempts - 1:
                if language == "hi":
                    await asyncio.to_thread(speak,
                                            "चेतावनी: यह आपका आखिरी प्रयास है। यदि कोई इनपुट प्रदान नहीं किया गया, तो Aria बंद हो जाएगी।",
                                            "hi")
                else:
                    await asyncio.to_thread(speak,
                                            "Warning: This is your last attempt. If no input is provided, Aria will quit.",
                                            "en")
            else:
                if language == "hi":
                    await asyncio.to_thread(speak,
                                            f"{elapsed_minutes} मिनट हो चुका है। कोई इनपुट नहीं मिला। दोबारा प्रयास कर रही हूँ।",
                                            "hi")
                else:
                    await asyncio.to_thread(speak,
                                            f"It's been over {elapsed_minutes} minute(s). No input detected from you. Making Attempt {attempt} of {max_attempts - 1}.",
                                            "en")
        else:
            if language == "hi":
                await asyncio.to_thread(speak, "कोई उत्तर नहीं मिला। Aria बंद हो रही है।", "hi")
            else:
                await asyncio.to_thread(speak, "No response detected. Aria is quitting.", "en")
            exit()


async def getTextInput(language):
    max_attempts = 4
    attempt = 0
    base_timeout = 60  # Timeout in seconds

    while attempt < max_attempts:
        input_event = threading.Event()
        user_input = [None]

        def input_thread():
            user_input[0] = input("कृपया अपना इनपुट टाइप करें: " if language == "hi" else "Please type your input: ")
            input_event.set()

        input_thread_obj = threading.Thread(target=input_thread)
        input_thread_obj.start()
        input_event.wait(base_timeout)

        if user_input[0] is not None:
            return user_input[0]

        attempt += 1
        if attempt < max_attempts:
            elapsed_minutes = attempt
            if attempt == max_attempts - 1:
                if language == "hi":
                    await asyncio.to_thread(speak,
                                            "चेतावनी: यह आपका आखिरी प्रयास है। यदि कोई इनपुट प्रदान नहीं किया गया, तो Aria बंद हो जाएगी।",
                                            "hi")
                else:
                    await asyncio.to_thread(speak,
                                            "Warning: This is your last attempt. If no input is provided, Aria will quit.",
                                            "en")
            else:
                if language == "hi":
                    await asyncio.to_thread(speak,
                                            f"{elapsed_minutes} मिनट हो चुका है। कोई इनपुट नहीं मिला। दोबारा प्रयास कर रही हूँ।",
                                            "hi")
                else:
                    await asyncio.to_thread(speak,
                                            f"It's been over {elapsed_minutes} minute(s). No input detected from you. Making Attempt {attempt} of {max_attempts - 1}.",
                                            "en")
        else:
            if language == "hi":
                await asyncio.to_thread(speak, "कोई उत्तर नहीं मिला। Aria बंद हो रही है।", "hi")
            else:
                await asyncio.to_thread(speak, "No response detected. Aria is quitting.", "en")
            exit()


def search_youtube(query):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'q': query,
        'key': YouTube_API_KEY,
        'type': 'video',
        'maxResults': 5  # Fetching top 5 results
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        if 'items' not in data or not data['items']:
            return None

        # Extract video details
        videos = []
        for index, item in enumerate(data['items']):
            video_title = item['snippet']['title']
            video_id = item['id']['videoId']
            video_url = f"https://www.youtube.com/watch?v={video_id}&autoplay=1"
            videos.append((video_title, video_url))
            print(f"{index + 1}. {video_title}")  # Displaying numbered video titles

        return videos
    except requests.RequestException as e:
        print(f"Error fetching YouTube data: {e}")
        return None


def extract_search_terms(query):
    """Extract search terms from the user's query or return the URL if it's a direct link."""
    query = query.lower().strip()

    # Check for direct YouTube URL
    if "youtube.com/watch?v=" in query or "youtu.be/" in query:
        return query

    # Remove common phrases that aren't part of the search term
    common_phrases = ["play video", "music video", "related video", "play"]
    for phrase in common_phrases:
        query = query.replace(phrase, "").strip()

    # Return cleaned search terms
    return query


def ask_which_video_to_play(results, language):
    # Speak the results
    for idx, result in enumerate(results, start=1):
        if language == "hi":
            speak(f"परिणाम {idx}: {result['title']}।", "hi")
        else:
            speak(f"Result {idx}: {result['title']}.", "en")

    # Ask the user which video to play
    if language == "hi":
        speak("आप कौन सा वीडियो चलाना चाहेंगे? कृपया संख्या बताएं।", "hi")
    else:
        speak("Which video would you like to play? Please select the number.", "en")
