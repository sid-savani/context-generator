import requests


def parse_github_url(url):
    url = url.replace(".git", "")  # 🔥 fix
    parts = url.strip().split("/")
    return parts[3], parts[4]


# ✅ smart file filter (frontend + backend)
def is_useful_file(name):
    name = name.lower()

    valid_extensions = (".js", ".jsx", ".ts", ".tsx", ".py", ".html", ".css")

    skip_keywords = ["config", "test", "spec", "lock", "env", "eslint", "prettier"]

    return (
        name.endswith(valid_extensions)
        and not any(skip in name for skip in skip_keywords)
    )


def get_repo_files(owner, repo):
    file_urls = []

    def fetch_contents(api_url):
        res = requests.get(api_url)
        data = res.json()

        # handle API error
        if isinstance(data, dict) and "message" in data:
            print("❌ API Error:", data["message"])
            return

        for item in data:
            if item["type"] == "file":
                name = item["name"]

                if is_useful_file(name):
                    file_urls.append((name, item["download_url"]))

            elif item["type"] == "dir":
                # 🔥 recursion happens here
                fetch_contents(item["url"])

    # start from root
    root_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
    fetch_contents(root_url)

    return file_urls

def fetch_file_content(url):
    try:
        return requests.get(url).text
    except:
        return ""


def build_repo_context(file_urls):
    context = ""

    for name, url in file_urls[:6]:  # limit for speed
        code = fetch_file_content(url)

        context += f"\n\n--- {name} ---\n"
        context += code[:2000]

    return context


def github_context_generator(repo_url):
    owner, repo = parse_github_url(repo_url)
    files = get_repo_files(owner, repo)
    return build_repo_context(files)
def explain_project(context):
    explanation = "\nPROJECT ANALYSIS:\n\n"

    # Detect language
    if ".py" in context:
        explanation += "- Project uses Python\n"
    if ".js" in context:
        explanation += "- Project uses JavaScript\n"
    if ".html" in context:
        explanation += "- Contains frontend (HTML/CSS)\n"

    # Detect frameworks/libraries
    if "PyQt5" in context:
        explanation += "- GUI built using PyQt5\n"
    if "flask" in context.lower():
        explanation += "- Backend uses Flask\n"
    if "react" in context.lower():
        explanation += "- Frontend uses React\n"

    # Detect features
    if "requests" in context:
        explanation += "- Uses API calls (requests library)\n"

    if "class" in context:
        explanation += "- Uses object-oriented structure\n"

    explanation += "\nFlow (inferred):\n"
    explanation += "- User input → processing → output display\n"

    explanation += "\nWhere to look:\n"
    explanation += "- Main logic likely in main/app file\n"
    explanation += "- UI/components defined in classes/functions\n"

    return explanation
from google import genai

client = genai.Client(api_key="AIzaSyDzA0nrLy2feFKzIBIyglWec0PiEQX-Vss")


def generate_ai_context(context):
    prompt = f"""
You are an expert software engineer.

Analyze this GitHub project code and generate structured context.

CODE:
{context[:6000]}

OUTPUT FORMAT:
- Project Type
- Tech Stack
- Main Files
- Architecture
- Data Flow
- Key Components
- Summary

Make it clean and reusable for answering coding questions.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",   # ✅ THIS works now
        contents=prompt
    )

    return response.text 

# 🔥 TEST
if __name__ == "__main__":
    repo_url = input("Enter GitHub repo URL: ")

    context = github_context_generator(repo_url)

    print("\n===== RAW CONTEXT =====\n")
    print(context[:1000])

    print("\n===== AI GENERATED CONTEXT =====\n")
    ai_context = generate_ai_context(context)
    print(ai_context)