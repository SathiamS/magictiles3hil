from pynput import keyboard
from pynput.keyboard import Key, Listener
import time
import threading

class KeystrokeReplayer:
    def __init__(self, file_path="clicks.txt"):
        self.file_path = file_path
        self.replaying = False
        self.replay_thread = None
        self.stop_replay = False
        self.keystrokes = []
        self.controller = keyboard.Controller()
        
    def load_keystrokes(self):
        """Load keystrokes and timing from the file"""
        try:
            with open(self.file_path, 'r') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            
            self.keystrokes = []
            i = 0
            
            # First entry might be a delay or a key
            if lines and not lines[0].replace('.', '').isdigit():
                # First line is a key, no initial delay
                self.keystrokes.append((0, lines[0]))
                i = 1
            elif lines and lines[0].replace('.', '').isdigit():
                # First line is a delay, skip it for now
                i = 1
            
            # Process pairs of (delay, key)
            while i < len(lines):
                if i + 1 < len(lines):
                    try:
                        delay = float(lines[i])
                        key = lines[i + 1]
                        self.keystrokes.append((delay, key))
                        i += 2
                    except ValueError:
                        # Skip invalid entries
                        i += 1
                else:
                    # Last line is just a key with no delay
                    if not lines[i].replace('.', '').isdigit():
                        self.keystrokes.append((0, lines[i]))
                    break
                    
            print(f"Loaded {len(self.keystrokes)} keystrokes from {self.file_path}")
            
        except FileNotFoundError:
            print(f"Error: {self.file_path} not found!")
            self.keystrokes = []
        except Exception as e:
            print(f"Error loading file: {e}")
            self.keystrokes = []
    
    def replay_keystrokes(self):
        """Replay the keystrokes with timing"""
        print("Starting keystroke replay...")
        keys_pressed = -1
        for delay, key in self.keystrokes:
            if self.stop_replay:
                print("Replay stopped by user")
                break
                
            # Wait for the specified delay
            if delay > 0:
                time.sleep(delay+0.002)
            
            # Check again after delay in case stop was pressed
            if self.stop_replay:
                print("Replay stopped by user")
                break
                
            # Press the key
            try:
                keys_pressed+=2
                self.controller.press(key)
                self.controller.release(key)
                print(f"Pressed: {key}, idx: {keys_pressed}")
            except Exception as e:
                print(f"Error pressing key '{key}': {e}")
        
        if not self.stop_replay:
            print("Replay completed")
        
        self.replaying = False
        self.stop_replay = False
    
    def start_replay(self):
        """Start replaying keystrokes"""
        if not self.replaying and self.keystrokes:
            self.replaying = True
            self.stop_replay = False
            self.replay_thread = threading.Thread(target=self.replay_keystrokes)
            self.replay_thread.daemon = True
            self.replay_thread.start()
        elif not self.keystrokes:
            print("No keystrokes loaded. Make sure clicks.txt exists and is properly formatted.")
        else:
            print("Already replaying keystrokes...")
    
    def stop_replay_now(self):
        """Stop the current replay"""
        if self.replaying:
            print("Stopping replay...")
            self.stop_replay = True
        else:
            print("No replay in progress")
    
    def on_key_press(self, key):
        """Handle key press events"""
        try:
            if key.char == 'z':
                print("'z' pressed - starting replay")
                self.start_replay()
            elif key.char == 'd':
                print("'d' pressed - stopping replay")
                self.stop_replay_now()
        except AttributeError:
            # Special keys (ctrl, alt, etc.) - ignore them
            pass

def main():
    replayer = KeystrokeReplayer()
    
    print("Keystroke Replayer")
    print("Loading keystrokes from clicks.txt...")
    replayer.load_keystrokes()
    
    if not replayer.keystrokes:
        print("No valid keystrokes found. Exiting.")
        return
    
    print("\nControls:")
    print("Press 'z' to start replaying keystrokes")
    print("Press 'd' to stop replay (even during execution)")
    print("Press 'Ctrl+C' to exit")
    print("\nReady...")
    
    # Set up the keyboard listener
    listener = Listener(on_press=replayer.on_key_press)
    listener.start()
    
    try:
        # Keep the program running
        listener.join()
    except KeyboardInterrupt:
        print("\nExiting...")
        replayer.stop_replay_now()
        listener.stop()

if __name__ == "__main__":
    main()