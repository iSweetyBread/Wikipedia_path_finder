import requests
import networkx as nx
import matplotlib.pyplot as plt
import re
from queue import Queue
import time

class page:
    def __init__(self, link: str):
        self.link = link
        self.content = self.grab_content(self.link)
        self.name = self.grab_name(self.content)
        self.links = self.grab_links(self.content)
    
    def grab_content(self, link, tries = 5):
        try:
            result = requests.get(link)
            if(result.status_code == 200):
                return result.text
            elif(tries > 0):
                time.sleep(5)
                return self.grab_content(link, tries - 1)
            else:
                return "No"
        except requests.exceptions.RequestException as e:
            if(tries > 0):
                time.sleep(5)
                return self.grab_content(link, tries - 1)
            else:
                return "No"
    
    def grab_name(self, content):
        try:
            name = re.search(r'<span class="mw-page-title-main">(.*?)</span>',content,re.DOTALL).group(1)
            return name
        except:
            return "Deadend"
    
    def grab_links(self, content):
        try:
            a = re.search(r'<div class="mw-content-ltr mw-parser-output" lang="en" dir="ltr">(.*?)<h2 id="(References|Notes|Citations)">',content,re.DOTALL).group(1)
            a = re.findall(r'href="(.*?)"',a)
            b = []
            for i in a:
                if(re.match(r'^/wiki',i)):
                    if(re.match(r'/wiki/(File:|Special:|Template_talk:|Template:|Category:|Portal:|Wikipedia:|Help:|Talk:)',i)):continue
                    b.append("https://en.wikipedia.org"+i)     
            return list(dict.fromkeys(b))
        except:
            return ["No"]

while True:
    start_raw = str(input("Insert starting Wikipedia page link: "))
    if(re.match(r'https://en.wikipedia.org/wiki/.*', start_raw)):
        break
    print("Invalid link")
while True:
    target_raw = str(input("Insert target Wikipedia page link: "))
    if(re.match(r'https://en.wikipedia.org/wiki/.*', target_raw)):
        break
    print("Invalid link")
    
start_time = time.time()

start = page(start_raw)
target = page(target_raw)

print(start.name)

def find(start, target):
    q = Queue()
    q.put(start)
    G = nx.Graph()
    visited = set()
    visited.add(start.link)

    while True:
        current = q.get()
        G.add_node(current.name)
        for i in current.links:
            if(i == "No" or i in visited):
                continue
            if(i == target.link):
                G.add_edge(current.name, target.name)
                return G
            print(i)
            visited.add(i)
            temp = page(i)
            q.put(temp)
            G.add_edge(current.name, temp.name)

result = find(start, target)

print(len(list(result.nodes)))
print(f'{nx.shortest_path(result,start.name,target.name)}--{len(nx.shortest_path(result,start.name,target.name))-1}')

node_colors = ['blue'] * result.number_of_nodes()
node_colors[list(result.nodes).index(target.name)] = 'red'

end_time = time.time()
print(f"time: {end_time - start_time}")

nx.draw(result, with_labels = True, node_color = node_colors)
plt.show()
