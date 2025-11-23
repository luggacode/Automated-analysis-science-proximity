import json 


class JsonHandler():
    def __init__(self, filepath):
        self.filepath = filepath
        self.content = None

    def get_content(self) -> str:
        with open(self.filepath) as f:
            first_item = json.load(f)[0]
            print(first_item)
            return first_item


handler = JsonHandler("Code/article_batch_1.json")
handler.get_content()


