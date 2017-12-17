import scrapy
import os
from scrapy.http import Request
from .. import items


class Spider(scrapy.Spider):
    name = 'spider'
    allowed_domains = ["imdb.com"]
    start_urls = [os.environ["START_URL"]]

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, dont_filter=False)

    def parse(self, response):
        print("URL: " + response.url)
        for movie_url in response.css('.lister-item-header a::attr(href)') \
                .extract():
            yield scrapy.Request(response.urljoin(movie_url),
                                 callback=self.parse_movie,
                                 dont_filter=True)

        url = response.css('.next-page::attr(href)').extract_first()
        yield scrapy.Request(response.urljoin(url),
                             callback=self.parse,
                             dont_filter=True)

    def parse_movie(self, response):
        key_url = response.css('div[itemprop="keywords"] nobr a::attr(href)').extract_first()

        item = items.Movie()
        item['url'] = response.url
        item['title'] = response.css('.title_wrapper h1::text').extract_first().replace(u'\u00a0', '')
        item['rating'] = response.css('.ratingValue strong span::text').extract_first()
        item['genres'] = list(map(str.lstrip, response.css('div[itemprop="genre"] a::text').extract()))
        item['year'] = response.css('#titleYear a::text').extract_first()
        item['director'] = response.css('span[itemprop="director"] a span::text').extract_first()
        poster = response.xpath('//*[@id="title-overview-widget"]/div[2]/div[3]/div[1]/a/img/@src').extract_first()
        if poster is None:
            poster = response.xpath('//*[@id="title-overview-widget"]/div[3]/div[1]/a/img/@src').extract_first()
        item['poster'] = poster

        plot_url = response.urljoin(response.xpath('//*[@id="titleStoryLine"]/span[2]/a[2]/@href').extract_first())
        reviews_url = response.urljoin(response.xpath('//*[@id="titleUserReviewsTeaser"]/div/a[2]/@href').extract_first())
        request = scrapy.Request(response.urljoin(key_url),
                                 callback=self.extract_keywords,
                                 meta={'item': item,
                                       'plot_url': plot_url,
                                       'reviews_url': reviews_url},
                                 priority=1)
        yield request

    def extract_keywords(self, response):
        item = response.meta['item']
        item['keywords'] = response.css('.sodatext a::text').extract()
        request2 = scrapy.Request(response.meta['plot_url'],
                                  callback=self.extract_plot,
                                  meta={'item': item,
                                        'reviews_url': response.meta['reviews_url']},
                                  priority=2)
        yield request2

    def extract_plot(self, response):
        item = response.meta['item']
        item['plot'] = ''.join(response.xpath('//*[@id="plot-synopsis-content"]/li/text()').extract())

        request3 = scrapy.Request(response.meta['reviews_url'],
                                  callback=self.extract_reviews,
                                  meta={'item': item},
                                  priority=3)
        yield request3

    def extract_reviews(self, response):
        item = response.meta['item']
        item['reviews'] = []

        # By default 9 reviews are loaded. To load more JS must be loaded
        # and .ipl-load-more__button must be pressed
        # TODO: use js to press buton

        urls = []
        try:
            item['reviews'] = response.css('.text::text').extract()
            yield item

        except:
            yield item
