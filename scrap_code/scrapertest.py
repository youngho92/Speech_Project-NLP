##### This code is to scrap 968 US presidential speeches from the miller center #####

import scrapy

class TestSpider(scrapy.Spider):
    name = 'presidential_speeches'
    start_urls = ['https://millercenter.org/the-presidency/presidential-speeches?field_president_target_id[3]=3']

    ## presidential id on the miller website
    ids = [3, 4, 141] + list(range(6, 46))

    ## list of urls
    url_loop = ['https://millercenter.org/the-presidency/presidential-speeches?field_president_target_id[' + \
    str(id_temp) + ']=' + str(id_temp) for id_temp in ids]
    index = 0
    front_page = True


    def parse(self, response):
        ## Finished scrapping a specific president
        if self.front_page:
            self.front_page = False
            next_url = 'https://millercenter.org/' + response.xpath('//span[@class="field-content"]//a/@href').extract()[0]
            yield scrapy.Request(url=next_url, callback=self.parse)

        else:
            ## Extract the president name, title, and transcript of speeches
            presidency = response.xpath('//label[@class="presidential-speeches--label"]/text()').extract()[0]
            title = response.xpath('//h2[@class="presidential-speeches--title"]/span/text()').extract()[0]
            transcript = response.xpath('//div[@class="view-transcript"]//p/text()').extract()
            if not transcript:
                transcript = response.xpath('//div[@class="transcript-inner"]//p/text()').extract()
            yield {'presidency': presidency, 'title': title, 'transcript': transcript}

            ## if there exists a next speech, scrap it
            if response.xpath('//div[@class="prev"]//a/@href').extract():
                next_url = 'https://millercenter.org/' + response.xpath('//div[@class="prev"]//a/@href').extract()[0]
            else:
                next_url = []

            if next_url:
                yield scrapy.Request(url=next_url, callback=self.parse)
            else:
                self.front_page = True  # move to the next president
                self.index += 1
                next_url = self.url_loop[self.index]
                if self.index < len(self.url_loop):
                    yield scrapy.Request(url=next_url, callback=self.parse)
