import json
import os
import requests
from jinja2 import Template


class WikiApi:
    def __init__(self):
        self.url = os.getenv("WIKI_API_URL")
        self.username = os.getenv("WIKI_API_USERNAME")
        self.password = os.getenv("WIKI_API_PASSWORD")
        self.session = requests.Session()
        self.auth = (os.getenv("WIKI_API_USERNAME"), os.getenv("WIKI_API_PASSWORD"))

    def login(self):
        # Retrieve login token first
        params = {
            "action": "query",
            "meta": "tokens",
            "type": "login",
            "format": "json",
        }

        request = self.session.get(url=self.url, params=params, auth=self.auth)
        data = request.json()

        token = data["query"]["tokens"]["logintoken"]

        # Send a post request to login. Using the main account for login is not
        # supported. Obtain credentials via Special:BotPasswords
        # (https://www.mediawiki.org/wiki/Special:BotPasswords) for lgname & lgpassword

        params = {
            "action": "login",
            "lgname": self.username,
            "lgpassword": self.password,
            "lgtoken": token,
            "format": "json",
        }

        request = self.session.post(self.url, data=params, auth=self.auth)
        return request.json()

    def update_wiki(self, page, content, summary):
        # Step 3: GET request to fetch CSRF token
        self.login()
        params = {"action": "query", "meta": "tokens", "format": "json"}

        request = self.session.get(url=self.url, params=params, auth=self.auth)
        data = request.json()

        token = data["query"]["tokens"]["csrftoken"]

        # Step 4: POST request to edit a page
        params = {
            "action": "edit",
            "title": page,
            "format": "json",
            "bot": True,
            "summary": summary,
            "text": content,
            "token": token,
        }

        request = self.session.post(self.url, data=params, auth=self.auth)
        data = request.json()
        return data

    def _get_template(self, schema_name):
        with open(os.path.join("templates", f"{schema_name}.j2")) as f:
            template = Template(f.read())
        return template

    def load_files(self, schema_name):
        data_path = os.path.join("..", schema_name)
        files = sorted(os.listdir(data_path))
        menu_template = self._get_template(f"{schema_name}_menu")
        template = self._get_template(schema_name)

        menu_entries = []
        for filename in files:
            if filename.endswith(".json"):
                filepath = os.path.join(data_path, filename)
                f = open(filepath)

                data = json.loads(f.read())

                page_url = f"{schema_name}_{filename.split('.')[0]}"
                content = template.render(data)
                self.update_wiki(page_url, content, "Automatic update")
                print(f"Pushed {filename}")
                menu_entries.append({"url": page_url, "data": data})

        menu_content = menu_template.render(items=menu_entries)
        self.update_wiki(schema_name, menu_content, "Automatic menu update")


wiki = WikiApi()

wiki.load_files("buildings")
