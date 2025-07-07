--------------------------------------------------
README: Virtual Machine Setup Instructions
--------------------------------------------------

This guide provides the step-by-step instructions to create and configure
the Windows analysis Virtual Machine (VM) for our automated malware sandbox.
Follow these steps exactly to ensure the sandbox operates correctly.


--- [ Phase 1: Create and Install the Virtual Machine ] ---

1.  **Open VirtualBox** and click the "New" icon.
2.  **Configure Name and OS:**
    - Name: Win81_Analysis_64bit
    - ISO Image: Select your Windows 8.1 64-bit ISO file.
    - Version: Ensure it says "Windows 8.1 (64-bit)".
    - CRITICAL: Check the box "Skip Unattended Installation".
3.  **Configure Hardware:**
    - Base Memory (RAM): 4096 MB (for a 24GB+ host) or 2048 MB (for an 8GB host).
    - Processors: 2 CPUs (for a 24GB+ host) or 1 CPU (for an 8GB host).
4.  **Configure Hard Disk:**
    - Create a new virtual hard disk.
    - Set the size to at least 40 GB.
5.  **Install Windows:**
    - Start the new VM. It will boot from the ISO.
    - When asked for a product key, use the following generic key to proceed:
      334NH-RXG76-64THK-C7CKG-D3VPT
    - When asked for installation type, choose "Custom: Install Windows only (advanced)".
6.  **Set Up User Account:**
    - During setup, it will ask you to sign in with a Microsoft account.
    - Click the link that says "Sign in without a Microsoft account".
    - On the next screen, click the "Local account" button.
    - Username: User
    - Password: LEAVE THIS COMPLETELY BLANK.
    - Click "Finish".


--- [ Phase 2: Harden the VM for Analysis ] ---

This phase disables features that can interfere with malware analysis.

1.  **Customize Settings:**
    - When you see the "Express settings" screen, click the "Customize" button.
    - Go through the settings pages and turn OFF everything related to automatic updates, sending data to Microsoft, and error reporting.

2.  **Disable Security (In Control Panel):**
    - Open the Control Panel.
    - Turn off "Windows Firewall".
    - Change "User Account Control (UAC)" settings by dragging the slider to "Never notify".
    - Go to "Windows Update" and set it to "Never check for updates".

3.  **CRITICAL - Disable UAC in the Registry:**
    - This is the most important step to prevent elevation errors.
    - Open the Registry Editor by typing "regedit" in the Start search.
    - Navigate to the following path:
      HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System
    - In the right-hand pane, find the value named "EnableLUA".
    - Double-click "EnableLUA" and change its "Value data" from 1 to 0.
    - Click OK and close the Registry Editor.

4.  **Reboot the VM:** You MUST restart the VM for the registry change to take effect.


--- [ Phase 3: Install Tools and Software ] ---

1.  **Install Guest Additions:**
    - After the VM reboots, go to the VirtualBox menu: Devices -> Insert Guest Additions CD image...
    - Run the installer from the pop-up inside the VM. Reboot again when it finishes.

2.  **Install Python:**
    - Transfer the 64-bit Python installer (e.g., python-3.8.10-amd64.exe) into the VM.
    - Run the installer.
    - CRITICAL: On the first screen, CHECK THE BOX that says "Add Python 3.x to PATH".

3.  **Install `psutil`:**
    - Give the VM temporary internet access by changing its Network setting in VirtualBox to "NAT".
    - Open a Command Prompt (cmd) in the VM and run: pip install psutil
    - After it succeeds, change the VM's Network setting back to "Host-only Adapter".

4.  **Create Tools Folder:**
    - Inside the VM, navigate to the C:\ drive and create a folder named "Tools".
    - Copy your analysis tools (`procdump64.exe`, Sysinternals `strings.exe`) into C:\Tools.


--- [ Phase 4: Deploy and Schedule the Analysis Script ] ---

1.  **Place the Script:** Copy your final "run-once" VM script (e.g., `vm_script.py`) onto the VM's desktop.

2.  **Open Task Scheduler:** Search for and open "Task Scheduler" from the Start screen.

3.  **Create the Task:**
    - In the Actions pane, click "Create Task...".
    - **General Tab:**
        - Name: RunAnalysisOnBoot
        - Check the box "Run with highest privileges".
        - Configure for: Windows 8.1 (or Windows 10).
    - **Triggers Tab:**
        - Click "New..." and set "Begin the task:" to "At log on". Click OK.
    - **Actions Tab:**
        - Click "New...".
        - Program/script: C:\Python38\python.exe (or the correct path to your Python install).
        - Add arguments: C:\Users\User\Desktop\vm_analyzer.py (the path to your script).
        - Click OK.

4.  Click OK to save the task.


--- [ Phase 5: Finalize the Sandbox ] ---

1.  **Shut Down the VM:** The sandbox is now fully configured. Shut it down completely.

2.  **Take the "Golden" Snapshot:**
    - In the main VirtualBox window, select your VM.
    - Go to the Snapshots panel.
    - Delete any old snapshots to merge the changes.
    - Take a new snapshot and name it exactly clean_state_64 (or a name that matches your host script).


RUN "run_sandbox_optimized.py" FROM HOST MACHINE WHILE GIVING IT A PATH OF AN EXE TO BE ANALYZED 

--------------------------------------------------
SETUP COMPLETE: The VM is now a fully configured analysis agent.
--------------------------------------------------