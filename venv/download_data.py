import nltk
import os

# Define the local download directory
local_nltk_dir = os.path.join(os.getcwd(), 'nltk_data')

print(f"--- Attempting to download NLTK data to local folder: {local_nltk_dir} ---")

# Download the 'punkt' package to the specified local directory
nltk.download('punkt', download_dir=local_nltk_dir)

print("--- Download script finished. ---")
print("Check the 'nltk_data' folder in your project to see if it contains a 'tokenizers' sub-folder.")