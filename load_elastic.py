import json
import os
from elasticsearch import Elasticsearch, RequestsHttpConnection


class StfcDatabase:
    def __init__(self):
        self.host = os.getenv("ES_HOST")
        self.port = os.getenv("ES_PORT")
        self.api_key = os.getenv("ES_API_KEY")

        self.es = Elasticsearch(
            [{"host": self.host, "port": self.port, "use_ssl": True}],
            api_key=self.api_key,
            scheme="https",
            connection_class=RequestsHttpConnection,
        )
        self.es_info = self.es.info()
        self.health = self.es.cluster.health()

    def load_files(self, schema_name):
        directory = os.path.join("data/", schema_name)
        self.es.indices.create(index=schema_name, ignore=[400])

        # Make sure the example file comes first as it will be used to
        # set the default data types in the index
        files = sorted(os.listdir(directory))
        files.remove("example.json")

        for filename in ["example.json"] + files:
            if filename.endswith(".json"):
                filepath = os.path.join(directory, filename)
                f = open(filepath)
                data = json.loads(f.read())
                doc_id = f"{schema_name}__{os.path.splitext(filename)[0]}"
                self.es.index(index=schema_name, doc_type="_doc", id=doc_id, body=data)
                print(f"Loaded {filename}")


ES = StfcDatabase()
ES.load_files("buildings")
