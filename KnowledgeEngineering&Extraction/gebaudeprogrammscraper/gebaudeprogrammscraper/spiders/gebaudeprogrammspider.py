import scrapy
import pandas as pd

class GebaudeSpider(scrapy.Spider):
    name = 'Gebaudeprogramm'
    start_urls = ['https://www.dasgebaeudeprogramm.ch/de/kantone/']

    def start_requests(self):
        kantone = ['aargau', 'appenzell-innerrhoden', 'appenzell-ausserrhoden', 'bern', 'basel-landschaft', 'basel-stadt', 'freiburg', 'geneve', 'glarus',
                   'graubuenden', 'jura', 'luzern', 'neuchatel', 'nidwalden', 'obwalden', 'st-gallen', 'schaffhausen', 'solothurn', 'schwyz', 'thurgau', 'ticino',
                   'uri', 'vaud', 'wallis', 'zug', 'zuerich']
        for kanton in kantone:
            yield scrapy.Request(url=f'https://www.dasgebaeudeprogramm.ch/de/kantone/{kanton}', callback=self.parse, meta={'kanton': kanton})

    def parse(self, response):
        kanton = response.meta['kanton']
        linkliste = response.css('li.supported-measures-teaser')

        if linkliste:
            for link in linkliste:
                yield {
                    'Kanton': kanton,
                    'Link': link.css('a::attr(href)').extract_first(),
                    'Name': link.xpath('normalize-space(.//span[@class="content"]/span[2]/text())').extract()
                }
        else:
            # Wenn keine Liste mit Massnahmen aufgeführt ist, dann ist der Link zur Kantonsinternetseite aufgeführt
            element_with_text = response.xpath('//a[contains(text(), "Zur Kantonsseite")]')

            if element_with_text:
                link = element_with_text.css('::attr(href)').extract_first()
                yield {
                    'Kanton': kanton,
                    'Link': link
                }
            else:
                self.log('Keine relevanten Elemente gefunden.')

"""
# Führe das Scrapy-Spider aus
from scrapy.crawler import CrawlerProcess
process = CrawlerProcess()
process.crawl(GebaudeSpider)
process.start()

"""