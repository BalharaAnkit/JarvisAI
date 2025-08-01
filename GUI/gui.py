import tkinter as tk
from tkinter import scrolledtext, messagebox
import asyncio
import webbrowser
import threading
import os
import datetime
from CoreTask.command_handling import takeCommand, getTextInput, search_youtube, extract_search_terms
from CoreTask.ai_interactions import chat
from CoreTask.speech_utils import speak


class AriaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Aria Assistant")


        self.videos = []  # Hold the videos for YouTube search results
        self.expecting_video_choice = False  # Track if expecting a video choice

        # Text area for output
        self.output_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=27)
        self.output_area.pack(pady=10)


        # Language selection
        self.language_var = tk.StringVar(value=None)  # No default language at startup
        self.language_label = tk.Label(root, text="Select Language:")
        self.language_label.pack(pady=5)


        self.language_dropdown = tk.OptionMenu(root, self.language_var, "en", "hi")
        self.language_dropdown.pack(pady=5)


        # Start button for the assistant
        self.start_button = tk.Button(root, text="Start Aria", command=self.start_aria)
        self.start_button.pack(pady=5)


        # Stop button for the assistant
        self.stop_button = tk.Button(root, text="Stop Aria", command=self.stop_aria)
        self.stop_button.pack(pady=5)
        self.stop_button.config(state=tk.DISABLED)  # Initially disabled


        # Start voice input button
        self.speech_button = tk.Button(root, text="Start Voice Input", command=self.start_voice_input)
        self.speech_button.pack(pady=5)
        self.speech_button.config(state=tk.DISABLED)  # Initially disabled


        # Text input section
        self.text_input_label = tk.Label(root, text="Or type your command:")
        self.text_input_label.pack(pady=5)


        self.text_input = tk.Entry(root, width=50)
        self.text_input.pack(pady=5)
        self.text_input.config(state=tk.DISABLED)  # Initially disabled


        self.text_input.bind("<Return>", self.submit_text_command)  # Bind Enter key to submit text command

        self.text_input_button = tk.Button(root, text="Submit Text Command", command=self.submit_text_command)
        self.text_input_button.pack(pady=5)
        self.text_input_button.config(state=tk.DISABLED)  # Initially disabled


        # Clear chat button
        self.clear_chat_button = tk.Button(root, text="Clear Chat", command=self.clear_chat)
        self.clear_chat_button.pack(pady=5)
        self.clear_chat_button.config(state=tk.DISABLED)  # Initially disabled


        # Welcome the user
        self.welcome_user()


    def welcome_user(self):
        # Start greeting the user based on time
        threading.Thread(target=self.greet_user).start()

    async def wishMe(self, language):
        hour = int(datetime.datetime.now().hour)
        if hour >= 0 and hour < 12:
            message = "Good Morning!" if language == "en" else "सुप्रभात"
        elif hour >= 12 and hour < 18:
            message = "Good Afternoon!" if language == "en" else "नमस्कार"
        else:
            message = "Good Evening!" if language == "en" else "शुभ संध्या"

        return message

    def greet_user(self):
        # Get greetings for both languages
        english_greeting = asyncio.run(self.wishMe("en"))
        hindi_greeting = asyncio.run(self.wishMe("hi"))

        # Update the output area with time-based greetings
        self.output_area.insert(tk.END, f"{english_greeting}\n")
        self.output_area.insert(tk.END, f"{hindi_greeting}\n")

        # Speak the greetings
        threading.Thread(target=self.speak_greetings, args=(english_greeting, hindi_greeting)).start()

        # Wait for the greetings to finish speaking before showing the welcome message
        self.root.after(3000, self.show_welcome_message)  # Adjust time as needed

    def show_welcome_message(self):
        # Standard welcome messages
        welcome_message = "Welcome to Aria Assistant! Please click 'Start Aria' to begin."
        welcome_message_hi = "अरिया सहायक में आपका स्वागत है! कृपया 'Start Aria' बटन पर क्लिक करें।"

        # Update the output area with standard welcome messages
        self.output_area.insert(tk.END, f"{welcome_message}\n")
        self.output_area.insert(tk.END, f"{welcome_message_hi}\n")

        # Speak the welcome messages
        threading.Thread(target=self.speak_welcome_messages, args=(welcome_message, welcome_message_hi)).start()

    def speak_greetings(self, english_greeting, hindi_greeting):
        # Speak the greetings
        speak(english_greeting, "en", silent=True)
        speak(hindi_greeting, "hi", silent=True)

    def speak_welcome_messages(self, welcome_message, welcome_message_hi):
        # Speak the welcome messages
        speak(welcome_message, "en", silent=True)
        speak(welcome_message_hi, "hi", silent=True)

    def start_aria(self):
        """
        Start Aria, greet the user, and prompt them to select a language.
        """
        # Disable other buttons and enable only the language dropdown
        self.language_dropdown.config(state=tk.NORMAL)
        self.start_button.config(state=tk.DISABLED)
        self.speech_button.config(state=tk.DISABLED)
        self.text_input.config(state=tk.DISABLED)
        self.text_input_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.clear_chat_button.config(state=tk.DISABLED)

        # Greet the user in both languages

        # Print the language selection messages in both languages
        language_message = "Please select your desired language. You can change it anytime."
        language_message_hi = "कृपया अपनी पसंदीदा भाषा चुनें। आप इसे कभी भी बदल सकते हैं।"
        self.output_area.insert(tk.END, f"{language_message}\n")
        self.output_area.insert(tk.END, f"{language_message_hi}\n")

        # Speak the language selection messages in both languages
        threading.Thread(target=self.speak_language_messages).start()

        # Monitor language selection through the dropdown
        self.language_var.trace("w", self.on_language_selected)

    def speak_language_messages(self):
        speak("Please select your desired language. You can change it anytime.", "en", silent=True)
        speak("कृपया अपनी पसंदीदा भाषा चुनें। आप इसे कभी भी बदल सकते हैं।", "hi", silent=True)

    def stop_aria(self):
        self.language_dropdown.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)
        self.speech_button.config(state=tk.DISABLED)
        self.text_input.config(state=tk.DISABLED)
        self.text_input_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.DISABLED)
        self.clear_chat_button.config(state=tk.DISABLED)

        """
        Stop Aria and thank the user for using the assistant.
        """
        self.output_area.insert(tk.END, "Aria has been stopped. Thank you for using Aria Assistant.\n")
        threading.Thread(target=speak,
                         args=("Aria has been stopped. Thank you for using Aria Assistant.", "en", True)).start()
        threading.Thread(target=speak,
                         args=("अरिया बंद हो गई है। अरिया सहायक का उपयोग करने के लिए धन्यवाद।", "hi", True)).start()

    def on_language_selected(self, *args):
        selected_language = self.language_var.get()
        if selected_language:
            if selected_language == "hi":
                message = "आपने हिंदी को अपनी भाषा के रूप में चुना है। आप इसे कभी भी बदल सकते हैं।"
            else:
                message = "You have selected English as your language. You can change it anytime."

            # Print the language selection message to the GUI
            self.output_area.insert(tk.END, f"Aria: {message}\n")
            self.output_area.see(tk.END)  # Scroll to the end

            # Use a single thread to speak the message and continue
            threading.Thread(target=self.speak_message_and_prepare_chat, args=(message, selected_language)).start()

    def speak_message_and_prepare_chat(self, message, language):
        # Speak the language selection message
        speak(message, language, silent=True)

        # After the message is spoken, clear the chat area
        self.clear_chat()

        # Display the "ready to chat" message
        if language == "hi":
            start_message = "अब आप चैट शुरू कर सकते हैं! आप अपना संदेश लिखें या वॉयस इनपुट का उपयोग करें।"
        else:
            start_message = "You can now start chatting! Type your message or use voice input."

        # Insert this message in the cleared chat area
        self.output_area.insert(tk.END, f"Aria: {start_message}\n")
        self.output_area.see(tk.END)

        # Speak the "ready to chat" message
        speak(start_message, language, silent=True)

        # Enable all input options
        self.speech_button.config(state=tk.NORMAL)
        self.text_input.config(state=tk.NORMAL)
        self.text_input_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.DISABLED)
        self.clear_chat_button.config(state=tk.NORMAL)

    def clear_chat(self):
        """Clear all text in the output area."""
        self.output_area.delete(1.0, tk.END)

    def start_voice_input(self):
        language = self.language_var.get()
        self.output_area.insert(tk.END, "Listening...\n")
        self.output_area.see(tk.END)

        # Capture voice input
        threading.Thread(target=self.capture_voice_input, args=(language,)).start()

    def capture_voice_input(self, language):
        command = asyncio.run(takeCommand(language))
        self.process_command(command, language)

    def submit_text_command(self, event=None):  # Accept event for Enter key
        language = self.language_var.get()
        query = self.text_input.get()
        self.output_area.insert(tk.END, f"You: {query}\n")
        self.text_input.delete(0,
                               tk.END)  # Clear the text input after submission                          //Not on the terminal
        self.process_command(query, language)

    def clear_chat(self):
        self.output_area.delete(1.0, tk.END)  # Clear all text in the output area

    def process_command(self, query, language):
        if self.expecting_video_choice:
            self.handle_video_choice(query)
            return  # Prevent further processing if expecting a video choice

        # Command handling
        handled_command = False

        # Websites to open
        sites = [["youtube", "https://www.youtube.com"], ["wikipedia", "https://www.wikipedia.com"],
                 ["google", "https://www.google.com"], ["Twilio", "https://console.twilio.com/"],
                 ["Projects", "https://zingsolutions.atlassian.net/jira/projects"],
                 ["Cases", "https://zing.lightning.force.com/lightning/o/Case/list?filterName=__Recent"],
                 ["Timesheets", "https://hub.zing.dev/"], ["Charlie", "https://zingdevlimited.charliehr.com/"],
                 ["Github", "https://github.com/"], ["ChatGpt", "https://chatgpt.com/"]]

        for site in sites:
            if f"open {site[0]}".lower() in query.lower():
                if language == "hi":
                    speak(f"{site[0]} खोल रही हूँ...", "hi")
                else:
                    speak(f"Opening {site[0]} sir...", "en")
                webbrowser.open(site[1])
                self.output_area.insert(tk.END, f"Opening {site[0]}...\n")
                handled_command = True
                break

        if not handled_command:
            thread = threading.Thread(target=self.handle_ai_response, args=(query, language))
            thread.start()

    def handle_ai_response(self, query, language):
        # Command handling
        handled_command = False

        if "what's the time" in query:
            self.tell_time(language)
            handled_command = True

        elif "open vscode" in query.lower():
            self.open_application("code", "VSCode", language)
            handled_command = True

        elif "open slack" in query.lower():
            self.open_application("Slack", "Slack", language)
            handled_command = True

        elif "play music" in query.lower():
            self.play_music(language)
            handled_command = True

        elif "open chrome" in query.lower():
            self.open_application("start chrome", "Chrome", language)
            handled_command = True

        elif "using youtube" in query.lower():
            self.handle_youtube_search(query, language)
            handled_command = True

        elif "aria quit" in query.lower():
            self.quit_application(language)
            handled_command = True

        elif "reset chat" in query.lower():
            self.output_area.insert(tk.END, "Chat reset.\n")
            handled_command = True

        if not handled_command:
            response = asyncio.run(chat(query, language, self.display_response))  # Pass display_response here

    def display_response(self, response_text):
        """Function to update the GUI with the AI response."""
        self.output_area.insert(tk.END, f"Aria: {response_text}\n")
        self.output_area.see(tk.END)  # Scroll to the end

    def tell_time(self, language):
        hour = datetime.datetime.now().strftime("%H")
        minute = datetime.datetime.now().strftime("%M")
        time_message = f"Sir, the time is {hour} hours and {minute} minutes." if language == "en" else f"साहब, समय {hour} घंटे और {minute} मिनट है।"
        self.output_area.insert(tk.END, f"Aria: {time_message}\n")
        speak(time_message, language)

    def open_application(self, command, app_name, language):
        if language == "hi":
            speak(f"{app_name} खोल रही हूँ...", "hi")
        else:
            speak(f"Opening {app_name}...", "en")
        os.system(command)
        self.output_area.insert(tk.END, f"Opening {app_name}...\n")

    def play_music(self, language):
        music_path = r"C:\Users\AnkitBalhara\Music\Dekha Tenu Pehli Pehli Baar Ve_320(PagalWorld.com.sb).mp3"
        os.system(f'start wmplayer "{music_path}"')
        if language == "hi":
            speak("आपका गाना बजा रही हूँ, सर...", "hi")
        else:
            speak("Playing your song, Sir...", "en")
        self.output_area.insert(tk.END, "Playing your song...\n")

    def quit_application(self, language):
        if language == "hi":
            speak("Aria बंद हो गई। Aria का उपयोग करने के लिए धन्यवाद।", "hi")
        else:
            speak("Aria Quit. Thanks for trying Aria.", "en")
        self.output_area.insert(tk.END, "Quitting Aria...\n")
        self.root.quit()

    def handle_youtube_search(self, query, language):
        search_terms = query.lower().replace("using youtube", "").strip()
        videos = search_youtube(search_terms)
        if videos:
            self.videos = videos  # Store the videos in a class variable
            self.expecting_video_choice = True  # Set state to expect a video choice

            if language == "hi":
                speak(f"आपकी खोज {search_terms} के आधार पर यहां शीर्ष 5 परिणाम हैं।", "hi")
                speak("कृपया बताएं कि मैं कौन सा वीडियो चलाूँ।", "hi")
            else:
                speak(f"Based on your search {search_terms}, here are the top 5 results.", "en")
                speak("Please select which one to play.", "en")

            self.output_area.insert(tk.END, f"Top results for {search_terms}:\n")
            for idx, (title, url) in enumerate(videos):
                self.output_area.insert(tk.END, f"{idx + 1}: {title}\n")
            self.output_area.insert(tk.END, "Please type the number of the video to play and press Enter.\n")
            self.output_area.see(tk.END)

        else:
            if language == "hi":
                speak("कोई वीडियो नहीं मिला।", "hi")
            else:
                speak("No videos found.", "en")
            self.output_area.insert(tk.END, "No videos found.\n")
            self.output_area.see(tk.END)

    def handle_video_choice(self, query):
        try:
            choice = int(query) - 1  # Get the user's choice
            if 0 <= choice < len(self.videos):  # Validate the choice
                video_title, video_url = self.videos[choice]  # Get the selected video
                language = self.language_var.get()
                if language == "hi":
                    speak(f"{video_title} वीडियो चला रही हूँ।", "hi")
                else:
                    speak(f"Playing the video: {video_title}.", "en")
                webbrowser.open(video_url)  # Open the video URL
                self.output_area.insert(tk.END, f"Playing the video: {video_title}...\n")

                # Clear the input field and reset state
                self.text_input.delete(0, tk.END)
                self.expecting_video_choice = False  # Reset state
                self.videos = []  # Clear the video list

            else:
                messagebox.showerror("Error", "Invalid choice. Please enter a valid number corresponding to the video.")
                self.text_input.delete(0, tk.END)  # Clear invalid input

        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please enter a number.")
            self.text_input.delete(0, tk.END)  # Clear invalid input

        finally:
            self.output_area.see(tk.END)  # Scroll to the end


if __name__ == "__main__":
    root = tk.Tk()
    aria_gui = AriaGUI(root)
    root.mainloop()
