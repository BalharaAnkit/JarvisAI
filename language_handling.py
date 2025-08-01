import asyncio
from speech_utils import speak
import datetime


async def wishMe(language):
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        if language == "hi":
            await asyncio.to_thread(speak, "सुप्रभात", "hi")
        else:
            await asyncio.to_thread(speak, "Good Morning!")
    elif hour >= 12 and hour < 18:
        if language == "hi":
            await asyncio.to_thread(speak, "नमस्कार", "hi")
        else:
            await asyncio.to_thread(speak, "Good Afternoon!")
    else:
        if language == "hi":
            await asyncio.to_thread(speak, "शुभ संध्या", "hi")
            await asyncio.to_thread(speak, "मैं अरिया हूँ। कृपया बताएं मैं आपकी कैसे मदद कर सकती हूँ?", "hi")
        else:
            await asyncio.to_thread(speak, "Good Evening!")
            await asyncio.to_thread(speak, "I am Aria. Please tell me how may I help you?")


async def selectLanguage():
    # Ask in both English and Hindi before language selection
    await asyncio.to_thread(speak, "Please select your language", "en")
    await asyncio.to_thread(speak, "कृपया अपनी भाषा चुनें", "hi")
    await asyncio.to_thread(speak, "Press 1 for Hindi or Press 2 for English...", "en")
    await asyncio.to_thread(speak, "हिंदी के लिए 1 दबाएँ या अंग्रेजी के लिए 2 दबाएँ...", "hi")

    # Get the user's choice
    language_choice = input("Select Language (1 for Hindi, 2 for English): ").strip()

    # Handle language selection
    if language_choice == "1":
        await asyncio.to_thread(speak, "हिंदी को अपनी भाषा के रूप में चुनने के लिए धन्यवाद, आपका स्वागत है!", "hi")
        return "hi"
    elif language_choice == "2":
        await asyncio.to_thread(speak, "Welcome! Thanks for choosing English as your Language.", "en")
        return "en"
    else:
        await asyncio.to_thread(speak, "Please select your language:", "en")
        await asyncio.to_thread(speak, "कृपया अपनी भाषा चुनें:", "hi")
        await asyncio.to_thread(speak, "Press 1 for Hindi or Press 2 for English...", "en")
        await asyncio.to_thread(speak, "हिंदी के लिए 1 दबाएँ या अंग्रेजी के लिए 2 दबाएँ...", "hi")

        # Get the user's choice
        language_choice = input("Select Language (1 for Hindi, 2 for English): ").strip()
        return "en"
