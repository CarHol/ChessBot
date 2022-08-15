import re

mention_pattern = r"<@[!]?(\d+)>"

def mention_to_id(mention):
    return re.findall(mention_pattern, mention)[0]

def id_to_mention(id):
    return f"<@{id}>"

def find_mention_id(content):
    return re.findall(mention_pattern, content)