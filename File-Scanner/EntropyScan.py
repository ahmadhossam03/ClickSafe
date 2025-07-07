from imports import *
def calculate_entropy(data):
    if not data:
        return 0.0
    length = len(data)
    freq = {byte: data.count(byte) / length for byte in set(data)}
    entropy = -sum(p * math.log2(p) for p in freq.values())
    return entropy

def analyze_pe_entropy(file_path):
    global Entropy_Score
    packed = False
    output_messages = []

    try:
        pe = pefile.PE(file_path)
    except Exception as e:
        return f"[ERROR] Failed to open PE file: {str(e)}"

    for section in pe.sections:
        section_entropy = calculate_entropy(section.get_data())
        temp=f"[+] Section: {section.Name.decode(errors='ignore').strip()} | Entropy: {section_entropy:.2f}"
        #remove non-alphanumeric characters except " ","[","]",".","+",":","-","!"
        temp = re.sub(r"[^a-zA-Z0-9 \[\].+:-]", "", temp)
        output_messages.append(temp)
        if section_entropy > 7.0:
            packed = True

    overlay_offset = pe.get_overlay_data_start_offset()
    overlay_data = pe.get_overlay()
    overlay_entropy = calculate_entropy(overlay_data)

    output_messages.append(f"[+] Overlay Offset: {overlay_offset} | Entropy: {overlay_entropy:.2f}")

    if overlay_entropy > 7.0:
        packed = True

    if packed:
        output_messages.append("[!] The file is likely packed.")

    else:
        output_messages.append("[!] The file is likely not packed.")

    return output_messages

path = r"D:\Games\Dark Souls 3 [FitGirl Repack]\setup.exe"

def mainEntropy(file_path):
    global Entropy_Score
    output=""
    try:
        entropy= analyze_pe_entropy(file_path)
        for line in entropy:
            output += line + "\n"
        #keep the line that has '!' and keep ines that has valuer more than 7.0, else remove
        output = "\n".join([line for line in output.split("\n") if "!" in line or (line.startswith("[+]") and float(line.split("Entropy: ")[1].split()[0]) > 7.0)])
        output += "\n-------------------------------\n"

        return output
    except Exception as e:
        return [f"[ERROR] An error occurred during entropy analysis: {str(e)}"]

