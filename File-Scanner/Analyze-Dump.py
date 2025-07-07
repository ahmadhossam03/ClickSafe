import subprocess
import os
import re
from collections import Counter
import hashlib
import SignatureScan
import stringswork

def is_valid_public_ip(ip_str):
    """
    Check if an IP address is valid and public (not private, loopback, multicast, etc.)
    
    Args:
        ip_str: String representation of IP address
        
    Returns:
        bool: True if IP is valid and public, False otherwise
    """
    try:
        # Split IP into octets and validate format
        octets = ip_str.split('.')
        if len(octets) != 4:
            return False
        
        # Convert to integers and validate range
        ip_nums = []
        for octet in octets:
            num = int(octet)
            if num < 0 or num > 255:
                return False
            # Reject IPs with leading zeros (like 192.168.001.1)
            if len(octet) > 1 and octet[0] == '0':
                return False
            ip_nums.append(num)
        
        # Filter out private, reserved, and special-use IP ranges
        first_octet = ip_nums[0]
        second_octet = ip_nums[1]
        
        # 0.0.0.0/8 - Current network (only valid as source)
        if first_octet == 0:
            return False
            
        # 10.0.0.0/8 - Private network
        if first_octet == 10:
            return False
            
        # 127.0.0.0/8 - Loopback
        if first_octet == 127:
            return False
            
        # 169.254.0.0/16 - Link-local
        if first_octet == 169 and second_octet == 254:
            return False
            
        # 172.16.0.0/12 - Private network
        if first_octet == 172 and 16 <= second_octet <= 31:
            return False
            
        # 192.168.0.0/16 - Private network
        if first_octet == 192 and second_octet == 168:
            return False
            
        # 224.0.0.0/4 - Multicast
        if first_octet >= 224 and first_octet <= 239:
            return False
            
        # 240.0.0.0/4 - Reserved for future use
        if first_octet >= 240:
            return False
            
        # 255.255.255.255 - Broadcast
        if ip_str == "255.255.255.255":
            return False
            
        # Additional filtering for common non-IP patterns that look like IPs
        # Reject IPs that are likely version numbers or other numeric data
        
        # Pattern like 1.0.0.0, 2.0.0.0 etc (likely version numbers)
        if ip_nums[1] == 0 and ip_nums[2] == 0 and ip_nums[3] == 0:
            return False
            
        # Pattern like X.X.X.0 where all are same (likely not real IPs)
        if len(set(ip_nums[:3])) == 1 and ip_nums[3] == 0:
            return False
            
        # Pattern like 1.1.1.1, 2.2.2.2 etc (likely test/dummy data)
        if len(set(ip_nums)) == 1:
            return False
            
        # Reject obviously invalid patterns
        # Like 999.999.999.999 that might have passed int conversion somehow
        if any(num > 255 for num in ip_nums):
            return False
            
        # Additional heuristics for real public IPs
        # Most real public IPs don't start with very low numbers
        if first_octet <= 1:
            return False
            
        return True
        
    except (ValueError, AttributeError):
        return False

def send_file_to_vm(file):
    #run this D:\YEAR4-SECurity\grad\run_sandbox.py and put the file as input
    # Run the sandbox script and wait for it to finish
    result = subprocess.run(
        ["python", r"D:\YEAR4-SECurity\grad\run_sandbox_optimized.py", file],
        check=True
    )
    # After run_sandbox.py finishes, find the .dmp file in the single directory inside C:\Sandbox_Reports
    sandbox_reports_dir = r"C:\Sandbox_Reports"
    if not os.path.exists(sandbox_reports_dir):
        raise FileNotFoundError("Sandbox reports directory not found.")
    subdirs = [os.path.join(sandbox_reports_dir, d) for d in os.listdir(sandbox_reports_dir) if os.path.isdir(os.path.join(sandbox_reports_dir, d))]
    if not subdirs:
        raise FileNotFoundError("No subdirectories found in Sandbox reports directory.")
    report_dir = subdirs[0]
    dmp_files = [os.path.join(report_dir, f) for f in os.listdir(report_dir) if f.lower().endswith('.dmp')]
    if not dmp_files:
        raise FileNotFoundError("No .dmp file found in the sandbox report directory.")
    return dmp_files[0]
    

def extract_strings_from_dump(dump_file_path):
    """Extract strings from dump file"""
    strings_exe = r"C:\Program Files\CodeBlocks\MinGW\bin\strings.exe"
    
    if not os.path.exists(strings_exe):
        # Try alternative paths
        alternative_paths = [
            r"D:\YEAR4-SECurity\grad\strings.exe",
            r"D:\YEAR4-SECurity\grad\strings64.exe",
            "strings.exe"  # Try system PATH
        ]
        
        for path in alternative_paths:
            if os.path.exists(path):
                strings_exe = path
                break
        else:
            return "Error: strings.exe not found"
    
    try:
        # Extract strings with minimum length of 4
        result = subprocess.run([strings_exe, "-n", "4", dump_file_path], 
                              capture_output=True, text=True, errors='ignore')
        
        if result.returncode == 0:
            raw_strings = [line.strip() for line in result.stdout.splitlines() if line.strip()]
            
            # Normalize whitespace for each string before filtering
            normalized_strings = []
            for string in raw_strings:
                # Replace 2 or more consecutive whitespaces with single space
                normalized_string = re.sub(r'\s{2,}', ' ', string)
                normalized_strings.append(normalized_string)
            
            # Filter strings based on criteria
            filtered_strings = []
            ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
            
            for string in normalized_strings:
                # Eliminate strings less than 5 characters
                if len(string) < 5:
                    continue
                
                # Keep strings that are 50% or more alphanumeric characters
                alnum_count = sum(1 for c in string if c.isalnum())
                alnum_ratio = alnum_count / len(string)
                if alnum_ratio < 0.5:
                    continue
                
                # Remove strings that have 70% of same character
                if len(string) > 0:
                    same_char_count = sum(1 for c in string if c == string[0])
                    same_char_ratio = same_char_count / len(string)
                    if same_char_ratio >= 0.7:
                        continue
                
                # Remove strings that don't have alphabetical chars except IP addresses
                has_alpha = any(c.isalpha() for c in string)
                is_ip_address = ip_pattern.match(string)
                
                if not has_alpha and not is_ip_address:
                    continue
                
                # Remove strings with less than 3 alphabetical characters except IP addresses
                if not is_ip_address:
                    alpha_count = sum(1 for c in string if c.isalpha())
                    if alpha_count < 3:
                        continue
                
                # Lowercase all strings
                string = string.lower()
                filtered_strings.append(string)
            
            # Remove duplicates
            filtered_strings = list(set(filtered_strings))
            
            # Sort alphabetically
            filtered_strings.sort()
            
            # Create text output with count on first line, then strings
            output_text = f"{len(filtered_strings)}\n"
            output_text += "\n".join(filtered_strings)

            #eliminate strings that has same character for more than 50% of the string
            output_text = "\n".join(s for s in output_text.splitlines() if not re.match(r'^(.)\1{2,}$', s))
            
            return output_text
        else:
            return f"Error: strings.exe failed: {result.stderr}"
            
    except Exception as e:
        return f"Error extracting strings: {str(e)}"


def filter_meaningful_strings(all_strings_text):
    """
    Analyzes a large block of text and aggressively filters it to find only
    the most high-value indicators based on user-defined rules. It uses
    frequency analysis (stacking) to automatically discard common system noise.

    Args:
        all_strings_text: A single multi-line string variable containing all
                          the strings extracted from a memory dump.

    Returns:
        A dictionary containing categorized lists of high-signal indicators.
    """

    # --- Step 1: Frequency Analysis to Remove Noise ---
    # First, we count the occurrences of every single line to find what's common.
    all_lines = [line.strip() for line in all_strings_text.splitlines() if line.strip()]
    string_counts = Counter(all_lines)
    
    # We will only process strings that are relatively rare (appear less than 10 times).
    # This is a powerful technique to eliminate common, benign strings from system libraries.
    unique_or_rare_strings = {s for s, count in string_counts.items() if count < 10}

    # --- Step 2: Define High-Value Patterns per Your Request ---

    # Regex to find and EXTRACT only the filename of interest.
    # e.g., C:\path\to\malware.exe -> captures just "malware.exe"
    path_regex = re.compile(r"\\([a-zA-Z0-9_.-]+\.(?:exe|dll|sys))\b", re.IGNORECASE)

    # Regex for IP Addresses.
    ip_regex = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")

    dangerous_terms = {
        "virus", "trojan", "worm", "malware","ransom","steal","ware","hijack","keylog","exploit"
    }

    # --- Step 3: Initialize and Populate the New, Focused Categories ---

    indicators = {
        "executables and dlls": set(),
        "ip addresses": set(),
        "dangerous terms": set()
    }

    # Only loop through the much smaller set of rare strings for efficiency
    for s in unique_or_rare_strings:
        
        # Find all matching filenames in the line
        path_matches = re.findall(path_regex, s)
        if path_matches:
            indicators["executables and dlls"].update(path_matches)
        
        # Find all matching IP addresses in the line
        ip_matches = re.findall(ip_regex, s)
        if ip_matches:
            # Filter out private, local, and invalid IPs - keep only real public IPs
            valid_public_ips = set()
            for ip in ip_matches:
                if is_valid_public_ip(ip):
                    valid_public_ips.add(ip)
            
            if valid_public_ips:
                indicators["ip addresses"].update(valid_public_ips)

        # Check if the string contains any dangerous terms
        if any(word in dangerous_terms for word in s.lower().split()):
          indicators["dangerous terms"].add(s)

    # Convert the sets of found items into clean, sorted lists for the final report
    for key in indicators:
        if key == "executables and dlls":
            # For executables and DLLs, always display files even if scan fails
            exe_dll_list = []
            for filename in indicators[key]:
                try:
                    file_path = find_executable_path(filename)
                    if file_path:
                        sha256_hash = calculate_file_hash(file_path, 'sha256')
                        if sha256_hash:  # Only scan if hash calculation was successful
                            try:
                                # Get signature scan result using SHA256 hash
                                signature = SignatureScan.scan_file(sha256_hash, SignatureScan.api_key_2)
                                if signature and "No total_votes data found" not in signature:
                                    # Parse the signature to extract malicious vote count
                                    malicious_votes = 0
                                    if '"Malicious"' in signature:
                                        # Extract the number after "Malicious" ->
                                        match = re.search(r'"Malicious"\s*->\s*(\d+)', signature)
                                        if match:
                                            malicious_votes = int(match.group(1))
                                    
                                    # Only include files with more than 0 malicious votes with signature
                                    if malicious_votes > 0:
                                        exe_dll_list.append(f"{filename} [{signature}]")
                                    else:
                                        exe_dll_list.append(f"{filename}")
                                else:
                                    # Scan failed but still show the file
                                    exe_dll_list.append(f"{filename}")
                            except:
                                # Scan failed but still show the file
                                exe_dll_list.append(f"{filename}")
                        else:
                            # Hash calculation failed but still show the file
                            exe_dll_list.append(f"{filename}")
                    else:
                        # File path not found but still show the filename
                        exe_dll_list.append(f"{filename}")
                except:
                    # Any other error, still show the file
                    exe_dll_list.append(f"{filename}")
            indicators[key] = sorted(exe_dll_list, key=str.lower)
        elif key == "ip addresses":
            # For IP addresses, consolidate IPs with same first 3 octets and always display them
            ip_dict = {}
            for ip in indicators[key]:
                # Extract first 3 octets as the network part
                parts = ip.split('.')
                if len(parts) == 4:
                    network = '.'.join(parts[:3])
                    last_octet = int(parts[3])
                    
                    if network not in ip_dict:
                        ip_dict[network] = []
                    ip_dict[network].append((last_octet, ip))
            
            # Process each network group - show only ONE representative per network
            ip_list = []
            for network, ip_group in ip_dict.items():
                ip_group.sort(key=lambda x: x[0])  # Sort by last octet
                
                # Always scan only the first IP in each network group as representative
                _, representative_ip = ip_group[0]
                try:
                    signature = SignatureScan.main(representative_ip, SignatureScan.ip_api_key)
                    
                    if signature and ("Malicious" in signature or "Suspicious" in signature or "Safe" in signature):
                        if len(ip_group) == 1:
                            # Only one IP in this network
                            ip_list.append(f"{representative_ip} [{signature}]")
                        else:
                            # Multiple IPs - show range summary regardless of count
                            first_ip = ip_group[0][1]
                            ip_list.append(f"{first_ip} [{signature}]")
                    else:
                        # Scan failed or returned no valid signature, still show the IP
                        if len(ip_group) == 1:
                            ip_list.append(f"{representative_ip}")
                        else:
                            first_ip = ip_group[0][1]
                            ip_list.append(f"{first_ip}")
                except:
                    # Scan failed completely, still show the IP
                    if len(ip_group) == 1:
                        ip_list.append(f"{representative_ip}")
                    else:
                        first_ip = ip_group[0][1]
                        ip_list.append(f"{first_ip}")
            
            indicators[key] = sorted(ip_list, key=str.lower)
        else:
            indicators[key] = sorted(list(indicators[key]), key=str.lower)

    return indicators



def extract_strings_from_dump(dump_path, strings_exe_path=r"C:\Program Files\CodeBlocks\MinGW\bin\strings.exe"):
    """A helper function to run strings.exe on a file."""
    output = subprocess.run(
        [strings_exe_path, "-n8", dump_path], # Using -n8 to reduce noise
        capture_output=True, text=True, errors="ignore"
    )
    return output.stdout


def calculate_file_hash(file_path, algorithm='md5'):
    """Calculate hash of a file using specified algorithm"""
    try:
        if not os.path.exists(file_path):
            return None
        
        hash_obj = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            # Read file in chunks to handle large files
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        return hash_obj.hexdigest()
    except (IOError, OSError, ValueError):
        return None


def find_executable_path(filename):
    """Attempt to find the full path of an executable/dll"""
    # Common Windows system directories to search
    search_paths = [
        r"C:\Windows\System32",
        r"C:\Windows\SysWOW64", 
        r"C:\Windows",
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        os.environ.get('TEMP', ''),
        os.environ.get('APPDATA', ''),
        os.environ.get('LOCALAPPDATA', ''),
        # Add current directory and PATH
        os.getcwd()
    ]
    
    # Also check PATH environment variable
    path_env = os.environ.get('PATH', '')
    search_paths.extend(path_env.split(os.pathsep))
    
    for search_path in search_paths:
        if not search_path or not os.path.exists(search_path):
            continue
            
        potential_path = os.path.join(search_path, filename)
        if os.path.isfile(potential_path):
            return potential_path
            
        # Also try recursive search in some directories (limited depth)
        if search_path in [r"C:\Windows\System32", r"C:\Windows\SysWOW64"]:
            try:
                for root, dirs, files in os.walk(search_path):
                    # Limit depth to avoid long searches
                    if root.count(os.sep) - search_path.count(os.sep) > 2:
                        continue
                    if filename.lower() in [f.lower() for f in files]:
                        return os.path.join(root, filename)
            except (OSError, PermissionError):
                continue
    
    return None




# This block now correctly demonstrates how to use your updated function
def main(file):
    output = ""
    # The path to the memory dump you created
   
    #file=r"C:\Users\ayhos\OneDrive\Desktop\G\plutonium.exe"
    #file=r"D:\Games\Dark Souls 3 [FitGirl Repack]\setup.exe"
    #file=r"C:\Users\ayhos\OneDrive\Desktop\G\Dolphin - Shortcut.lnk"
    dump_file = send_file_to_vm(file)
    #dump_file="D:\YEAR4-SECurity\grad\plutonium.exe_12772.dmp"

    if os.path.exists(dump_file):
       # output += f"Analyzing memory dump: {dump_file}\n"
        
        # 1. Extract all strings from the dump file
        raw_string_data = extract_strings_from_dump(dump_file)
        if raw_string_data:
            
            # Extract malware-relevant strings from the raw data
            lines = raw_string_data.split('\n')
            if len(lines) > 1:
                # Skip the first line (count) and get the actual strings
                
                string_list = lines[1:]  # Get strings without the count
                malware_strings = string_list
                #malware_strings = stringswork.extract_malware_relevant_strings(string_list)
                #print(f"Found {len(malware_strings)} malware-relevant strings")
                
                
                # Create a text block with the malware-relevant strings for further processing
                malware_text = "\n".join(malware_strings)
                
                # 2. Call the function to get categorized indicators
                filtered_result = filter_meaningful_strings(malware_text)
                
                # 3. Print the clean, categorized results
                total_items = 0
                for category, items in filtered_result.items():
                    if items:
                        total_items += len(items)
                        output += f"\n--- {category.upper()} ---"
                        for item in items:
                            output += f"\n  - {item}"

            else:
                output += "No strings extracted from dump file."
    else:
        output += f"Dump file not found: {dump_file}"
    
    # Remove any files or directories inside C:\Sandbox_Reports
    import shutil
    sandbox_reports_dir = r"C:\Sandbox_Reports"
    if os.path.exists(sandbox_reports_dir):
        for entry in os.listdir(sandbox_reports_dir):
            entry_path = os.path.join(sandbox_reports_dir, entry)
            try:
                if os.path.isfile(entry_path) or os.path.islink(entry_path):
                    os.unlink(entry_path)
                elif os.path.isdir(entry_path):
                    shutil.rmtree(entry_path)
            except Exception as e:
                print(f"Failed to delete {entry_path}: {e}")
    
    return output

def analyze_output_summary(output_text):
    """
    Analyzes the output of main() function and returns counts of malicious/suspicious indicators
    
    Args:
        output_text: String output from main() function
        
    Returns:
        String with summary counts
    """
    lines = output_text.split('\n')
    
    # Initialize counters
    malicious_execs_dlls = 0
    malicious_ips = 0
    suspicious_ips = 0
    dangerous_terms_count = 0
    
    # Track which section we're currently in
    current_section = None
    
    for line in lines:
        line = line.strip()
        
        # Check for section headers
        if line.startswith("--- ") and line.endswith(" ---"):
            section_name = line[4:-4].lower()  # Remove "--- " and " ---"
            current_section = section_name
            continue
        
        # Skip empty lines and non-item lines
        if not line.startswith("- "):
            continue
        
        # Remove the "- " prefix to get the actual content
        content = line[2:]
        
        # Count based on current section
        if current_section == "executables and dlls":
            if "malicious" in content.lower():
                malicious_execs_dlls += 1
        elif current_section == "ip addresses":
            if "malicious" in content.lower():
                malicious_ips += 1
            elif "suspicious" in content.lower():
                suspicious_ips += 1
        elif current_section == "dangerous terms":
            dangerous_terms_count += 1
    
    # Create summary text
    summary = f"""Security Analysis Summary:
- Malicious Executables/DLLs: {malicious_execs_dlls}
- Malicious IP Addresses: {malicious_ips}
- Suspicious IP Addresses: {suspicious_ips}
- Dangerous Terms Found: {dangerous_terms_count}"""
    
    return summary
    
file=r"D:\Games\Dark Souls 3 [FitGirl Repack]\setup.exe"
#mal1=r"D:\Malwares\a00d0a0d8205dbde441d345dd9af431e9bd8ed2e9e61cfbb3f8d3eaac95cd501.exe"
#mal2=r"D:\Malwares\e1cffe1faffd2a399f833405e2b28960f35ed3ec9dcb9cfaeb2d66f27eccba47.exe"
#mal3=r"D:\Malwares\bbdd8d5f4788efb219aaf2cf17d959b339f9abc399517e6f131485ef2adcd6a9.exe"

x=main(file)
print("\n" + "="*50)
summary = analyze_output_summary(x)
print(summary)
print("\n" + "="*50)
print(x)


