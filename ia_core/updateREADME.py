from github import Github, Auth
from dotenv import load_dotenv
import os

load_dotenv()

file_url= "README.md"
TOKEN=os.getenv("GITHUB_TOKEN")
g =Github(auth=Auth.Token(TOKEN))
rep=g.get_repo("SantanaOlmo/webAI")

readme_remote=rep.get_contents(file_url)
with open(file_url,"r",encoding="utf-8") as local_readme:
    readme_content=local_readme.read()

rep.update_file(
    path=file_url,
    message="updated README.md",
    content=readme_content,
    sha=readme_remote.sha
)