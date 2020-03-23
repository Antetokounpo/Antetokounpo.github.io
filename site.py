import sys
import os
import locale
from datetime import datetime
import markdown
from bs4 import BeautifulSoup

def read_file(filename):
    with open(filename, 'r') as f:
        text = f.read()
    return text

def get_posts(directory):
    return [{'filename': i.split('.')[0], 'text': read_file(os.path.join(directory, i))} for i in os.listdir(directory)]

def get_timestamp(date_str):
    locale.setlocale(locale.LC_TIME, 'fr_CA.utf8')
    return datetime.strptime(date_str, '%d %B %Y').timestamp()

def timestamp_to_date(timestamp):
    locale.setlocale(locale.LC_TIME, 'fr_CA.utf8')
    return datetime.utcfromtimestamp(timestamp).strftime("%d %B %Y")

def md_to_html(text):
    md = markdown.Markdown()
    return md.convert(text)

def change_html_href(html):
    soup = BeautifulSoup(html, features="html.parser")
    for link in soup.findAll('link'):
        if not link['href'].startswith('https'):
            link['href'] = os.path.join("..", link['href'])
    for a in soup.findAll('a'):
        if not a['href'].startswith('https'):
            a['href'] = os.path.join("..", a['href'])
    for img in soup.findAll('img'):
        if not img['src'].startswith('https'):
            img['src'] = os.path.join("..", img['src'])
    return str(soup)

def generate_html(markdown_posts):
    html_posts = []
    for post in markdown_posts:
        filename = post['filename']+'.html'
        title = post['text'].split('\n')[0].strip('# ')
        date = get_timestamp(post['text'].split('\n')[1].strip('# '))
        html = md_to_html(post['text'])
        html_posts.append({
            'filename': filename,
            'title': title,
            'date': date,
            'html': html
        })
    return html_posts

def write_html(html_posts, html_template, directory):
    if not os.path.isdir(directory):
        os.mkdir(directory)

    for post in html_posts:
        with open(os.path.join(directory, post['filename']), 'w') as f:
            f.write(html_template[0]+post['html']+html_template[1])

def create_blog_index(html_posts, html_template, html_posts_dir):
    with open("blog.html", 'w') as f:
        html = ""
        sorted_posts = sorted(html_posts, key=lambda x: x['date'], reverse=True)
        for post in sorted_posts:
            html += """
                <a href={filename} class="blog-entry-link">
                    <article class="blog-entry">
                        <h2>{title}</h2>
                        <h5>{date}</h5>
                    </article>
                </a>
            """.format(filename=os.path.join(html_posts_dir, post['filename']), title=post['title'], date=timestamp_to_date(post['date']))
        f.write(html_template[0]+html+html_template[1])


def main():
    if len(sys.argv) < 2:
        print("Usage: {} [Markdown directory]".format(sys.argv[0]))
        return
    if not os.path.isfile("template.html"):
        print("No template.html found")
        return

    with open("template.html", 'r') as f:
        template = f.read()

    html_posts = generate_html(get_posts(sys.argv[1]))
    write_html(html_posts, change_html_href(template).split("{%%}"), "blog")
    create_blog_index(html_posts, template.split("{%%}"), "blog")

if __name__ == '__main__':
    main()