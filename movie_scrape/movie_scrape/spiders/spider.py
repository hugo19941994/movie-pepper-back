import scrapy
from .. import items


class Spider(scrapy.Spider):
    name = 'spider'
    start_urls = [
        'http://www.imdb.com/search/title?groups=top_1000&sort=user_rating,'
        'desc&page=1&ref'
    ]

    def parse(self, response):
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
        reviews_url = response.urljoin(response.xpath('//*[@id="titleUserReviewsTeaser"]/div/div[3]/a[2]/@href').extract_first())
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
        item['plot'] = ''.join(response.xpath('//*[@id="swiki.2.1"]/text()').extract())

        request3 = scrapy.Request(response.meta['reviews_url'],
                                  callback=self.extract_reviews,
                                  meta={'item': item},
                                  priority=3)
        yield request3

    def extract_reviews(self, response):
        item = response.meta['item']
        item['reviews'] = []

        # 3 pages -> 30 reviews
        urls = []
        for url in response.xpath('//*[@id="tn15content"]/table[1]/tr/td[2]//a/@href').extract()[:3]:
            urls.append(url)

        request4 = scrapy.Request(response.urljoin(urls.pop()),
                                  callback=self.extract_reviews_page,
                                  meta={'item': item, 'urls': urls},
                                  priority=4)
        yield request4

    def extract_reviews_page(self, response):
        item = response.meta['item']

        for review in response.xpath('//*[@id="tn15content"]//p'):
            item['reviews'].append(''.join(review.xpath('./text()').extract()))

        if len(response.meta['urls']) == 0:
            yield item
        else:
            request4 = scrapy.Request(response.urljoin(response.meta['urls'].pop()),
                                    callback=self.extract_reviews_page,
                                    meta={'item': item, 'urls': response.meta['urls']},
                                    priority=4)
            yield request4

