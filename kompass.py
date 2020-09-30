import scrapy
import pandas as pd
from scrapy import Request
import gspread
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings



s = get_project_settings()
s['DOWNLOAD_DELAY'] = '10'
s['USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'

gc = gspread.service_account(filename='creds.json')
sh = gc.open('kompass-final').get_worksheet(0)
sh.clear()
sh2 = gc.open('kompass-final').get_worksheet(1)
header = ['Company','Company-Activity','Address','Code','URL','Year of Creation','SIREN','Workforce at Address','Managers']
sh.append_row(header,1)
urlvalue = sh2.acell('A2').value



class KompassSpider(scrapy.Spider):
  name = 'kompass'
  page_number = 2
  start_urls = [urlvalue]

  def parse(self, response):
    links  = response.css('.company-container > h2 > a::attr(href)').getall()
    for link in links:
      yield scrapy.Request(url=link, callback=self.parse_list)
    next_page = str(urlvalue) + 'page-' + str(KompassSpider.page_number) + '/'
    if KompassSpider.page_number <= 20:
      KompassSpider.page_number += 1
      yield Request(url = next_page, callback = self.parse)



  def parse_list(self, response):
    try:
      table = response.css('table').getall()[0]
    except:
      table = response.css('table').getall()

    df = pd.read_html(str(table))
    try:
      company = response.css('.blockNameCompany > h1::text').getall()[0].strip()
    except:
      company = response.css('.blockNameCompany > h1::text').getall()
    try:
      company_activity = response.css('.company-activities::text').getall()[0].strip()
    except:
      company_activity = response.css('.company-activities::text').getall()
    try:  
      year = df[0].values[1][1]
    except:
      year = "Not Available"
    company_url = response.url
    address1 = response.css('.blockAddress > span.spRight >span::text').getall()
    address1 = list(map(str.strip, address1))
    address1 = ' '.join([str(elem) for elem in address1])
    address2 = response.css('.blockAddress > span.spRight::text').getall()[-2].strip()
    address = str(address1) + ',' + str(address2)
    code = response.css('.blockAddress > span.spRight::text').getall()[-2].strip()[0:4]
    try:
      siren = df[0].values[5][1]
    except:
      siren = "Not Available" 
    try:
      workforce = df[0].values[8][1] 
    except:
      workforce = df[0].values[-2][1]   

    managers = response.css('.executiveName::text').getall()
    managers = list(map(str.strip, managers))
    managers =','.join([str(elem) for elem in managers]) 
      
    yield{
      'Company' : company,
      'Comapny-Activity' : company_activity,
      'Address' : address,
      'Code' : code,
      'URL' : company_url,
      'Year of Creation' : year,
      'SIREN' : siren,
      'Workforce at Address' : workforce,
      'Managers' : managers,
    }

    

    sh.append_row([company, company_activity, address, code, company_url, year, siren, workforce, managers],2)




if __name__ == '__main__':
  process = CrawlerProcess(s)
  process.crawl(KompassSpider)
  process.start()



    

   

   

      

