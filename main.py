# Libraries used to crawl and parse the data
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd

# Utils libs
import os
import datetime
import time

# Custom the Python recursion limit
from sys import setrecursionlimit
setrecursionlimit(100000)

class Crawler:

  def __init__(self):
    # Custom the crawler 
    self.baseURL = 'https://www.bumper.com'
    self.limit_pages = 1000
    self.limit_save = 200

    self.urls = set()
    self.urls_not_crawled = set()
    self.urls_crawled = []
    self.urls_error = []

    self.output = []

    self.count = 0
    self.count_save = 1

    self.date = datetime.datetime.now()


    self.urls_to_exclude = []
    self.folder = f"./output/{self.date.year}-{self.date.month}-{self.date.day}"
    
    self.start_crawl = time.time()
    self.total_urls_crawled = []

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
      body = soup.find('main')
      text = body.get_text()

      # 
      #  H heads
      #

      # H1
      h1 = []
      h1_count = 0

      h1_soup = soup.find_all("h1")
      if h1_soup != 0 : 
        for h in h1_soup:
          h1.append(h.get_text())
          h1_count += 1

      # H2
      h2 = []
      h2_count = 0

      h2_soup = soup.find_all("h2")
      if h2_soup != 0 : 
        for h in h2_soup:
          h2.append(h.get_text())
          h2_count += 1

      # H3
      h3 = []
      h3_count = 0

      h3_soup = soup.find_all("h3")
      if h3_soup != 0 : 
        for h in h3_soup:
          h3.append(h.get_text())
          h3_count += 1

      # H4
      h4 = []
      h4_count = 0

      h4_soup = soup.find_all("h4")
      if h4_soup != 0 : 
        for h in h4_soup:
          h4.append(h.get_text())
          h4_count += 1

      # H5
      h5 = []
      h5_count = 0

      h5_soup = soup.find_all("h5")
      if h5_soup != 0 : 
        for h in h5_soup:
          h5.append(h.get_text())
          h5_count += 1

      # H6
      h6 = []
      h6_count = 0

      h6_soup = soup.find_all("h6")
      if h6_soup != 0 : 
        for h in h6_soup:
          h6.append(h.get_text())
          h6_count += 1

      

      # Images

      # Links
      links = []
      links_soup = soup.find_all('a')
      # print(f"Links found: {len(links)}")

      for link in links_soup:
        if 'href' in link.attrs:
          links.append([link.text, link.attrs['href']] )
          self.checkUrl(link.attrs['href'])

      
      self.log(f"Counter: {self.count} - URL crawled: {url}")
      self.urls_crawled.append(url)  

      # OUTPUT
      # URL, Status, Title, Title amount, Description, Description amount, 
      # H1, H1 amount, H2, H2 amount, H3, H3 amount, H4, H4 amount, H5, H5 amount, H6, H6 amount
      # Conten texts, links (inside body) ancor, url
      # Images source, images size, image alt
      output = [
        url, page_status,
        titles_arr, titles_count,
        desc_arr, desc_count,
        h1, h1_count, h2, h2_count, h3, h3_count,
        h4, h4_count, h5, h5_count, h6, h6_count,
        text,
        links
      ]
      self.output.append(output)

    except:
      self.urls_error.append(url)
      self.log(f"Error crawling page: {url}")
    
    self.count += 1    
    self.start()

  ##
  # Save DataFrames in CSV files
  #
  def save_df(self, df, name_file):
    df.to_csv(f'{self.folder}/{name_file}.csv', index=False)
  

  ##
  # Save informations about the crawl
  #
  def log(self, log):  
    file = f"{self.folder}/log.txt"

    # create a file
    if not os.path.exists(file):
      open(file, 'x')

    # Save the info
    with open(file, 'a') as arq:
      arq.write("")
      arq.write(f"{log} \n")
      arq.close()


  ##
  # Start the script and control the flux
  #
  def start(self):    
    
    # Create a new folder per day 
    if os.path.isdir(f"./output") == False:
      os.mkdir(f"./output")
    
    # Check if there is a folder for today
    if os.path.isdir(f"{self.folder}") == False:
      os.mkdir(f"{self.folder}")

    # Check if there is no URL in the set and add the baseURL if not
    if len(self.urls) == 0: 
      self.urls.add(self.baseURL)
      # self.crawl(self.baseURL) ### check the homepage

      # Create a folder for each crawl
      folders = len(os.listdir(f'{self.folder}/'))
      if folders == 0 : 
        self.folder = f"{self.folder}/1"
        os.mkdir(f"{self.folder}")
      else:
        self.folder = f"{self.folder}/{folders + 1}"
        os.mkdir(f"{self.folder}")

      print("//////////")
      print("Crawler started")
      print(f"URL: {self.baseURL}")

      if os.path.exists('./urls-crawled.csv'):
        total_urls_crawled_df = pd.read_csv('./urls-crawled.csv')
        self.total_urls_crawled = total_urls_crawled_df.values.tolist()


    # Save into small files if more than 1k URL's to scrape else save in just one
    if self.limit_pages > 1000:

      # Output 
      if self.count > self.limit_save - 1 and self.count > (self.count_save * self.limit_save) - 1:
        # print(f"self_count:{self.count} - limit_save:{self.limit_save} - count_save: {self.count_save} ") 

        try:
          
          output = pd.DataFrame(self.output[(self.count_save - 1) * self.limit_save : self.count]) 
          file_name = f'crawled-{self.count_save}'
          self.save_df(output, file_name)
          self.log(f"URL's crawled saved - Total: {len(output)} - Count_save: {self.count_save}")

          self.count_save += 1
        
        except Exception as error:
          self.log(f"Error saving files: {error}")

      
    # End of the Crawler
    if self.count >= self.limit_pages:
      end = time.time()
      print("///////////////////////////")
      print("End of the crawler")
      print(f"Duration: {round(end - self.start_crawl, 2)} secounds")

      # Output
      try:

        # Save into small files if more than 1k URL's to scrape else save in just one
        if self.limit_pages > 1000 :
          # Save the rest of URL's crawled in CSV
          rest = self.limit_pages % self.limit_save
          if rest != 0:        
            output_rest = pd.DataFrame(self.output[((self.count_save - 1) * self.limit_save)  : self.count + 1])           
            file_name_rest = f'crawled-{self.count_save}'
            self.save_df(output_rest, file_name_rest)
            self.log(f"URL's crawled saved - Total: {len(output_rest)} - Count_save: {self.count_save}")
          

        # Save into small files if more than 1k URL's to scrape else save in just one
        else:
          # Save URL's crawled in CSV
          urls_crawled = pd.DataFrame(self.urls_crawled)  
          file_name_urls_crawled = f'crawled-total'
          self.save_df(urls_crawled,file_name_urls_crawled )
          self.log(f"URL's crawled saved - Total: {len(urls_crawled)}")

          # Save URL's NOT crawled in CSV
          urls_not_crawled = pd.DataFrame(self.urls_not_crawled)  
          file_name_urls_not_crawled = f'not_crawled-total'
          self.save_df(urls_not_crawled, file_name_urls_not_crawled)
          self.log(f"URL's NOT crawled saved - Total: {len(urls_not_crawled)}")

          # Save URL's with ERROR in CSV
          urls_error = pd.DataFrame(self.urls_error)  
          filne_name_urls_error = f'errors-total'
          self.save_df(urls_error, filne_name_urls_error)
          self.log(f"URL's with ERROR saved - Total: {len(urls_error)}")

          # Save ALL URL's in CSV
          total_urls = list(self.urls)
          total_urls_df = pd.DataFrame(total_urls)  
          file_name_total_urls_df = f'total-urls'
          self.save_df(total_urls_df, file_name_total_urls_df)
          self.log(f"All URL's found saved - Total: {len(total_urls)}")

          # Save OUTPUTS in CSV
          total_output_df = pd.DataFrame(self.output)  
          filen_name_total_output_df = f'outputs'
          self.save_df(total_output_df, filen_name_total_output_df)
          self.log(f"All OUTPUTS saved - Total: {len(total_output_df)}")

          ############

          # Save the main output - URL's FOUND
          file = './urls-total.csv'
          if not os.path.exists(file):
            total_urls_df.to_csv(file, index=False)
          else:
            total_urls_df.to_csv(file, mode='a', index=False)

          # Save the main output - URL's CRAWLED
          file = './urls-crawled.csv'
          if not os.path.exists(file):
            urls_crawled.to_csv(file, index=False)
          else:
            urls_crawled.to_csv(file, mode='a', index=False)
            
        self.count_save += 1
      
      except Exception as error:
        self.log(f"Error saving files: {error}")

    else:
      newUrl = list(self.urls)   

      # Check URl was crawled before and not seted with error or is seted to NOT be crawled
      if newUrl[self.count] not in self.urls_crawled and newUrl[self.count] not in self.urls_error and newUrl[self.count] not in self.total_urls_crawled:
        self.crawl(newUrl[self.count])
      else:
        self.crawl(newUrl[self.count+1])
  

if __name__ == "__main__":
    Crawler()