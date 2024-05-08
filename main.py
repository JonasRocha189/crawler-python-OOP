import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd

from sys import setrecursionlimit
setrecursionlimit(100000)

class Crawler:

  def __init__(self):
    self.baseURL = 'https://www.bumper.com'

    self.urls = set()
    self.urls_not_crawled = set()
    self.urls_crawled = []
    self.urls_error = []

    self.count = 0

    self.start()


  #### TODO: Refact methods remove query and fragments
  def checkUrl(self, url):   

    link = urlparse(url)

    # Check if is internal or external
    if link.netloc == "www.bumper.com" or link.netloc == "":   

      # Complete a relative link
      # if link.netloc == "" and str(link.path)[0] == "/":
      if link.netloc == "":
        url = self.baseURL+link.path
        # print(f"Fixed link: {link}")


      ## 
      # Check if is a valid URL and standardize the format
      #

      # Remove querys
      if len(link.query) > 0:
        l = str(url).split("?")
        url = l[0]
        # print(f"Query: {link}")
      
      # Remove fragments (#)
      if len(link.fragment) > 0:
        ll = str(url).split("#")
        url = ll[0]
        # print(f"Fragment: {link}")

      # Check if mailto or tel link
      if link.scheme == 'tel' or link.scheme == 'mailto':
        self.urls_not_crawled.add(url) 
      else:
        self.urls.add(url)

    else:
      # Remove querys
      if len(link.query) > 0:
        l = str(url).split("?")
        url = l[0]
        # print(f"Query: {link}")
      
      # Remove fragments (#)
      if len(link.fragment) > 0:
        ll = str(url).split("#")
        url = ll[0]
        # print(f"Fragment: {link}")

      self.urls_not_crawled.add(url)        


  def crawl(self, url):   

    # print(f"URL to be crawled: {url}")

    try:
      page = requests.get(url)
      # print(page.status_code)

      #### TODO
      # Check status, if != 200, create validations
      soup = BeautifulSoup(page.text, 'lxml')

      # Title
      # print("\n")
      # titles = soup.find_all('title')
      # print(f"Titles found: {len(titles)}")
      # for title in titles:
      #   print(f"Title: {title.get_text()}")

      # Description


      # Links
      links = soup.find_all('a')
      # print(f"Links found: {len(links)}")

      for link in links:
        # remove telephone link
        # if link.get('href').find('tel:'):
        #   link.extract()
        # # remove mailto link
        # if link.get('href').find('mailto:'):
        #     link.extract()

        if 'href' in link.attrs:
          # print(f"Ancor Text: {link.text} | Link: {link.attrs['href']}" )
          self.checkUrl(link.attrs['href'])

      
      print(f"\n\nURL crawled: {url} \nCounter: {self.count}")
      self.urls_crawled.append(url)  
    except:
      self.urls_error.add(url)
      print(f"Error crawling page: {url}")
    
    self.count += 1    
    self.start()

    


  def start(self):

    if len(self.urls) == 0: 
      self.urls.add(self.baseURL)
      # self.crawl(self.baseURL) ### check the homepage
      
    if self.count >= 1000:
      print("///////////////////////////")
      print("End of the crawler")

      ### Check Crawled URL's
      print(f"\n\nURLS Crawled({len(self.urls_crawled)}):")
      for l in self.urls_crawled:
        print(l)

      print(f"\n\nURLS NOT CRAWLED ({len(self.urls_not_crawled)}):")
      for n in self.urls_not_crawled:
        print(n)  

      print(f"\n\nLINKS NOT FOUND ({len(self.urls)}):")
      for n in self.urls:
        print(n) 

      print(f"\n\nURL's WITH ERROR ({len(self.urls_error)}):")
      for n in self.urls:
        print(n)  

    else:
      newUrl = list(self.urls)
      self.crawl(newUrl[self.count])


    


if __name__ == "__main__":
    Crawler()