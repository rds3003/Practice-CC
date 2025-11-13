import subprocess
import sys
import os
import getpass

# --------------------------------------------------------------------
# --- DEFINE YOUR "ALLOW LIST" HERE ---
#
# Add every account you want to REMAIN ENABLED to this list.
#
# WARNING: If you do not add your own account, you will be locked out!
# --------------------------------------------------------------------
USERS_TO_KEEP = [
    "YourMainUser",
    "AnotherAdmin",
    "ServiceAccount1"
]
# --------------------------------------------------------------------


def check_admin():
    """Returns True if the script is running with admin privileges, False otherwise."""
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

def get_current_user():
    """Gets the username of the user running the script."""
    return getpass.getuser()

def get_all_enabled_users():
    """
    Uses PowerShell to get a list of all local user accounts that are
    currently enabled. Returns a list of usernames.
    """
    print("[*] Fetching all currently enabled user accounts...")
    
    # PowerShell command to get names of enabled users
    command = [
        "powershell", 
        "-NoProfile", 
        "-Command", 
        "Get-LocalUser | Where-Object { $_.Enabled -eq $true } | Select-Object -ExpandProperty Name"
    ]
    
    try:
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=True, 
            shell=True # shell=True is simpler for this call
        )
        
        # Split the output into a list of names
        user_list = result.stdout.strip().splitlines()
        print(f"    ...Found {len(user_list)} enabled users.")
        return [user.strip() for user in user_list if user.strip()]
        
    except subprocess.CalledProcessError as e:
        print(f"  [ERROR] Failed to get user list via PowerShell: {e.stderr}")
        return None
    except FileNotFoundError:
        print("  [ERROR] 'powershell' command not found. This script requires PowerShell.")
        return None

def disable_user(username):
    """
    Disables a single user account using 'net user'.
    """
    print(f"  [DISABLING] Attempting to disable: {username}")
    command = ["net", "user", username, "/active:no"]
    
    try:
        subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            check=True, 
            shell=False
        )
        print(f"    [SUCCESS] User {username} has been disabled.")
        
    except subprocess.CalledProcessError as e:
        print(f"    [ERROR] Failed to disable user {username}: {e.stderr.strip()}")

# --- Main Script Execution ---
if __name__ == "__main__":
    
    if sys.platform != "win32":
        print("This script is designed for Windows.")
        sys.exit(1)
        
    if not check_admin():
        print("="*50)
        print("ERROR: This script must be run as an Administrator.")
        print("Please re-run in an elevated CMD or PowerShell window.")
        print("="*50)
        sys.exit(1)

    print("--- Starting User Account Hardening Script ---")
    
    # --- Create the final, safe "Allow List" ---
    # We use a set for fast, case-insensitive lookups.
    
    # 1. Add users from the configured list
    final_allow_list = {user.lower() for user in USERS_TO_KEEP}
    
    # 2. (SAFETY NET) Automatically add the user running the script
    current_user = get_current_user()
    if current_user.lower() not in final_allow_list:
        print(f"[INFO] SAFETY: Automatically adding current user '{current_user}' to the allow list.")
        final_allow_list.add(current_user.lower())
        
    # 3. (SAFETY NET) Automatically add critical system accounts
    # These are often disabled by default, but we should never try to disable them.
    system_accounts = ["administrator", "guest", "defaultaccount", "wdagutilityaccount"]
    final_allow_list.update(system_accounts)

    print("\n--- Final 'Allow List' (Accounts that will be KEPT enabled) ---")
    for user in sorted(list(final_allow_list)):
        print(f"  - {user}")
    print("---------------------------------------------------------------")
    
    # Get all currently enabled users
    all_enabled_users = get_all_enabled_users()
    
    if all_enabled_users is None:
        print("\nCould not fetch user list. Exiting script to be safe.")
        sys.exit(1)
        
    if not all_enabled_users:
        print("\nNo enabled users were found (this is unusual). Exiting.")
        sys.exit(0)
        
    print("\n--- Processing Accounts ---")
    disable_count = 0
    for username in all_enabled_users:
        if username.lower() in final_allow_list:
            print(f"[KEEPING] User '{username}' is on the allow list.")
        else:
            # This user is enabled, but NOT on our allow list. Disable it.
            disable_user(username)
            disable_count += 1
            
    print("-------------------------")
    print(f"\nScript complete. Disabled {disable_count} non-approved user account(s).")
