from flask import Flask, request, render_template
from bs4 import BeautifulSoup
import requests

app = Flask(__name__, template_folder='static')

def render_search_results(query=None, lang=None, country=None, num=None, display_form=True, results=None, userAgent=None, proxy=None):
    return render_template("index.html", query=query, lang=lang, country=country, num=num, display_form=display_form, results=results, userAgent=userAgent, proxy=proxy)

@app.route("/", methods=["GET", "POST"])
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        query = request.form.get("query")
        lang = request.form.get("lang")
        country = request.form.get("country")
        num = int(request.form.get("num"))
        user_agent = request.form.get("userAgent")
        proxy = request.form.get("proxy")
    else:
        query = request.args.get("query")
        lang = request.args.get("lang")
        country = request.args.get("country")
        num = int(request.args.get("num"))
        user_agent = request.args.get("userAgent")
        proxy = request.args.get("proxy")

    results = None

    if query:
        results = google_search(query, lang, country, num, user_agent, proxy)

    return render_search_results(query, lang, country, num, results=results, userAgent=user_agent, proxy=proxy)

def google_search(query, lang, country, num, user_agent, proxy):
    params = {
        "q": query,
        "hl": lang,
        "gl": country,
        "start": 0,
        "num": num
    }

    headers = {
        "User-Agent": user_agent if user_agent else "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    }
    # The proxy feature hasnt been properly tested yet
    if proxy:
        proxies = {
            "http": "http://" + proxy,
            "https": "https://" + proxy
        }
    else:
        proxies = None


    page_limit = 10
    page_num = 0

    data = []

    while True:
        page_num += 1
        print(f"Page: {page_num}\n")

        try:
            html = requests.get("https://www.google.com/search", params=params, headers=headers, proxies=proxies, timeout=30)
            html.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            break

        soup = BeautifulSoup(html.text, 'lxml')

        for result in soup.select(".tF2Cxc"):
            title = result.select_one(".DKV0Md").text
            try:
                snippet = result.select_one(".lEBKkf span").text
            except:
                snippet = None
            links = result.select_one(".yuRUbf a")["href"]

            data.append({
                "title": title,
                "snippet": snippet,
                "link": links
            })

            print(f"Title: {title}")
            if snippet:
                print(f"Snippet: {snippet}")
            print(f"Link: {links}\n")

        if page_num == page_limit:
            break
        if soup.select_one(".d6cvqb a[id=pnnext]"):
            params["start"] += 10
        else:
            break

    return data

if __name__ == "__main__":
    app.run(debug=True)
