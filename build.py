import os
import re
import shutil
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

"""HTML文件格式约束
    <!--
    title: 网页标题
    date: 制作日期
    description: 网页描述
    -->

    html文件内容(注意只包括body内容)

"""

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / ".templates"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_FILE = BASE_DIR / "index.html"
CONTENT_DIR = BASE_DIR / ".content"
PROJECT_DIR = BASE_DIR / ".projects"



def get_article(file):
    raw = file.read_text(encoding="utf-8")
    meta_match = re.search(r"<!--(.*?)-->", raw, re.DOTALL)
    metadata = {}
    "获取元数据"
    if meta_match:
        comment_text = meta_match.group(1)
        for line in comment_text.strip().splitlines():
            m = re.match(r"(\w+):\s*(.+)", line.strip())
            if m:
                key = m.group(1).lower()
                value = m.group(2).strip()
                metadata[key] = value
    "获取内容"
    content = re.sub(r"<!--.*?-->", "", raw, flags=re.DOTALL).strip()
    return {
        "title": metadata.get("title"),
        "date": metadata.get("date"),
        "description": metadata.get("description"),
        "content": content,
        "slug": file.stem
    }

def get_articles():
    ".content目录下的html文件按照日期排序,获取文章列表"
    contentFiles = sorted(CONTENT_DIR.glob("*.html"),reverse=True)
    ".project目录下的html文件按照日期排序,获取文章列表"
    projectFiles = sorted(PROJECT_DIR.glob("*.html"),reverse=True)

    articles = []
    projects = []
    for file in contentFiles:
        article = get_article(file)
        articles.append(article)
    for file in projectFiles:
        article = get_article(file)
        projects.append(article)
    return articles,projects
    
def createHtml(articles,projects):
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(["html"]),
    )
    indexTemplate = env.get_template("index.html")
    indexHtml = indexTemplate.render(posts=articles, projects=projects)
    (OUTPUT_FILE).write_text(indexHtml, encoding="utf-8")

    posts_output_dir = OUTPUT_DIR / "posts"
    projects_output_dir = OUTPUT_DIR / "projects"
    posts_output_dir.mkdir(parents=True, exist_ok=True)
    projects_output_dir.mkdir(parents=True, exist_ok=True)

    post_template = env.get_template("post.html")
    for article in articles:
        postHtml = post_template.render(post=article)
        outPutPath = posts_output_dir / (article["slug"] + ".html")
        outPutPath.write_text(postHtml, encoding="utf-8")
    project_template = env.get_template("project.html")
    for project in projects:
        projectHtml = project_template.render(project=project)
        outPutPath = projects_output_dir / (project["slug"] + ".html")
        outPutPath.write_text(projectHtml, encoding="utf-8")

def main():
    OUTPUT_DIR.mkdir(exist_ok=True,parents=True)
    articles , projects = get_articles()
    createHtml(articles,projects)




if __name__ == "__main__":
    main()
