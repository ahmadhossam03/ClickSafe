from imports import *

def print_results_beforecoeffient(html, counts, features):
    """Prints HTML, feature counts, and risk classifications."""
    print("\n--- Webpage HTML Content ---\n")
    if html is not None:
        print(html[:2000])  # Limit output to first 2000 characters for readability
    else:
        print("No HTML content available (page may have failed to load).")

    print("\n--- Content-Based Classification Results before coefficient ---")
    print("\n--- Feature Occurrence Counts ---")
    for feature, count in counts.items():
        print(f"{feature}: {count} occurrences")

    print("\n--- Risk Classification (1 = Low, 3 = Medium, 5 = High) ---")
    for feature, score in features.items():
        print(f"{feature}: Risk Level {score}")

def print_results_js(js_counts, js_features):
    """Prints JavaScript analysis results."""
    print("\n--- JavaScript Analysis ---")
    for feature, count in js_counts.items():
        print(f"{feature}: {count} occurrences")
    print("\n--- JavaScript Risk Classification ---")
    for feature, score in js_features.items():
        print(f"{feature}: Risk Level {score}")

def print_results(html, counts, features):

    print("\n--- Feature Occurrence Counts ---")
    for feature, count in counts.items():
        print(f"{feature}: {count} occurrences")

    print("\n--- Risk Classification (1 = Low, 3 = Medium, 5 = High) ---")
    for feature, score in features.items():
        print(f"{feature}: Risk Level {score}")
