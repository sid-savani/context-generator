import requests
from google import genai

# 🔑 Gemini Client
client = genai.Client(api_key="YOURAPIKEY")


# =========================
# URL PARSER
# =========================
def parse_github_url(url):
    url = url.replace(".git", "")
    parts = url.strip().split("/")
    return parts[3], parts[4]


# =========================
# FILE FILTER (keep almost everything)
# =========================
def is_useful_file(name):
    name = name.lower()
    skip_keywords = ["node_modules", ".git", "__pycache__", ".env"]
    return not any(skip in name for skip in skip_keywords)


# =========================
# RECURSIVE FILE EXTRACTION
# =========================
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
                # skip junk folders
                if any(skip in item["name"].lower() for skip in ["node_modules", ".git", "__pycache__"]):
                    continue

                fetch_contents(item["url"])  # 🔥 recursion

    root_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
    fetch_contents(root_url)

    return file_urls


# =========================
# FETCH FILE CONTENT
# =========================
def fetch_file_content(url):
    try:
        return requests.get(url).text
    except:
        return ""


# =========================
# BUILD CONTEXT
# =========================
def build_repo_context(file_urls):
    context = ""

    for name, url in file_urls[:10]:  # limit for API safety
        code = fetch_file_content(url)

        context += f"\n\n--- {name} ---\n"
        context += code[:1500]

    return context


# =========================
# MAIN CONTEXT GENERATOR
# =========================
def github_context_generator(repo_url):
    owner, repo = parse_github_url(repo_url)
    files = get_repo_files(owner, repo)
    return build_repo_context(files)


# =========================
# AI CONTEXT GENERATION
# =========================
def generate_ai_context(context):
    prompt = f"""
You are an expert software engineer.

Analyze this GitHub project and generate structured context.

CODE:
{context[:6000]}

OUTPUT:
- Project Type
- Tech Stack
- Main Files
- Architecture
- Data Flow
- Key Components
- Summary

Make it reusable for answering coding questions.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )

    return response.text


# =========================
# SAVE CONTEXT
# =========================
def save_context(context):
    with open("repo_context.txt", "w", encoding="utf-8") as f:
        f.write(context)


# =========================
# LOAD CONTEXT
# =========================
def load_context():
    with open("repo_context.txt", "r", encoding="utf-8") as f:
        return f.read()


# =========================
# ASK QUESTIONS
# =========================
def ask_question(context, question):
    prompt = f"""
You are a coding assistant.

PROJECT CONTEXT:
{context}

QUESTION:
{question}

Answer clearly based on the project.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )

    return response.text


# =========================
# MAIN EXECUTION
# =========================
if __name__ == "__main__":
    repo_url = input("Enter GitHub repo URL: ")

    print("\n🔍 Extracting repo...")
    raw_context = github_context_generator(repo_url)

    print("\n🤖 Generating AI context...")
    ai_context = generate_ai_context(raw_context)

    print("\n===== AI GENERATED CONTEXT =====\n")
    print(ai_context)

    # Save context
    save_context(ai_context)

    print("\n💾 Context saved. You can now ask questions.")

    # Interactive loop
    while True:
        question = input("\nAsk a question (type 'exit'): ")

        if question.lower() == "exit":
            break

        saved_context = load_context()
        answer = ask_question(saved_context, question)

        print("\n💡 AI Answer:\n", answer)
