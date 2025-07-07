import requests

def print_html(url):
    try:
        # Fetch the webpage content
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful

        # Print the HTML content
        print(response.text)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")

# Example usage
url = input("Enter the webpage URL to print HTML: ")
print_html(url)