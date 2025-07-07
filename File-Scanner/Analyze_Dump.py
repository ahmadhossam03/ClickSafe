import subprocess
import os
import re
from collections import Counter
import hashlib
import SignatureScan
import StringsScan


import run_sandbox_optimized
def send_file_to_vm(file):
    #run this D:\YEAR4-SECurity\grad\run_sandbox.py and put the file as input
    # Run the sandbox script and wait for it to finish
    try:
        run_sandbox_optimized.main(file)  # This will run the sandbox script with the provided file
        

    except subprocess.TimeoutExpired:
        raise Exception("VM sandbox operation timed out")
    except subprocess.CalledProcessError as e:
        raise Exception(f"VM sandbox failed: {e.stderr}")
    except Exception as e:
        raise Exception(f"VM sandbox error: {str(e)}")
    
    # After run_sandbox.py finishes, find the .dmp file in the single directory inside C:\Sandbox_Reports
    sandbox_reports_dir = r"C:\Sandbox\Reports"
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


    

def extract_strings_from_dump(dump_file_path):
    """Extract strings from dump file"""
    strings_exe = r"C:\xampp\htdocs\grad\grad\strings\strings.exe"
    
    
    try:
        # Extract strings with minimum length of 4
        result = subprocess.run([strings_exe, "-n", "4", dump_file_path], 
                              capture_output=True, text=True, errors='ignore',
                              timeout=120)  # 2 minute timeout
        
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
import StringsScan

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

    # Regex for IP Addresses.
    ip_regex = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")

    dangerous_terms = {
        "virus", "trojan", "worm", "malware","ransom","steal","ware","hijack","keylog","exploit"
    }

    # --- Step 3: Initialize and Populate the New, Focused Categories ---

    indicators = {
        "ip addresses": set(),
        "dangerous terms": set()
    }

    # Only loop through the much smaller set of rare strings for efficiency
    for s in unique_or_rare_strings:
        
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
        if key == "ip addresses":
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




# This block now correctly demonstrates how to use your updated function
def main(file):
    output = ""
    dump_file = None
    
    try:
        # The path to the memory dump you created
        dump_file = send_file_to_vm(file)
        
        if os.path.exists(dump_file):
            # Extract all strings from the dump file
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

                    # Process dropped files report
                    dropped_files_output = process_dropped_files_report(os.path.dirname(dump_file))
                    output += dropped_files_output
                    
                    # 3. Print the clean, categorized results
                    total_items = 0
                    for category, items in filtered_result.items():
                        # Skip executables and dlls as they will be handled by dropped files report
                        if category == "executables and dlls":
                            continue
                            
                        output += "\n-------------------------------\n"
                        if items:
                            total_items += len(items)
                            for item in items:
                                output += f"\n  - {item}"
                    
                    # Add dropped files analysis results
                    

                else:
                    output += "No strings extracted from dump file."
        else:
            output += f"Dump file not found: {dump_file}"
    
    except Exception as e:
        output += f"Error during dynamic analysis: {str(e)}"
    
    finally:
        # Clean up dump file if it exists
        if dump_file and os.path.exists(dump_file):
            try:
                os.remove(dump_file)
                print(f"Cleaned up dump file: {dump_file}")
            except Exception as cleanup_error:
                print(f"Failed to cleanup dump file: {cleanup_error}")
        
        # Remove any files or directories inside C:\Sandbox_Reports
        import shutil
        sandbox_reports_dir = r"C:\Sandbox\Reports"
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
    
    # Track which section we're currently in based on content patterns
    current_section = None
    
    for line in lines:
        line = line.strip()
        
        # Skip separator lines
        if line.startswith("-------------------------------") or not line:
            continue
        
        # Skip lines that don't start with "- "
        if not line.startswith("- "):
            continue
        
        # Remove the "- " prefix to get the actual content
        content = line[2:]
        
        # Determine section based on content patterns
        if any(ext in content.lower() for ext in ['.exe', '.dll', '.sys']):
            # This is an executable/DLL entry from dropped files
            if "malicious" in content.lower():
                # Look for pattern like "Malicious"-> followed by a number > 0
                match = re.search(r'"?malicious"?\s*->\s*(\d+)', content.lower())
                if match and int(match.group(1)) > 0:
                    malicious_execs_dlls += 1
        elif re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', content):
            # This is an IP address entry
            if "malicious" in content.lower():
                malicious_ips += 1
            elif "suspicious" in content.lower():
                suspicious_ips += 1
        else:
            # Check if this could be a dangerous term
            # This would be anything that's not an executable or IP
            if not any(ext in content.lower() for ext in ['.exe', '.dll', '.sys']) and not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', content):
                dangerous_terms_count += 1
    
    # Create summary text
    summary = f"""
- Malicious Executables/DLLs: {malicious_execs_dlls}
- Malicious IP Addresses: {malicious_ips}
- Suspicious IP Addresses: {suspicious_ips}
- Dangerous Terms Found: {dangerous_terms_count}"""
    
    return summary

def process_dropped_files_report(report_directory):
    """
    Process the dropped_files_report.txt file to extract hashes and scan them
    
    Args:
        report_directory: Directory containing the dropped_files_report.txt file
        
    Returns:
        String with formatted scan results for dropped files
    """
    dropped_files_report_path = os.path.join(report_directory, "dropped_files_report.txt")
    output = ""
    
    if not os.path.exists(dropped_files_report_path):
        return ""
    
    try:
        with open(dropped_files_report_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
        
        # Eliminate empty lines
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        if not lines:
            return ""
        
        output += "\n-------------------------------\n"        
        for line in lines:
            # Skip separator lines
            if line.startswith("-------------------------------"):
                continue
            
            # Extract filename and hash using regex
            # Pattern: filename.ext -> (MD5: hash)
            match = re.search(r'^(.+?)\s*->\s*\(MD5:\s*([a-fA-F0-9]{32})\)', line)
            if match:
                filename = match.group(1).strip()
                file_hash = match.group(2).strip()
                
                try:
                    # Scan the hash using SignatureScan
                    scan_result = SignatureScan.scan_file_sandbox(file_hash, SignatureScan.api_key)
                    
                    if scan_result and scan_result.strip():
                        output += f"\n  - {filename} -> {scan_result}"
                    else:
                        output += f"\n  - {filename} -> No scan data available"
                        
                except Exception as e:
                    output += f"\n  - {filename} -> Scan failed: {str(e)}"
            else:
                # If the line doesn't match the expected format, include it as-is
                if line and not line.startswith("-------------------------------"):
                    output += f"\n  - {line}"
        
        return output
        
    except Exception as e:
        return f"\nError processing dropped files report: {str(e)}"


#file=r"D:\Games\Dark Souls 3 [FitGirl Repack]\setup.exe"
#file=r"D:\Dolphin\Dolphin.exe"
#mal1=r"D:\Malwares\a00d0a0d8205dbde441d345dd9af431e9bd8ed2e9e61cfbb3f8d3eaac95cd501.exe"
#mal2=r"D:\Malwares\e1cffe1faffd2a399f833405e2b28960f35ed3ec9dcb9cfaeb2d66f27eccba47.exe"
#mal3=r"D:\Malwares\bbdd8d5f4788efb219aaf2cf17d959b339f9abc399517e6f131485ef2adcd6a9.exe"
#dll=r"D:\Games\Power Rangers - Super Legends\powerrangers_remove.dll"
#x=main(file)
#print("\n" + "="*50)
#summary = analyze_output_summary(x)
#print(summary)
#print("\n" + "="*50)
#print(x)



#file=r"C:\hagat flashet asem\SysinternalsSuite\AccessEnum.exe"
#print(main(file))