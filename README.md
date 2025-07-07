# ClickSafe
ClickSafe is a cybersecurity project designed to mitigate the growing risks posed by deceptive online threats such as clickjacking, clickbait, and malicious file or URL-based attacks.


## URL ANALYSIS ##
-Submit URL to VirusTotal API for intial insights
-URL Structure Analysis where URL is spilt into components (Scheme, Domain, Path)
-Detection of suspicious substrings, formatting, IP addresses or shortened links via Regex
-Lexical features analysis is scored and weighed by a scoring system
-Analysis of host information by cheching domain popularity, country and ISP info with an implemented ranking system
-Content-Based Analysis, Where the HTML content is fully fetched and analyzed for any malicious tags, Javacript or any abnormal functions, While also SSL Certificate validity check.

## FILE ANALYSIS ##
-Extarct file hash nad requesr a scan from VirusTotal via API for intial insights
-Calculate Entropy for all PE Format sections to detect Compression/Encryption/Packing
-String Analysis by filtering out readable strings and extract dangerous terms, IP addresses, Domains or API functions called
-XML Analysis for Installer framework of file authentication and identify privileges needed for execution
-Deploy file into a shared folder with the sandbox to prepare for execution
-At Sandbox, File is Executed and child processes is memory dumped and a dump file is returned to the host machine for analysis, While also identification of files dropped to chech their safety
-Automatic VM cleaning system by reverting to a clean state snapshot after every file scan
-Dump File is analyzed for deeper string analysis



## CREDITS: Ahmed Hossam - Abdelrahman Khaled - Asem Ahmed - Rahma Hussein - Jana Hesham ##
