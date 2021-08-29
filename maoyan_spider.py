# -*- coding:utf-8 -*-

import re
import requests
from scrapy import Selector
from fontTools.ttLib import TTFont
from font_model.font_knn import Classify


class MaoYanSpider(object):
    def __init__(self):
        self.classify = Classify()
        self.url = 'https://maoyan.com/board/1'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
        }
        self.response = self.send_request()
        self.num_map = self.get_num_map()

    def send_request(self):
        response = requests.get(
            url=self.url,
            headers=self.headers
        )
        return response
    
    def save_font_file(self):
        font_file = 'http:' + re.findall(r'url\(\'(.*?)\'\) format\(\'woff\'\);', self.response.text)[0]
        font_name = font_file.rsplit('/', 1)[1]
        with open(font_name, 'wb') as file:
            file.write(requests.get(font_file).content)
        return font_name
     
    def get_num_map(self):
        datas = []
        font = TTFont(self.save_font_file())
        glyph_orders = font.getGlyphOrder()[2:]
        for index, glyph_order in enumerate(glyph_orders):
            points = font['glyf'][glyph_order].coordinates
            coors = [_ for c in points for _ in c]
            datas.append(coors)
        glyph_orders = [item.lower().replace('uni', '') for item in glyph_orders]
        nums = [str(int(num)) for num in self.classify.knn_predict(datas)[:10]]
        num_map = dict(zip(glyph_orders, nums))
        return num_map

    def get_num_from_font(self, string):
        for name, num in self.num_map.items():
            num_str = re.sub(name, num, string)
            string = num_str
        return string

    def parse_movie(self):
        movies = Selector(text=self.response.content).xpath('//div[@class="board-item-content"]').extract()
        for movie in movies:
            info = Selector(text=movie)
            name = info.xpath('//p[@class="name"]/a/text()').extract_first()
            star = info.xpath('//p[@class="star"]/text()').extract_first()
            releasetime = info.xpath('//p[@class="releasetime"]/text()').extract_first()
            realtime_boxoffice_num = info.xpath('//p[@class="realtime"]/span/span/text()').extract_first().encode('unicode-escape').decode()
            realtime_boxoffice_unit = info.xpath('//p[@class="realtime"]/text()').extract()
            realtime_boxoffice_unit.insert(1, self.get_num_from_font(realtime_boxoffice_num))
            realtime_boxoffice_unit = ''.join(realtime_boxoffice_unit).replace(' ', '').replace('\n', '').replace('\\u', '')
            total_boxoffice_num = info.xpath('//p[@class="total-boxoffice"]/span/span/text()').extract_first().encode('unicode-escape').decode()
            total_boxoffice_unit = info.xpath('//p[@class="total-boxoffice"]/text()').extract()
            total_boxoffice_unit.insert(1, self.get_num_from_font(total_boxoffice_num))
            total_boxoffice_unit = ''.join(total_boxoffice_unit).replace(' ', '').replace('\n', '').replace('\\u', '')
            print('{}\n{}\n{}\n{}\n{}'.format(name, star, releasetime, realtime_boxoffice_unit, total_boxoffice_unit))
            print('=' * 60)


if __name__ == '__main__':
    maoyan = MaoYanSpider()
    maoyan.parse_movie()
