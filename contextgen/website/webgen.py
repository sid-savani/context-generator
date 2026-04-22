from parse import fetch_website_data 
from genstructure import generate_structure 
url = "https://www.apple.com"

data = fetch_website_data(url)
print(data)