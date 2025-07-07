from imports import *
import subprocess
import requests
import os
import re

def extract_strings(file_path):
    output = subprocess.run(
        [r"C:\xampp\htdocs\grad\grad\strings\strings.exe", "-n5", "-d", file_path],
        capture_output=True, text=True
    )
    strings = output.stdout

    return strings

def extract_xml(strings):
    xml_string = ""
    start = strings.find('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
    end = strings.find('</assembly>', start) + len('</assembly>')
    if start != -1 and end != -1:
        xml_string = strings[start:end]
        strings = strings.replace(xml_string, '')
    else:
        xml_string = "No XML found"
    return xml_string


def filter_strings(strings):
    #remove xml content from strings
    xml_string = ""
    start = strings.find('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>')
    end = strings.find('</assembly>', start) + len('</assembly>')
    if start != -1 and end != -1:
        xml_string = strings[start:end]
        strings = strings.replace(xml_string, '')
    # Remove lines that are whitespaces or contain only numbers
    strings = [line.strip() for line in strings.splitlines() if line.strip() and not line.strip().isdigit()]

    # keep strings that are 50% or more alphanumeric characters
    strings = [line for line in strings if sum(c.isalnum() for c in line) / len(line) >= 0.5]
    #remove strings that has 70% of same character
    strings = [line for line in strings if sum(c == line[0] for c in line) / len(line) < 0.7]
    # lowercase all strings
    strings = [line.lower() for line in strings]
    # sort alphabetically
    strings.sort()
    
    return strings




api_key="AIzaSyD1cqy7So8NCXwVfpHtCdcn6X3MLURpekU"

def Ai_scan(prompt,api_key):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=GEMINI_API_KEY"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
    }
    # Replace GEMINI_API_KEY with your actual API key
    url = url.replace("GEMINI_API_KEY", api_key)
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}
    
def extract_gemini_response(response):
    try:
        return response['candidates'][0]['content']['parts'][0]['text']
    except (KeyError, IndexError, TypeError):
        return "No response found"
    

# Commented out extract_opcodes function - not currently used
"""
def extract_opcodes(file_path, max_instructions=100):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Use 'objdump' or 'gobjdump' if on macOS
    objdump_cmd = ['objdump', '-d', file_path]

    try:
        result = subprocess.run(objdump_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running objdump: {e.stderr}")
        return []

    lines = result.stdout.splitlines()
    opcode_data = []

    # Regex for opcode lines
    pattern = re.compile(r'^\s*([0-9a-fA-F]+):\s+((?:[0-9a-fA-F]{2}\s)+)\s*(.+)$')

    for line in lines:
        match = pattern.match(line)
        if match:
            address = match.group(1)
            opcodes = match.group(2).strip()
            instruction = match.group(3).strip()
            opcode_data.append((address, opcodes, instruction))
            if len(opcode_data) >= max_instructions:
                break

    return opcode_data
"""

# Create a list of malicious/suspicious opcodes sequences for packing, shellcoding, etc
malicious_opcode_sequences = [
    {
        "sequence": ["push", "ret"],
        "description": "Common shellcode pattern for jumping to shellcode or redirecting execution flow."
    },
    {
        "sequence": ["jmp", "esp"],
        "description": "Used in exploits to redirect execution to shellcode placed on the stack."
    },
    {
        "sequence": ["mov", "eax", "fs:[0x30]"],
        "description": "Accesses the Process Environment Block (PEB), often used in anti-debugging and unpacking routines."
    },
    {
        "sequence": ["xor", "eax", "eax"],
        "description": "Zeroing a register, often used in shellcode to avoid null bytes or clear registers."
    },
    {
        "sequence": ["call", "eax"],
        "description": "Indirect call, often used in obfuscated or packed code to hide control flow."
    },
    {
        "sequence": ["pop", "ebp", "mov", "esp", "ebp"],
        "description": "Stack pivoting, used in ROP chains and exploits."
    },
    {
        "sequence": ["int", "0x2e"],
        "description": "Direct system call, often used to bypass user-mode hooks or AV."
    },
    {
        "sequence": ["mov", "reg", "reg", "call", "reg"],
        "description": "Register-to-register moves followed by indirect calls, common in unpackers and shellcode."
    },
    {
        "sequence": ["mov", "reg", "0x401000", "jmp", "reg"],
        "description": "Jumping to a hardcoded address, often used in unpacking stubs."
    },
    {
        "sequence": ["lea", "reg", "[esp+value]", "call", "reg"],
        "description": "Stack-based call, used in shellcode to locate code/data dynamically."
    },
    {
        "sequence": ["pushad", "popad"],
        "description": "Saves/restores all general-purpose registers, often seen in shellcode and packers."
    },
    {
        "sequence": ["pushfd", "popfd"],
        "description": "Saves/restores EFLAGS register, used in anti-debugging and shellcode."
    },
    {
        "sequence": ["mov", "reg", "fs:[reg]"],
        "description": "Accessing thread or process information, often for anti-analysis or unpacking."
    },
    {
        "sequence": ["xor", "reg", "reg", "mov", "reg", "value"],
        "description": "Obfuscation pattern to hide constants or API addresses."
    },
    {
        "sequence": ["db", "0xcc"],
        "description": "Breakpoint instruction, sometimes used in packed or protected code."
    }
]
def opcode_analyses(opcodes,patterns):
    detected_patterns = []
    for pattern in patterns:
        if all(op in opcodes for op in pattern["sequence"]):
            detected_patterns.append(pattern)
    #if detected_patterns is empty
    if not detected_patterns:
        print("No malicious opcode patterns detected.")
    return detected_patterns

def mainString(file,ThirdParty):
    malicious_opcode_sequences = [
        {
            "sequence": ["push", "ret"],
            "description": "Common shellcode pattern for jumping to shellcode or redirecting execution flow."
        },
        {
            "sequence": ["jmp", "esp"],
            "description": "Used in exploits to redirect execution to shellcode placed on the stack."
        },
        {
            "sequence": ["mov", "eax", "fs:[0x30]"],
            "description": "Accesses the Process Environment Block (PEB), often used in anti-debugging and unpacking routines."
        },
        {
            "sequence": ["xor", "eax", "eax"],
            "description": "Zeroing a register, often used in shellcode to avoid null bytes or clear registers."
        },
        {
            "sequence": ["call", "eax"],
            "description": "Indirect call, often used in obfuscated or packed code to hide control flow."
        },
        {
            "sequence": ["pop", "ebp", "mov", "esp", "ebp"],
            "description": "Stack pivoting, used in ROP chains and exploits."
        },
        {
            "sequence": ["int", "0x2e"],
            "description": "Direct system call, often used to bypass user-mode hooks or AV."
        },
        {
            "sequence": ["mov", "reg", "reg", "call", "reg"],
            "description": "Register-to-register moves followed by indirect calls, common in unpackers and shellcode."
        },
        {
            "sequence": ["mov", "reg", "0x401000", "jmp", "reg"],
            "description": "Jumping to a hardcoded address, often used in unpacking stubs."
        },
        {
            "sequence": ["lea", "reg", "[esp+value]", "call", "reg"],
            "description": "Stack-based call, used in shellcode to locate code/data dynamically."
        },
        {
            "sequence": ["pushad", "popad"],
            "description": "Saves/restores all general-purpose registers, often seen in shellcode and packers."
        },
        {
            "sequence": ["pushfd", "popfd"],
            "description": "Saves/restores EFLAGS register, used in anti-debugging and shellcode."
        },
        {
            "sequence": ["mov", "reg", "fs:[reg]"],
            "description": "Accessing thread or process information, often for anti-analysis or unpacking."
        },
        {
            "sequence": ["xor", "reg", "reg", "mov", "reg", "value"],
            "description": "Obfuscation pattern to hide constants or API addresses."
        },
        {
            "sequence": ["db", "0xcc"],
            "description": "Breakpoint instruction, sometimes used in packed or protected code."
        }
    ]
    
    output = ""
    all_strings = extract_strings(file)
    filtered_strings = filter_strings(all_strings)
    xml_content = extract_xml(all_strings)

    # Read PromptHelper.txt to help the AI with detection
    with open("PromptHelper.txt", "r", encoding="utf-8") as f:
        helper_text = f.read()

    prompt = ("You are a malware analyst, you will get files that has PE FORMAT, You are required to be consistent because sometimes i give the same samples and get diffrent analysis, i will try to give you some helping notes to make your responses consistent." +
    "Below is a list of Windows API functions and behaviors often used for malicious intent:\n"
    + helper_text +
    "\n\nAnalyze the following strings extracted from a PE file, Make sure to follow the exact guidelines for the responce, dont add put greetings or any summary at the end. For each string, print it and print besides it (Normal, Suspicious, or Malicious), if suspicious or malicious write a short sentence of why  (example: 'string -> <normal/suspicious/malicious> '). Here are the strings:\n"
    )

    for string in filtered_strings:
        prompt += f"\n{string}"

    response = Ai_scan(prompt, api_key)
    AI_response = extract_gemini_response(response)

    # eliminate lines that has "-> normal" 
    AI_response = "\n".join(
        line for line in AI_response.splitlines() if "-> Normal" not in line
    )
    # eliminate lines that DOES NOT has "-> Suspicious" and "-> Malicious"
    AI_response = "\n".join(
        line for line in AI_response.splitlines() if "-> Suspicious" in line or "-> Malicious" in line
    )
    # delete duplicate lines from AI_response
    seen = set()
    AI_response = "\n".join(
        line for line in AI_response.splitlines() if not (line in seen or seen.add(line))
    )

    suspicious_count = sum(
        1 for line in AI_response.splitlines()
        if "-> Suspicious" in line
    )
    malicious_count = sum(
        1 for line in AI_response.splitlines()
        if "-> Malicious" in line
    )
    AI_response = "\n".join(
        line.replace("Suspicious : ", "").replace("Malicious : ", "") for line in AI_response.splitlines()
    )

    output+=AI_response
    output += "\n-------------------------------\n"


    with open("PromptHelper2.txt", "r", encoding="utf-8") as f:
        helper_text2 = f.read()

    Prompt2 = "Based on the following strings -> Description, write 'Summary: ' and then Summarize the behaviour in 1-3 sentances of the file and determine if it is Suspicious or Malicious, at last line determine file is Suspicious or Malicious(say 'Safe' if neither), here is the strings:\n " + AI_response + "\n\n Number of Suspicious strings: " + str(suspicious_count) + "\n Number of Malicious strings: " + str(malicious_count) + "\n\nhere is a helper text to help you with the analysis:\n" + helper_text2 + "And also here is virusTotal verdict about this file(use it to make your summary more accurate, but DO NOT mention virusTotal anywhere in your reply):" + ThirdParty + "\n\n"
    response2 = Ai_scan(Prompt2, api_key)
    AI_response2 = extract_gemini_response(response2)
    output += AI_response2
    output += "-------------------------------\n"
    
    with open("PromptHelper3.txt", "r", encoding="utf-8") as f:
        helper_text3 = f.read()

    prompt3 = helper_text3 + xml_content
    response3 = Ai_scan(prompt3, api_key)
    AI_response3 = extract_gemini_response(response3)
    output += AI_response3

    return output


#file=r"D:\\Games\\Power Rangers - Super Legends\\GameLauncher.exe"

#print(mainString(file))