from pynput import keyboard
import time
from datetime import datetime

class KeystrokeLogger:
    def __init__(self):
        self.logging = False
        self.last_time = None
        self.log_file = f"clicks.txt"
        
    def start_logging(self):
        """Start logging keystrokes"""
        if not self.logging:
            self.logging = True
            self.last_time = time.time()
            print(f"Keystroke logging started. Saving to: {self.log_file}")
            with open(self.log_file, 'a') as f: #buffer log
                f.write(f"{'z'}\n")

    def stop_logging(self):
        """Stop logging keystrokes"""
        if self.logging:
            self.logging = False
            print("Keystroke logging stopped.")

    def log_key(self, key):
        """Log a keystroke with timing"""
        if self.logging:
            current_time = time.time()
            
            # Get key name
            try:
                key_name = key.char
            except AttributeError:
                # Special keys (ctrl, alt, etc.)
                key_name = str(key).replace('Key.', '')
            
            # Skip logging the control keys z and d
            if key_name in ['z', 'd']:
                return
            
            # Calculate time gap from last keystroke
            if self.last_time is not None:
                time_gap = round(current_time - self.last_time, 2)-0.009
                # Write time gap first
                with open(self.log_file, 'a') as f:
                    f.write(f"{time_gap}\n")
            
            # Write the key
            with open(self.log_file, 'a') as f:
                f.write(f"{key_name}\n")
            
            self.last_time = current_time
    
    def on_key_press(self, key):
        """Handle key press events"""
        try:
            if key.char == 'z':
                self.start_logging()
            elif key.char == 'd':
                self.stop_logging()
            else:
                self.log_key(key)
        except AttributeError:
            # Special keys - still log them if logging is active
            self.log_key(key)

def main():
    logger = KeystrokeLogger()
    
    print("Personal Keystroke Logger (macOS compatible)")
    print("Press 'z' to start logging")
    print("Press 'd' to stop logging")
    print("Press 'Ctrl+C' to exit")
    
    # Set up the keyboard listener
    listener = keyboard.Listener(on_press=logger.on_key_press)
    listener.start()
    
    try:
        # Keep the program running
        listener.join()
    except KeyboardInterrupt:
        print("\nExiting...")
        logger.stop_logging()
        listener.stop()

if __name__ == "__main__":
    main()