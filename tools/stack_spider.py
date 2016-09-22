import time
from scrapy import Spider
from scrapy.selector import Selector

from items import StackItem
from selenium import webdriver
from pprint import pprint



class StackSpider(Spider):
    name = "stack"
    allowed_domains = ["stackoverflow.com"]
    start_urls = [
        "http://stackoverflow.com/questions?pagesize=50&sort=newest",
    ]

    def __init__(self):
        self.driver = webdriver.Firefox()

    def parse(self, response):
        self.driver.get(response.url)
        #time.sleep(3)
        questions = self.driver.find_elements_by_xpath('//div[@class="summary"]/h3')

        for question in questions:
            #print question
            #pprint (vars(question))
            item = StackItem()
            item['title'] = question.find_element_by_xpath('a[@class="question-hyperlink"]').get_attribute('text')   #.extract()[0]
            item['url'] = question.find_element_by_xpath('a[@class="question-hyperlink"]').get_attribute('href')  
			           
            yield item