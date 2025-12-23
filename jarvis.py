#!/usr/bin/env python3
"""
Jarvis Assistant for macOS
Version: 2.1.0
Author: its4yus4
License: MIT
GitHub: https://github.com/its4yus4/jarvis-assistant
"""

import sys
import os
import json
import time
import re
import subprocess
import argparse
import threading
from datetime import datetime
from pathlib import Path

# Third-party imports
try:
    import speech_recognition as sr
    import pyttsx3
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

# ASCII Banner
BANNER = f"""{Fore.CYAN}
    ╔{'═' * 58}╗
    ║{' ' * 58}║
    ║{Fore.YELLOW}      ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗     {Fore.CYAN}║
    ║{Fore.YELLOW}      ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝     {Fore.CYAN}║
    ║{Fore.YELLOW}      ██║███████║██████╔╝██║   ██║██║███████╗     {Fore.CYAN}║
    ║{Fore.YELLOW} ██   ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║     {Fore.CYAN}║
    ║{Fore.YELLOW} ╚█████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║     {Fore.CYAN}║
    ║{Fore.YELLOW}  ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝     {Fore.CYAN}║
    ║{' ' * 58}║
    ║{Fore.GREEN}      Just A Rather Very Intelligent System      {Fore.CYAN}║
    ║{' ' * 58}║
    ║{Fore.MAGENTA}         macOS Assistant • Version 2.1.0          {Fore.CYAN}║
    ║{Fore.MAGENTA}           GitHub: @its4yus4                    {Fore.CYAN}║
    ║{Fore.MAGENTA}           License: MIT                         {Fore.CYAN}║
    ║{' ' * 58}║
    ╚{'═' * 58}╝
{Style.RESET_ALL}"""

class JarvisAssistant:
    """Main Jarvis Assistant Class"""
    
    def __init__(self, debug=False, log_file=None):
        self.debug = debug
        self.version = "2.1.0"
        self.author = "its4yus4"
        self.license = "MIT"
        
        # Initialize logging
        self.setup_logging(log_file)
        
        # Print banner
        self.print_banner()
        
        # Create necessary directories
        self.setup_directories()
        
        # Initialize components
        self.recognizer = sr.Recognizer()
        self.engine = self.init_tts()
        
        # Load configurations
        self.config = self.load_config('config.json', self.default_config())
        self.apps_config = self.load_config('apps_config.json', self.default_apps_config())
        
        # Set wake word
        self.wake_word = self.config.get('wake_word', 'hey jarvis').lower()
        self.quit_commands = ['quit', 'exit', 'goodbye', 'stop', 'shutdown', 'close']
        
        # State variables
        self.is_active = True
        self.listening = False
        
        # Print initialization info
        self.print_info()
        
        # Speak welcome message
        self.speak(f"Jarvis initialized. Say '{self.wake_word}' to begin.")
    
    def setup_logging(self, log_file):
        """Setup logging configuration"""
        import logging
        
        if log_file is None:
            log_file = 'logs/jarvis.log'
        
        self.logger = logging.getLogger('Jarvis')
        self.logger.setLevel(logging.DEBUG if self.debug else logging.INFO)
        
        # File handler
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def setup_directories(self):
        """Create necessary directories"""
        directories = ['logs', 'images', 'examples']
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
    
    def print_banner(self):
        """Print the ASCII banner"""
        print(BANNER)
    
    def print_info(self):
        """Print system information"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}🤖 Jarvis Assistant v{self.version}")
        print(f"{Fore.GREEN}👤 Author: {self.author}")
        print(f"{Fore.BLUE}📄 License: {self.license}")
        print(f"{Fore.MAGENTA}🎤 Wake Word: '{self.wake_word}'")
        print(f"{Fore.CYAN}💻 System: macOS {self.get_macos_version()}")
        print(f"{Fore.BLUE}📁 Logs: logs/jarvis.log")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    def get_macos_version(self):
        """Get macOS version"""
        try:
            result = subprocess.run(['sw_vers', '-productVersion'], 
                                  capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except:
            return "Unknown"
    
    def init_tts(self):
        """Initialize text-to-speech engine"""
        try:
            engine = pyttsx3.init()
            
            # Get available voices
            voices = engine.getProperty('voices')
            
            # Prefer Daniel voice (British English, sounds like Jarvis)
            preferred = ['daniel', 'alex', 'samantha']
            for voice in voices:
                for pref in preferred:
                    if pref in voice.name.lower():
                        engine.setProperty('voice', voice.id)
                        self.logger.info(f"Using voice: {voice.name}")
                        break
                if engine.getProperty('voice'):
                    break
            
            # Set properties
            engine.setProperty('rate', 185)  # Speech speed
            engine.setProperty('volume', 0.95)  # Volume
            
            return engine
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS: {e}")
            return None
    
    def load_config(self, filename, default_config):
        """Load configuration from file or create default"""
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    config = json.load(f)
                self.logger.info(f"Loaded config from {filename}")
                return config
            except json.JSONDecodeError as e:
                self.logger.error(f"Error reading {filename}: {e}")
                return default_config
        else:
            # Create default config file
            with open(filename, 'w') as f:
                json.dump(default_config, f, indent=4)
            self.logger.info(f"Created default {filename}")
            return default_config
    
    def default_config(self):
        """Return default configuration"""
        return {
            "wake_word": "hey jarvis",
            "listen_timeout": 7,
            "phrase_time_limit": 8,
            "energy_threshold": 300,
            "dynamic_energy_threshold": True,
            "pause_threshold": 0.8,
            "ambient_adjust_duration": 0.5,
            "voice_rate": 185,
            "voice_volume": 0.95,
            "log_level": "INFO",
            "auto_start": False,
            "notifications": True,
            "beep_on_wake": True,
            "license": "MIT"
        }
    
    def default_apps_config(self):
        """Return default applications configuration"""
        return {
            "applications": {
                "chrome": {
                    "path": "/Applications/Google Chrome.app",
                    "commands": ["chrome", "browser", "google", "web"]
                },
                "safari": {
                    "path": "/Applications/Safari.app",
                    "commands": ["safari", "apple browser"]
                },
                "firefox": {
                    "path": "/Applications/Firefox.app",
                    "commands": ["firefox", "mozilla"]
                },
                "terminal": {
                    "path": "/System/Applications/Utilities/Terminal.app",
                    "commands": ["terminal", "command line", "bash", "shell"]
                },
                "notes": {
                    "path": "/System/Applications/Notes.app",
                    "commands": ["notes", "note taking"]
                },
                "calculator": {
                    "path": "/System/Applications/Calculator.app",
                    "commands": ["calculator", "calc"]
                },
                "calendar": {
                    "path": "/System/Applications/Calendar.app",
                    "commands": ["calendar", "schedule"]
                },
                "spotify": {
                    "path": "/Applications/Spotify.app",
                    "commands": ["spotify", "music", "play music"]
                },
                "vscode": {
                    "path": "/Applications/Visual Studio Code.app",
                    "commands": ["code", "visual studio code", "editor"]
                },
                "messages": {
                    "path": "/System/Applications/Messages.app",
                    "commands": ["messages", "imessage", "text"]
                },
                "mail": {
                    "path": "/System/Applications/Mail.app",
                    "commands": ["mail", "email"]
                },
                "facetime": {
                    "path": "/System/Applications/FaceTime.app",
                    "commands": ["facetime", "video call"]
                },
                "photos": {
                    "path": "/System/Applications/Photos.app",
                    "commands": ["photos", "pictures"]
                }
            },
            "system_commands": {
                "lock_screen": "pmset displaysleepnow",
                "screenshot": "screencapture ~/Desktop/Screenshot_$(date +%Y%m%d_%H%M%S).png",
                "show_desktop": """
                    osascript -e 'tell application "System Events"
                        key code 103 using {command down}
                    end tell'
                """,
                "volume_up": """
                    osascript -e 'set volume output volume (output volume of (get volume settings) + 15)'
                """,
                "volume_down": """
                    osascript -e 'set volume output volume (output volume of (get volume settings) - 15)'
                """,
                "mute": "osascript -e 'set volume output volume 0'",
                "max_volume": "osascript -e 'set volume output volume 100'"
            }
        }
    
    def speak(self, text, wait=True):
        """Convert text to speech"""
        print(f"{Fore.CYAN}🤖 Jarvis:{Style.RESET_ALL} {text}")
        self.logger.info(f"Speaking: {text}")
        
        if self.engine:
            try:
                self.engine.say(text)
                if wait:
                    self.engine.runAndWait()
            except Exception as e:
                self.logger.error(f"TTS Error: {e}")
    
    def listen(self, listen_type="command"):
        """Listen for audio input"""
        try:
            # Configure recognizer
            self.recognizer.energy_threshold = self.config.get('energy_threshold', 300)
            self.recognizer.dynamic_energy_threshold = self.config.get('dynamic_energy_threshold', True)
            self.recognizer.pause_threshold = self.config.get('pause_threshold', 0.8)
            
            with sr.Microphone() as source:
                # Adjust for ambient noise
                adjust_duration = self.config.get('ambient_adjust_duration', 0.5)
                self.recognizer.adjust_for_ambient_noise(source, duration=adjust_duration)
                
                # Set timeout based on listen type
                if listen_type == "wake_word":
                    print(f"{Fore.YELLOW}👂 Listening for '{self.wake_word}'...{Style.RESET_ALL}")
                    timeout = 3
                    phrase_limit = 3
                else:
                    print(f"{Fore.GREEN}🎤 Speak your command...{Style.RESET_ALL}")
                    timeout = self.config.get('listen_timeout', 7)
                    phrase_limit = self.config.get('phrase_time_limit', 8)
                
                try:
                    # Listen for audio
                    audio = self.recognizer.listen(
                        source, 
                        timeout=timeout,
                        phrase_time_limit=phrase_limit
                    )
                    
                    # Recognize speech
                    text = self.recognizer.recognize_google(audio).lower()
                    self.logger.info(f"Recognized: {text}")
                    
                    return text
                    
                except sr.WaitTimeoutError:
                    if listen_type == "wake_word":
                        print(f"{Fore.YELLOW}⏳ No wake word detected{Style.RESET_ALL}", end='\r')
                    else:
                        print(f"{Fore.YELLOW}⏳ No command detected{Style.RESET_ALL}")
                    return None
                    
                except sr.UnknownValueError:
                    print(f"{Fore.RED}❓ Could not understand audio{Style.RESET_ALL}")
                    return None
                    
                except sr.RequestError as e:
                    print(f"{Fore.RED}🌐 Network error: {e}{Style.RESET_ALL}")
                    return None
                    
        except OSError as e:
            print(f"{Fore.RED}🎤 Microphone error: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Please check microphone permissions in System Preferences{Style.RESET_ALL}")
            return None
        except Exception as e:
            self.logger.error(f"Listen error: {e}")
            return None
    
    def open_application(self, app_name):
        """Open an application"""
        app_name = app_name.lower().strip()
        
        # Remove command words
        for word in ['open', 'launch', 'start', 'run']:
            if app_name.startswith(word + ' '):
                app_name = app_name[len(word)+1:]
        
        self.logger.info(f"Opening application: {app_name}")
        
        # Search in configured applications
        for app_key, app_data in self.apps_config.get('applications', {}).items():
            # Check app_key
            if app_name == app_key:
                return self.launch_app(app_key, app_data['path'])
            
            # Check commands
            for cmd in app_data.get('commands', []):
                if app_name == cmd:
                    return self.launch_app(app_key, app_data['path'])
            
            # Check partial matches
            if app_name in app_key or any(app_name in cmd for cmd in app_data.get('commands', [])):
                return self.launch_app(app_key, app_data['path'])
        
        # Try to open using Spotlight
        return self.launch_via_spotlight(app_name)
    
    def launch_app(self, app_name, app_path):
        """Launch application by path"""
        if os.path.exists(app_path):
            try:
                self.speak(f"Opening {app_name.replace('_', ' ')}")
                subprocess.Popen(['open', app_path], 
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
                return True
            except Exception as e:
                self.speak(f"Failed to open {app_name}")
                self.logger.error(f"Launch error: {e}")
                return False
        else:
            self.speak(f"{app_name} not found at {app_path}")
            return False
    
    def launch_via_spotlight(self, app_name):
        """Launch application using Spotlight"""
        try:
            self.speak(f"Trying to open {app_name}")
            
            # Try without .app extension
            result = subprocess.run(['open', '-a', app_name],
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                return True
            
            # Try with .app extension
            result = subprocess.run(['open', '-a', f"{app_name}.app"],
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                return True
            
            self.speak(f"Sorry, I couldn't find {app_name}")
            return False
            
        except Exception as e:
            self.logger.error(f"Spotlight launch error: {e}")
            self.speak(f"Error opening {app_name}")
            return False
    
    def execute_system_command(self, command):
        """Execute system command"""
        system_cmds = self.apps_config.get('system_commands', {})
        
        for cmd_key, cmd_value in system_cmds.items():
            if command in cmd_key:
                try:
                    action_name = cmd_key.replace('_', ' ')
                    self.speak(f"Executing {action_name}")
                    
                    subprocess.run(cmd_value, shell=True, check=True,
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
                    return True
                except subprocess.CalledProcessError as e:
                    self.speak(f"Failed to execute {cmd_key}")
                    self.logger.error(f"Command error: {e}")
                    return False
        
        return False
    
    def process_command(self, command_text):
        """Process voice command"""
        if not command_text:
            return True
        
        original_text = command_text
        command_text = command_text.lower().strip()
        
        # Remove wake word if present
        command_text = command_text.replace(self.wake_word, '').strip()
        
        self.logger.info(f"Processing command: {original_text}")
        
        # Check for quit commands
        if any(cmd in original_text for cmd in self.quit_commands):
            self.speak("Goodbye! Shutting down.")
            return False
        
        # Check for license information
        if any(word in command_text for word in ['license', 'mit', 'open source']):
            self.speak("This project is licensed under the MIT License.")
            print(f"\n{Fore.CYAN}License:{Style.RESET_ALL} MIT")
            print(f"{Fore.CYAN}Details:{Style.RESET_ALL} See LICENSE file")
            return True
        
        # Check for application opening
        app_patterns = [
            r'open\s+(.+)',
            r'launch\s+(.+)',
            r'start\s+(.+)',
            r'run\s+(.+)'
        ]
        
        for pattern in app_patterns:
            match = re.search(pattern, command_text)
            if match:
                app_name = match.group(1)
                return self.open_application(app_name)
        
        # System commands
        if 'lock' in command_text or 'sleep' in command_text:
            return self.execute_system_command('lock_screen')
        elif 'screenshot' in command_text:
            return self.execute_system_command('screenshot')
        elif 'desktop' in command_text:
            return self.execute_system_command('show_desktop')
        elif any(word in command_text for word in ['volume up', 'louder', 'increase volume']):
            return self.execute_system_command('volume_up')
        elif any(word in command_text for word in ['volume down', 'quieter', 'decrease volume']):
            return self.execute_system_command('volume_down')
        elif 'mute' in command_text:
            return self.execute_system_command('mute')
        elif any(word in command_text for word in ['max volume', 'full volume', 'volume max']):
            return self.execute_system_command('max_volume')
        
        # Information queries
        elif 'time' in command_text:
            current_time = datetime.now().strftime('%I:%M %p')
            self.speak(f"The time is {current_time}")
            return True
        elif 'date' in command_text:
            current_date = datetime.now().strftime('%A, %B %d, %Y')
            self.speak(f"Today is {current_date}")
            return True
        elif 'day' in command_text:
            current_day = datetime.now().strftime('%A')
            self.speak(f"Today is {current_day}")
            return True
        
        # Conversational
        elif any(word in command_text for word in ['hello', 'hi ', 'hey ', 'greetings']):
            responses = [
                "Hello! How can I assist you?",
                "Hi there!",
                "Greetings!",
                "Hello! Ready to help."
            ]
            self.speak(responses[datetime.now().second % len(responses)])
            return True
        elif 'your name' in command_text:
            self.speak("I am Jarvis, your personal assistant.")
            return True
        elif 'who are you' in command_text:
            self.speak("I am J.A.R.V.I.S., Just A Rather Very Intelligent System.")
            return True
        elif 'how are you' in command_text:
            responses = [
                "I'm functioning optimally, thank you.",
                "All systems are operational.",
                "I'm well, thank you for asking.",
                "Running smoothly as always."
            ]
            self.speak(responses[datetime.now().second % len(responses)])
            return True
        elif any(word in command_text for word in ['thank', 'thanks']):
            responses = [
                "You're welcome!",
                "My pleasure.",
                "Happy to help!",
                "Anytime!"
            ]
            self.speak(responses[datetime.now().second % len(responses)])
            return True
        elif 'help' in command_text:
            self.show_help()
            return True
        
        # Default response
        else:
            self.speak(f"I'm not sure how to '{original_text}'. Try saying 'help'.")
            return True
    
    def show_help(self):
        """Show help information"""
        help_text = f"""
{Fore.CYAN}{'='*60}{Style.RESET_ALL}
{Fore.YELLOW}🎮 AVAILABLE COMMANDS{Style.RESET_ALL}
{Fore.CYAN}{'='*60}{Style.RESET_ALL}

{Fore.GREEN}📱 Applications:{Style.RESET_ALL}
  • "Open [application]" - Launch any app
  • Examples: "Open Chrome", "Launch Terminal"

{Fore.BLUE}⚙️ System Controls:{Style.RESET_ALL}
  • "Lock screen" - Lock your Mac
  • "Take screenshot" - Capture screen
  • "Show desktop" - Minimize all windows
  • "Volume up/down" - Adjust volume
  • "Mute" - Silence audio

{Fore.MAGENTA}📅 Information:{Style.RESET_ALL}
  • "What time is it?" - Current time
  • "What's today's date?" - Today's date
  • "What day is it?" - Day of week

{Fore.CYAN}💬 Conversation:{Style.RESET_ALL}
  • "Hello" - Greet Jarvis
  • "How are you?" - Check status
  • "Thank you" - Say thanks
  • "What's your name?" - Who am I

{Fore.YELLOW}📄 License:{Style.RESET_ALL}
  • "License" - Show license information

{Fore.RED}🛑 Control:{Style.RESET_ALL}
  • "Quit" or "Exit" - Shutdown Jarvis

{Fore.CYAN}{'='*60}{Style.RESET_ALL}
"""
        print(help_text)
        self.speak("Here are the available commands.")
    
    def wake_word_mode(self):
        """Run in wake word detection mode"""
        self.speak(f"Wake word mode activated. Say '{self.wake_word}' to begin.")
        print(f"\n{Fore.YELLOW}💤 Sleeping... Say '{self.wake_word}' to wake me up.{Style.RESET_ALL}\n")
        
        while self.is_active:
            try:
                # Listen for wake word
                text = self.listen("wake_word")
                
                if text and self.wake_word in text:
                    print(f"\n{Fore.GREEN}✅ Wake word detected!{Style.RESET_ALL}")
                    
                    # Beep sound
                    print('\a', end='', flush=True)
                    
                    # Listen for command
                    self.speak("Yes?")
                    command = self.listen("command")
                    
                    if command:
                        self.is_active = self.process_command(command)
                    
                    print(f"\n{Fore.YELLOW}💤 Returning to sleep...{Style.RESET_ALL}\n")
                
                # Small delay to prevent CPU overuse
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}🛑 Keyboard interrupt detected.{Style.RESET_ALL}")
                self.is_active = False
            except Exception as e:
                self.logger.error(f"Wake word loop error: {e}")
                time.sleep(1)
    
    def continuous_mode(self):
        """Run in continuous listening mode"""
        self.speak("Continuous mode activated. I'm always listening.")
        print(f"\n{Fore.GREEN}🎧 Always listening... Speak commands anytime.{Style.RESET_ALL}\n")
        
        while self.is_active:
            try:
                command = self.listen("command")
                
                if command:
                    self.is_active = self.process_command(command)
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}🛑 Keyboard interrupt detected.{Style.RESET_ALL}")
                self.is_active = False
            except Exception as e:
                self.logger.error(f"Continuous mode error: {e}")
                time.sleep(1)
    
    def manual_mode(self):
        """Run in manual input mode"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⌨️  MANUAL MODE{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Type commands or 'quit' to exit.{Style.RESET_ALL}\n")
        
        while self.is_active:
            try:
                command = input(f"{Fore.BLUE}Command > {Style.RESET_ALL}").strip()
                
                if not command:
                    continue
                
                if command.lower() in self.quit_commands:
                    print(f"{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
                    break
                
                self.process_command(command)
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
                break
            except EOFError:
                print(f"\n{Fore.YELLOW}👋 Goodbye!{Style.RESET_ALL}")
                break
    
    def test_mode(self):
        """Run system tests"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}🧪 TEST MODE{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        tests = [
            ("TTS Engine", self.test_tts),
            ("Microphone", self.test_microphone),
            ("Application Launch", self.test_app_launch),
            ("System Commands", self.test_system_commands),
            ("Speech Recognition", self.test_speech_recognition)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n{Fore.BLUE}Testing: {test_name}...{Style.RESET_ALL}")
            result = test_func()
            status = f"{Fore.GREEN}✓ PASS{Style.RESET_ALL}" if result else f"{Fore.RED}✗ FAIL{Style.RESET_ALL}"
            results.append((test_name, result, status))
            print(f"  Result: {status}")
        
        # Print summary
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}📊 TEST SUMMARY{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        passed = sum(1 for _, result, _ in results if result)
        total = len(results)
        
        for test_name, result, status in results:
            print(f"{status} {test_name}")
        
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Results: {passed}/{total} tests passed{Style.RESET_ALL}")
        
        if passed == total:
            print(f"{Fore.GREEN}✅ All systems operational!{Style.RESET_ALL}")
            self.speak("All tests passed. Systems are operational.")
        else:
            print(f"{Fore.YELLOW}⚠️  Some tests failed. Check logs for details.{Style.RESET_ALL}")
            self.speak(f"{passed} out of {total} tests passed.")
        
        input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
    
    def test_tts(self):
        """Test text-to-speech"""
        try:
            self.speak("Testing text to speech.")
            return True
        except:
            return False
    
    def test_microphone(self):
        """Test microphone"""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                return True
        except:
            return False
    
    def test_app_launch(self):
        """Test application launching"""
        try:
            # Test with a system app that should always exist
            subprocess.run(['open', '-a', 'Calculator'], 
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL,
                         timeout=2)
            time.sleep(1)
            subprocess.run(['pkill', 'Calculator'],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
            return True
        except:
            return False
    
    def test_system_commands(self):
        """Test system commands"""
        try:
            subprocess.run(['osascript', '-e', 'get volume settings'],
                         capture_output=True, timeout=2)
            return True
        except:
            return False
    
    def test_speech_recognition(self):
        """Test speech recognition"""
        try:
            # Just check if we can access the recognizer
            self.recognizer.recognize_google
            return True
        except:
            return False
    
    def run(self, mode='wake'):
        """Main run method"""
        modes = {
            'wake': self.wake_word_mode,
            'continuous': self.continuous_mode,
            'manual': self.manual_mode,
            'test': self.test_mode
        }
        
        if mode in modes:
            modes[mode]()
        else:
            print(f"{Fore.RED}Error: Unknown mode '{mode}'{Style.RESET_ALL}")
            print(f"Available modes: {', '.join(modes.keys())}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Jarvis Assistant - Voice-controlled macOS assistant',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  {sys.argv[0]} --mode wake      # Wake word mode (default)
  {sys.argv[0]} --mode continuous # Always listening
  {sys.argv[0]} --mode manual     # Type commands
  {sys.argv[0]} --mode test       # Run system tests
  {sys.argv[0]} --debug          # Enable debug mode
  {sys.argv[0]} --license        # Show license information
        """
    )
    
    parser.add_argument('--mode', '-m',
                       choices=['wake', 'continuous', 'manual', 'test'],
                       default='wake',
                       help='Operation mode (default: wake)')
    
    parser.add_argument('--debug', '-d',
                       action='store_true',
                       help='Enable debug logging')
    
    parser.add_argument('--log', '-l',
                       help='Log file path')
    
    parser.add_argument('--version', '-v',
                       action='version',
                       version='Jarvis Assistant v2.1.0 (MIT License)')
    
    parser.add_argument('--license', 
                       action='store_true',
                       help='Show license information')
    
    args = parser.parse_args()
    
    # Show license if requested
    if args.license:
        print(f"{Fore.CYAN}Jarvis Assistant - MIT License{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Copyright (c) 2024 its4yus4{Style.RESET_ALL}")
        print("\nPermission is hereby granted, free of charge, to any person obtaining a copy")
        print("of this software and associated documentation files (the 'Software'), to deal")
        print("in the Software without restriction, including without limitation the rights")
        print("to use, copy, modify, merge, publish, distribute, sublicense, and/or sell")
        print("copies of the Software, and to permit persons to whom the Software is")
        print("furnished to do so, subject to the following conditions:")
        print("\nThe above copyright notice and this permission notice shall be included in all")
        print("copies or substantial portions of the Software.")
        print("\nTHE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR")
        print("IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,")
        print("FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE")
        print("AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER")
        print("LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,")
        print("OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.")
        print(f"\n{Fore.GREEN}For full license text, see LICENSE file.{Style.RESET_ALL}")
        return
    
    try:
        # Create Jarvis instance
        jarvis = JarvisAssistant(debug=args.debug, log_file=args.log)
        
        # Run in selected mode
        jarvis.run(args.mode)
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Jarvis terminated by user.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}💥 Fatal error: {e}{Style.RESET_ALL}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
