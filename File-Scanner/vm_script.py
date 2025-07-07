# run_sandbox_final.py - The simple, reliable host controller.

import os
import subprocess
import time
import shutil

# --- CONFIGURATION (Ensure these are correct for your PC) ---
VBOXMANAGE_PATH = r"D:\virutalBOX\VBoxManage.exe"
VM_NAME = "Win81_Analysis_64bit"
SNAPSHOT_NAME = "clean_state_64"
SHARED_FOLDER_PATH = r"D:\YEAR4-SECurity\grad\VM_Share"
RESULTS_FOLDER = r"C:\Sandbox_Reports"
EXE_TASK_NAME = "sample.exe"
DLL_TASK_NAME = "sample.dll"

def run_full_analysis(path_to_malware_sample):
    """Orchestrates the analysis from a clean, powered-off state every time."""
    print("--- SIMPLE AND RELIABLE SANDBOX CONTROLLER ---")
    if not os.path.exists(path_to_malware_sample): return

    is_dll = path_to_malware_sample.lower().endswith('.dll')
    task_name_in_vm = DLL_TASK_NAME if is_dll else EXE_TASK_NAME
    shared_task_path = os.path.join(SHARED_FOLDER_PATH, task_name_in_vm)
    print(f"[INFO] Detected sample type: {'DLL' if is_dll else 'EXE'}")
    
    try:
        # STEP 1: Place file in share BEFORE booting
        print("[1] Preparing analysis task...")
        for item in os.listdir(SHARED_FOLDER_PATH):
            full_item_path = os.path.join(SHARED_FOLDER_PATH, item)
            if os.path.isfile(full_item_path): os.remove(full_item_path)
        shutil.copy(path_to_malware_sample, shared_task_path)
        print(f"  Sample placed as '{task_name_in_vm}'.")

        # STEP 2: Start the VM
        print(f"[2] Starting VM '{VM_NAME}' to begin analysis...")
        subprocess.run([VBOXMANAGE_PATH, "startvm", VM_NAME, "--type", "headless"], check=True)

        # STEP 3: Wait for completion signal
        print("[3] Waiting for completion signal from VM...")
        timeout = 240  # 4 minute timeout for safety
        start_time = time.time()
        analysis_complete = False
        while time.time() - start_time < timeout:
            if not os.path.exists(shared_task_path):
                print("  Signal received: Analysis complete.")
                analysis_complete = True
                break
            time.sleep(5)
        
        if not analysis_complete: print("  Timeout reached.")

        # STEP 4: Collect results
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
        # STEP 5: Always shut down and revert
        print("[5] Shutting down and reverting VM to clean state...")
        subprocess.run([VBOXMANAGE_PATH, "controlvm", VM_NAME, "poweroff"], capture_output=True)
        time.sleep(5)
        subprocess.run([VBOXMANAGE_PATH, "snapshot", VM_NAME, "restore", SNAPSHOT_NAME], check=True)
        print("\n--- AUTOMATION CYCLE COMPLETE ---")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2: print("Usage: python script.py <path_to_sample>")
    else: run_full_analysis(sys.argv[1])