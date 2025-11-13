import subprocess
import sys
import os
import getpass
import ctypes

def check_admin():
    """Returns True if the script is running with admin privileges, False otherwise."""
    try:
        # Check for admin rights on Windows
        return os.getuid() == 0
    except AttributeError:
        # Fallback for non-Linux (Windows)
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def change_password(username, new_password):
    """
    Attempts to change the password for a single user.
    """
    print(f"\n[*] Attempting to change password for user: {username}")
    
    # The command to change a user's password.
    # We pass the username and password as separate arguments.
    command = ["net", "user", username, new_password]
    
    try:
        # Execute the command
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            shell=False
        )
        
        print(f"  [SUCCESS] Successfully changed password for user: {username}")
        # print(f"  Output: {result.stdout.strip()}") # Uncomment for more detail
        
    except subprocess.CalledProcessError as e:
        # This block runs if the command returns a non-zero (error) code
        print(f"  [ERROR] Failed to change password for user: {username}.")
        error_message = e.stderr.strip()
        if not error_message:
             error_message = e.stdout.strip() # 'net user' sometimes sends errors to stdout
        
        print(f"  Details: {error_message}")
        if "access is denied" in error_message.lower():
            print("  [HINT] This script must be run as an Administrator.")
        elif "complexity" in error_message.lower():
            print("  [HINT] The password does not meet the system's complexity requirements.")
            
    except FileNotFoundError:
        print("  [ERROR] 'net' command not found. This script must be run on Windows.")
    except Exception as e:
        print(f"  [ERROR] An unexpected error occurred: {e}")

# --- Main part of the script ---
if __name__ == "__main__":
    
    if sys.platform != "win32":
        print("This script is designed for Windows and uses the 'net user' command.")
        sys.exit(1)
    
    if not check_admin():
        print("="*40)
        print("WARNING: Script is NOT running with admin rights.")
        print("Please re-run this script in an Administrator shell.")
        print("="*40)
        sys.exit(1)
        
    print("--- Change Windows User Password ---")
    
    # 1. Get the username
    username = input("Enter the username: ").strip()
    
    if not username:
        print("No username entered. Exiting.")
        sys.exit(1)
        
    try:
        # 2. Get the new password (hidden)
        new_pass = getpass.getpass("Enter the new password: ")
        
        # 3. Confirm the new password (hidden)
        confirm_pass = getpass.getpass("Confirm the new password: ")
        
    except (EOFError, KeyboardInterrupt):
        print("\nPassword entry cancelled. Exiting.")
        sys.exit(1)

    # 4. Check if passwords match
    if new_pass != confirm_pass:
        print("\n[ERROR] Passwords do not match. Please try again.")
    elif not new_pass:
         print("\n[ERROR] Password cannot be empty. Exiting.")
    else:
        # 5. Run the function to change the password
        change_password(username, new_pass)
