from imports import *

def extract_requested_privileges(file_path):
    output = []  # List to store results instead of printing

    try:
        pe = pefile.PE(file_path)

        # Check if the PE file has a resource section
        if not hasattr(pe, "DIRECTORY_ENTRY_RESOURCE"):
            return {"error": "No resource section found."}

        for resource_type in pe.DIRECTORY_ENTRY_RESOURCE.entries:
            if resource_type.id == pefile.RESOURCE_TYPE["RT_MANIFEST"]:  # Look for Manifest
                for resource_id in resource_type.directory.entries:
                    for resource_lang in resource_id.directory.entries:
                        data_rva = resource_lang.data.struct.OffsetToData
                        size = resource_lang.data.struct.Size
                        manifest_data = pe.get_memory_mapped_image()[data_rva : data_rva + size].decode("utf-8", errors="ignore")

                        # Extract execution level and uiAccess using regex
                        match = re.search(r'<requestedExecutionLevel level="(.*?)" uiAccess="(.*?)"', manifest_data)
                        if match:
                            level, ui_access = match.groups()

                            # Default descriptions
                            description = "Unknown privilege level."
                            description2 = "Unknown UI access."

                            if level == "asInvoker":
                                description = "The application runs with the same access token as its parent process."
                            elif level == "highestAvailable":
                                description = "The application runs with the highest privileges the user can obtain."
                            elif level == "requireAdministrator":
                                description = "The application runs with administrator privileges."

                            if ui_access == "true":
                                description2 = "The application can interact with the desktop, Keylogger/Screen capture signs."
                            elif ui_access == "false":
                                description2 = "The application cannot interact with the desktop."

                            # Append results instead of printing
                            output.append(f"Requested Privilege : {level} -> {description}")
                            output.append(f"UI Access : {ui_access} -> {description2}")

    except Exception:
        return {"error": "No Info extracted"}

    return output  # Return the list instead of printing

def get_manifest(file_path):
    try:
        pe = pefile.PE(file_path)

        # Check if the PE file has a resource section
        if not hasattr(pe, "DIRECTORY_ENTRY_RESOURCE"):
            return {"error": "No resource section found."}

        for resource_type in pe.DIRECTORY_ENTRY_RESOURCE.entries:
            if resource_type.id == pefile.RESOURCE_TYPE["RT_MANIFEST"]:  # Look for Manifest
                for resource_id in resource_type.directory.entries:
                    for resource_lang in resource_id.directory.entries:
                        data_rva = resource_lang.data.struct.OffsetToData
                        size = resource_lang.data.struct.Size
                        manifest_data = pe.get_memory_mapped_image()[data_rva : data_rva + size].decode("utf-8", errors="ignore")


                        manifest_data = manifest_data.replace(" ", "")
                        return manifest_data




    except Exception as e:
        return {""}

def extract_assembly_identity(file_path, manifest):
    output = []  # List to store results instead of printing
    try:
        # Split manifest into lines
        manifest_lines = manifest.split("\n")
        lines_count = len(manifest_lines) - 1  # Total number of lines

        for i, line in enumerate(manifest_lines):
            if "assemblyIdentity" in line:
                output.append(line)  # Store the found line

                # Move to the next line safely
                j = i + 1
                while j <= lines_count:
                    line = manifest_lines[j]
                    output.append(line)  # Store each relevant line

                    if "/>" in line:
                        break  # Stop at the end of the block

                    j += 1  # Move to the next line

                break  # Stop after first assemblyIdentity block

    except Exception:
        output.append("No Info extracted")

    return output  # Return the stored results instead of printing

path = r"D:\Games\Dark Souls 3 [FitGirl Repack]\setup.exe"


