# Libraries used to crawl and parse the data
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd

# Utils libs
import os
import datetime

# Custom the Python recursion limit
from sys import setrecursionlimit
setrecursionlimit(100000)

class Crawler:

  def __init__(self):
    # Custom the crawler 
    self.baseURL = 'https://www.bumper.com'
    self.limit_pages = 105
    self.limit_save = 10

    self.urls = set()
    self.urls_not_crawled = set()
    self.urls_crawled = []
    self.urls_error = []

    self.output = []

    self.count = 0
    self.count_save = 1

    self.start()


  ##
  # Check if URL is internal or external, relative or absolute and remove params and fragments
  # Standardize the URL's by the baseURL seted
  #
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

  ##
  # Crawl the URL and get the links for recursion
  #
  def crawl(self, url):   

    # print(f"URL to be crawled: {url}")

    try:
      page = requests.get(url)
      page_status = page.status_code

      #### TODO
      # Check status, if != 200, create validations
      soup = BeautifulSoup(page.text, 'lxml')

      # Title
      titles = soup.find_all('title')
      titles_arr = []
      titles_count = 0
      if len(titles)  != 0:
        for title in titles:
          titles_arr.append(title.get_text())
          titles_count += 1

      # Description
      desc_arr = []
      desc_count = 0

      desc = soup.find_all("meta", {'name':'Description'})
      if len(desc) != 0:
        for d in desc:
          desc_arr.append(d['content'])
          desc_count += 1

      desc_min = soup.find_all("meta", {'name':'description'})
      if len(desc_min) != 0:
        for dm in desc_min:
          desc_arr.append(dm['content'])
          desc_count += 1

      # Text

      # H heads
      # h1 = []
      # h1_count = 0

      # h2 = []
      # h2_count = 0

      # h3 = []
      # h3_count = 0

      # h4 = []
      # h4_count = 0

      # h5 = []
      # h5_count = 0
      
      # h6 = []
      # h6_count = 0

      # if(check_result(soup.find_all("h1"))): 
      #   for h in check_result(soup.find_all("h1")):
      #     h1.append(h.get_text())
      #     h1_count += 1

      # if(check_result(soup.find_all("h2"))): 
      #   for h in check_result(soup.find_all("h2")):
      #     h2.append(h.get_text())
      #     h2_count += 1

      # if(check_result(soup.find_all("h3"))): 
      #   for h in check_result(soup.find_all("h3")):
      #     h3.append(h.get_text())
      #     h3_count += 1

      # if(check_result(soup.find_all("h4"))): 
      #   for h in check_result(soup.find_all("h4")):
      #     h4.append(h.get_text())
      #     h4_count += 1

      # if(check_result(soup.find_all("h5"))): 
      #   for h in check_result(soup.find_all("h5")):
      #     h5.append(h.get_text())
      #     h5_count += 1

      # if(check_result(soup.find_all("h6"))): 
      #   for h in check_result(soup.find_all("h6")):
      #     h6.append(h.get_text())
      #     h6_count += 1

      # Images

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

      
      print(f"Counter: {self.count} - URL crawled: {url}")
      self.urls_crawled.append(url)  

      # OUTPUT
      # URL, Status, Title, Title amount, Description, Description amount, 
      # H1, H1 amount, H2, H2 amount, H3, H3 amount, H4, H4 amount, H5, H5 amount, H6, H6 amount
      # P text, links (inside content) ancor, url
      # Images source, images size, image alt
      output = [
        url, page_status,
        titles_arr, titles_count,
        desc_arr, desc_count,
        # h1, h1_count, h2, h2_count, h3, h3_count,
        # h4, h4_count, h5, h5_count, h6, h6_count,
      ]
      self.output.append(output)

    except:
      self.urls_error.append(url)
      print(f"Error crawling page: {url}")
    
    self.count += 1    
    self.start()

  ##
  # Save DataFrames in CSV files
  #
  def save_df(self, df, name_file):
    df.to_csv(f'output/{date.year}-{date.month}-{date.day}/{name_file}.csv', index=False)
  
  ##
  # Start the script and control the flux
  #
  def start(self):
    
    # Create a new folder per day 
    date = datetime.datetime.now()
    if os.path.isdir(f"./output/{date.year}-{date.month}-{date.day}") == False:
      os.mkdir(f"./output/{date.year}-{date.month}-{date.day}")

    if len(self.urls) == 0: 
      self.urls.add(self.baseURL)
      # self.crawl(self.baseURL) ### check the homepage

    # Output 
    if self.count > self.limit_save - 1 and self.count > (self.count_save * self.limit_save) - 1:
      # print(f"self_count:{self.count} - limit_save:{self.limit_save} - count_save: {self.count_save} ") 

      try:
        
        output = pd.DataFrame(self.output[(self.count_save - 1) * self.limit_save : self.count]) 
        print(f"{(self.count_save - 1) * self.limit_save} : {self.count}")

        print("DATAFRAME - SELECTION")
        print(self.output[(self.count_save - 1) * self.limit_save : self.count])
        print("\n")

        output.to_csv(f'output/{date.year}-{date.month}-{date.day}/crawled-{self.count_save}.csv', index=False)
        print(f"URL's crawled saved - Total: {len(output)} - Count_save: {self.count_save}")

        self.count_save += 1
      
      except Exception as error:
        print(f"Error saving files: {error}")

      
    # End of the Crawler
    if self.count >= self.limit_pages:
      print("///////////////////////////")
      print("End of the crawler")

      ### Check Crawled URL's
      # print(f"\n\nURLS Crawled({len(self.urls_crawled)}):")
      # for l in self.urls_crawled:
      #   print(l)

      # print(f"\n\nURLS NOT CRAWLED ({len(self.urls_not_crawled)}):")
      # for n in self.urls_not_crawled:
      #   print(n)  

      # print(f"\n\nLINKS NOT FOUND ({len(self.urls)}):")
      # for n in self.urls:
      #   print(n) 

      # print(f"\n\nURL's WITH ERROR ({len(self.urls_error)}):")
      # for n in self.urls:
      #   print(n)  

      # Output
      try:

        # Save the rest of URL's crawled in CSV
        rest = self.limit_pages % self.limit_save
        if rest != 0:
        
          output_rest = pd.DataFrame(self.output[((self.count_save - 1) * self.limit_save)  : self.count + 1]) 
          print(f"{((self.count_save - 1) * self.limit_save) } : {self.count + 1}")

          print("DATAFRAME - SELECTION")
          print(self.output[((self.count_save - 1) * self.limit_save)  : self.count + 1])
          print("\n")

          output_rest.to_csv(f'output/{date.year}-{date.month}-{date.day}/crawled-{self.count_save}.csv', index=False)
          print(f"URL's crawled saved - Total: {len(output_rest)} - Count_save: {self.count_save}")



        # Save URL's crawled in CSV
        urls_crawled = pd.DataFrame(self.urls_crawled)  
        urls_crawled.to_csv(f'output/{date.year}-{date.month}-{date.day}/crawled-total.csv', index=False)
        print(f"URL's crawled saved - Total: {len(urls_crawled)}")

        # Save URL's NOT crawled in CSV
        urls_not_crawled = pd.DataFrame(self.urls_not_crawled)  
        urls_not_crawled.to_csv(f'output/{date.year}-{date.month}-{date.day}/not_crawled-total.csv', index=False)
        print(f"URL's NOT crawled saved - Total: {len(urls_not_crawled)}")

        # Save URL's with ERROR in CSV
        urls_error = pd.DataFrame(self.urls_error)  
        urls_error.to_csv(f'output/{date.year}-{date.month}-{date.day}/errors-total.csv', index=False)
        print(f"URL's with ERROR saved - Total: {len(urls_error)}")

        # Save ALL URL's in CSV
        total_urls = list(self.urls)
        total_urls_df = pd.DataFrame(total_urls)  
        total_urls_df.to_csv(f'output/{date.year}-{date.month}-{date.day}/total-urls.csv', index=False)
        print(f"All URL's found saved - Total: {len(total_urls)}")


        # Save OUTPUTS in CSV
        total_output_df = pd.DataFrame(self.output)  
        total_output_df.to_csv(f'output/{date.year}-{date.month}-{date.day}/outputs.csv', index=False)
        print(f"All OUTPUTS saved - Total: {len(total_output_df)}")

        self.count_save += 1
      
      except Exception as error:
        print(f"Error saving files: {error}")

    else:
      newUrl = list(self.urls)
      self.crawl(newUrl[self.count])

  

if __name__ == "__main__":
    Crawler()