import json
import os
import requests


class WikiApi:
    def __init__(self):
        self.url = os.getenv("WIKI_API_URL")
        self.username = os.getenv("WIKI_USERNAME")
        self.password = os.getenv("WIKI_PASSWORD")
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
        params = {"action": "query", "meta": "tokens", "format": "json"}

        request = self.session.get(url=self.url, params=params, auth=self.auth)
        data = request.json()

        token = data["query"]["tokens"]["csrftoken"]

        # Step 4: POST request to edit a page
        params = {
            "action": "edit",
            "title": page,
            "token": token,
            "format": "json",
            "bot": True,
            "summary": summary,
            "text": content,
        }

        request = self.session.post(self.url, data=params, auth=self.auth)
        data = request.json()
        return data

    def load_files(self, schema_name):
        files = sorted(os.listdir(schema_name))

        for filename in files:
            if filename.endswith(".json"):
                filepath = os.path.join(schema_name, filename)
                f = open(filepath)

                # Load and dump to validate that we have a json file
                data = json.loads(f.read())

                print(f"Pushed {filename}")


wiki = WikiApi()

wiki.load_files("buildings")
