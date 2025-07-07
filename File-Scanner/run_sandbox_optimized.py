# run_sandbox_final_simple.py - The definitive simple and reliable host script.

import os
import subprocess
import time
import shutil
import re

# --- CONFIGURATION (Your paths and names are preserved) ---
VBOXMANAGE_PATH = r"C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
VM_NAME = "Win81_Analysis_64bit"
SNAPSHOT_NAME = "clean_state" # IMPORTANT: Make sure this matches your 64-bit snapshot name (e.g., "clean_state_64")
SHARED_FOLDER_PATH = r"C:\file_backend\grad\VM_Share"
RESULTS_FOLDER = r"C:\Sandbox\Reports" 
# Adding the DLL task name back in to support your dual-mode VM script
EXE_TASK_NAME = "sample.exe"
DLL_TASK_NAME = "sample.dll"

# The "get_vm_state" and "ensure_vm_is_ready" functions are no longer needed for this simpler logic.

def cleanup_and_revert_vm():
    """
    This is the simple cleanup logic. It only powers off and reverts.
    It does NOT restart the VM, leaving it off for the next run.
    """
    print("[CLEANUP] Preparing VM for the next run...")
    try:
        print("  - Powering off the VM...")
        subprocess.run([VBOXMANAGE_PATH, "controlvm", VM_NAME, "poweroff"], capture_output=True, timeout=60)
        time.sleep(5) # Give it a moment to power off fully

        print("  - Reverting to the clean snapshot...")
        subprocess.run([VBOXMANAGE_PATH, "snapshot", VM_NAME, "restore", SNAPSHOT_NAME], check=True)
        print("  VM is now powered off and in a clean state.")

    except subprocess.CalledProcessError as e:
        print(f"  ERROR during cleanup: {e}")
        pass

def run_full_analysis(path_to_malware_sample):
    """The main orchestration script using the simple run-once method."""
    print("--- SIMPLE AND RELIABLE SANDBOX CONTROLLER ---")

    if not os.path.exists(path_to_malware_sample):
        print(f"ERROR: Sample not found at '{path_to_malware_sample}'")
        return
        
    # Determine file type and set the correct task name for the VM
    is_dll = path_to_malware_sample.lower().endswith('.dll')
    task_name_in_vm = DLL_TASK_NAME if is_dll else EXE_TASK_NAME
    shared_task_path = os.path.join(SHARED_FOLDER_PATH, task_name_in_vm)
    
    try:
        # --- 1. Prepare the Task BEFORE starting the VM ---
        print(f"[1] Preparing analysis task for {os.path.basename(path_to_malware_sample)}...")
        # Clean the shared folder
        for item in os.listdir(SHARED_FOLDER_PATH):
            if os.path.isfile(os.path.join(SHARED_FOLDER_PATH, item)):
                os.remove(os.path.join(SHARED_FOLDER_PATH, item))
        # Place the new sample
        shutil.copy(path_to_malware_sample, shared_task_path)
        print(f"  Sample placed as '{task_name_in_vm}'.")
        
        # --- 2. Start the VM ---
        # It will boot and find the file waiting for it.
        print(f"[2] Starting VM '{VM_NAME}' to begin analysis...")
        subprocess.run([VBOXMANAGE_PATH, "startvm", VM_NAME, "--type", "headless"], check=True)
        
        # --- 3. Wait for the completion signal ---
        print("[3] Waiting for completion signal from VM...")
        timeout = 240 # 4 minutes
        start_time = time.time()
        analysis_complete = False
        while time.time() - start_time < timeout:
            if not os.path.exists(shared_task_path):
                print("  Signal received: Analysis complete.")
                analysis_complete = True
                break
            time.sleep(5)
        
        if not analysis_complete:
            print("  Timeout reached.")

        # --- 4. Collect results ---
        if analysis_complete:
            print("[4] Collecting results...")
            sample_name = os.path.basename(path_to_malware_sample)
            destination_folder = os.path.join(RESULTS_FOLDER, f"{sample_name}_{int(time.time())}")
            os.makedirs(destination_folder, exist_ok=True)
            
            items_found = 0
            for item in os.listdir(SHARED_FOLDER_PATH):
                if item.lower() != "system volume information":
                    shutil.move(os.path.join(SHARED_FOLDER_PATH, item), os.path.join(destination_folder, item))
                    items_found += 1
            print(f"  Success! Moved {items_found} result file(s) to: {destination_folder}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # --- 5. Always run the simple cleanup procedure ---
        cleanup_and_revert_vm()
        print("\n--- CYCLE COMPLETE ---")

# This main function is preserved exactly as you requested.
def main(file):
    if not file:
        return
    run_full_analysis(file)

# The example call from your script is also preserved.
#main(r"C:\hagat flashet asem\SysinternalsSuite\AccessEnum.exe")