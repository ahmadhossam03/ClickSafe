
import string
import os
import time
import uuid
import threading
import logging
import gc
import shutil
import concurrent.futures
from flask import Flask, request, jsonify
from flask_cors import CORS
#from maine import scar_url
from StringsScan import *
import SignatureScan
from EntropyScan import mainEntropy
import Analyze_Dump
api_key= "7ab5f0228475a1cc39da09508c0b8b3b49345deb5d80e35154338a67ccca7969"

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Lock for VM operations to prevent concurrent access
vm_lock = threading.Lock()






@app.route("/scanfile", methods=['POST'])
def scan_file():
    output = ""
    file_path = None
    temp_copy_path = None  # Add this for the temporary copy
    reports_dir=r"C:\file_backend\grad\uploads_reports"  # Change this to your desired reports directory

    os.makedirs(reports_dir, exist_ok=True)

    try:
        logger.info("Starting dynamic scan request")
        
        if 'file' not in request.files:
            return "Error: No file part", 400

        file = request.files['file']

        if file.filename == '':
            return "Error: No selected file", 400

        # Create unique filename to prevent conflicts
        timestamp = int(time.time())
        unique_id = uuid.uuid4().hex[:8]
        unique_filename = f"{timestamp}_{unique_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        # Create a temporary copy for subprocess operations
        temp_copy_filename = f"temp_{unique_filename}"
        temp_copy_path = os.path.join(UPLOAD_FOLDER, temp_copy_filename)
        shutil.copy2(file_path, temp_copy_path)
        logger.info(f"Created temporary copy: {temp_copy_filename}")
        
        file_hash=SignatureScan.get_file_hash(file_path)
        # check if the a file called <file_hash>.txt already exists in the reports directory,if yes, return its content as the output
        report_file_path = os.path.join(reports_dir, f"{file_hash}.txt")
        logger.info(f"File hash: {file_hash}")
        if os.path.exists(report_file_path):
            logger.info(f"Report already exists: {report_file_path}")
            with open(report_file_path, "r") as report_file:
                cached_result = report_file.read()
            
            # Clean up files before returning cached result
            try:
                if temp_copy_path and os.path.exists(temp_copy_path):
                    os.remove(temp_copy_path)
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                logger.info("Cleaned up files before returning cached result")
            except Exception as early_cleanup_error:
                logger.warning(f"Early cleanup failed: {early_cleanup_error}")
            
            return cached_result
        # Check that the file has a PE format.
        try:
            import pefile
            pe = pefile.PE(file_path)
            pe.close()  # Explicitly close the PE file handle
        except ImportError:
            logger.error("pefile module not installed. Please install it with 'pip install pefile'.")
            return "Error: pefile module not installed on server.", 500
        except Exception as pe_error:
            logger.error(f"File is not a valid PE file: {pe_error}")
            return "Error: Uploaded file is not a valid PE (Portable Executable) file.", 400
        

        logger.info(f"File saved as: {unique_filename}")

        # Run initial static analysis operations in parallel while VM is being prepared
        start_time = time.time()
        logger.info("Starting parallel static analysis")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all tasks using the temporary copy to avoid file locking on original
            signature_future = executor.submit(SignatureScan.scan_file, temp_copy_path, api_key)
            entropy_future = executor.submit(mainEntropy, temp_copy_path)
            string_future = executor.submit(mainString, temp_copy_path, signature_future.result())
            
            # Collect results as they complete
            SignatureAnalysis = signature_future.result()
            EntropyAnalysis = entropy_future.result()
            StringAnalysis = string_future.result()
        
        static_time = time.time() - start_time
        logger.info(f"Static analysis completed in {static_time:.2f} seconds")
        
        output += SignatureAnalysis
        output += EntropyAnalysis
        output += StringAnalysis
        output += "\n====================\n"
        
        # Use lock for VM operations to prevent conflicts
        logger.info("Starting VM analysis")
        with vm_lock:
            DynamicAnalysis = Analyze_Dump.main(temp_copy_path)  # Use temp copy here
            DynamicSummary = Analyze_Dump.analyze_output_summary(DynamicAnalysis)
        
        logger.info("VM analysis completed")
        output += DynamicSummary
        output += DynamicAnalysis
        print(DynamicAnalysis)
        #create a file with the hash as the name (<file_hash>.txt)
        with open(os.path.join(reports_dir, f"{file_hash}.txt"), "w") as report_file:
            report_file.write(output)

        return output

    except Exception as e:
        logger.error(f"Error in dynamic scan: {str(e)}")
        return f"Error: {str(e)}", 500  # Return error if something goes wrong
    
    finally:
        # Force garbage collection to close any lingering file handles
        gc.collect()
        
        # Clean up the temporary copy first (might still be in use)
        if temp_copy_path and os.path.exists(temp_copy_path):
            try:
                # Wait a bit for subprocess to finish
                time.sleep(2.0)
                os.remove(temp_copy_path)
                logger.info(f"Cleaned up temp copy: {temp_copy_path}")
            except Exception as temp_cleanup_error:
                logger.warning(f"Temp copy cleanup failed (will be cleaned up later): {temp_cleanup_error}")
        
        # Clean up the original uploaded file (should be free now since only temp copy is used by subprocesses)
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Cleaned up original file: {file_path}")
            except Exception as cleanup_error:
                logger.error(f"Original file cleanup failed: {cleanup_error}")


@app.route("/scanfile_static", methods=['POST'])
def scan_file_static():
    output = ""
    file_path = None
    reports_dir = r"C:\file_backend\grad\uploads_reports"  # Change this to your desired reports directory
    os.makedirs(reports_dir, exist_ok=True)
    
    try:
        logger.info("Starting static scan request")
        
        if 'file' not in request.files:
            return "Error: No file part", 400

        file = request.files['file']

        if file.filename == '':
            return "Error: No selected file", 400

        # Create unique filename to prevent conflicts
        timestamp = int(time.time())
        unique_id = uuid.uuid4().hex[:8]
        unique_filename = f"{timestamp}_{unique_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        file_hash = SignatureScan.get_file_hash(file_path)
        # check if the a file called <file_hash>.txt already exists in the reports directory,if yes, return its content as the output
        report_file_path = os.path.join(reports_dir, f"{file_hash}.txt")
        logger.info(f"File hash: {file_hash}")
        if os.path.exists(report_file_path):
            logger.info(f"Report already exists: {report_file_path}")
            with open(report_file_path, "r") as report_file:
                return report_file.read()
        
        logger.info(f"File saved as: {unique_filename}")

        # Run static analysis operations in parallel to reduce total time
        start_time = time.time()
        logger.info("Starting parallel static analysis")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all tasks
            signature_future = executor.submit(SignatureScan.scan_file, file_path, api_key)
            entropy_future = executor.submit(mainEntropy, file_path)
            string_future = executor.submit(mainString, file_path)
            
            # Collect results as they complete
            SignatureAnalysis = signature_future.result()
            EntropyAnalysis = entropy_future.result()
            StringAnalysis = string_future.result()
        
        static_time = time.time() - start_time
        logger.info(f"Static analysis completed in {static_time:.2f} seconds")
        
        output += SignatureAnalysis
        output += EntropyAnalysis
        output += StringAnalysis
        
        return output

    except Exception as e:
        logger.error(f"Error in static scan: {str(e)}")
        return f"Error: {str(e)}", 500  # Return error if something goes wrong
    
    finally:
        # Force garbage collection to close any lingering file handles
        gc.collect()
        
        # Always clean up the uploaded file
        if file_path and os.path.exists(file_path):
            try:
                # Longer wait to ensure all processes release the file
                time.sleep(1.5)
                os.remove(file_path)
                logger.info(f"Cleaned up: {file_path}")
            except PermissionError as perm_error:
                logger.warning(f"File still in use, retrying cleanup: {perm_error}")
                # Retry after additional delay
                time.sleep(2.0)
                try:
                    os.remove(file_path)
                    logger.info(f"Cleanup successful on retry: {file_path}")
                except Exception as retry_error:
                    logger.error(f"Final cleanup failed: {retry_error}")
            except Exception as cleanup_error:
                logger.error(f"Cleanup failed: {cleanup_error}")

@app.route("/scanfile_extentsion", methods=['POST'])
def scan_file_extention():
    file_path = None
    reports_dir = r"C:\file_backend\grad\uploads_reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    try:
        logger.info("Starting static scan request")
        
        if 'file' not in request.files:
            return "Error: No file part", 400

        file = request.files['file']

        if file.filename == '':
            return "Error: No selected file", 400

        # Create unique filename to prevent conflicts
        timestamp = int(time.time())
        unique_id = uuid.uuid4().hex[:8]
        unique_filename = f"{timestamp}_{unique_id}_{file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        # file_hash = SignatureScan.get_file_hash(file_path)  # Unused variable removed
        Signanture = SignatureScan.scan_file_sandbox(file_path, SignatureScan.api_key)
        # assume signature looks like this: Votes : "Malicious"-> 182 , extract the number of malicious votes if more than 0, else return "File is Malicious", else if 0 then return "File is Safe"

        if "Malicious" in Signanture:
            malicious_votes = int(Signanture.split("->")[-1].strip())
            if malicious_votes > 0:
                return f"File is Malicious", 400
            else:
                return "File is Safe", 200
        else:
            return "File is Safe", 200

    except Exception as e:
        logger.error(f"Error in static scan: {str(e)}")
        return f"Error: {str(e)}", 500  # Return error if something goes wrong

if __name__ == "__main__":
    app.run(debug=True)

