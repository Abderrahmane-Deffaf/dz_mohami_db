# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DzmohamiItem(scrapy.Item):
    name = scrapy.Field()
    fname = scrapy.Field()
    email = scrapy.Field()
    phone = scrapy.Field()
    address = scrapy.Field()
    description = scrapy.Field()
    avocat_image = scrapy.Field()
    categories = scrapy.Field()
    schedule = scrapy.Field()
    rating = scrapy.Field()
    comments = scrapy.Field()
    social = scrapy.Field()
    wilaya = scrapy.Field()
    longitude = scrapy.Field()
    latitude = scrapy.Field()

    pass
class OktobitItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class PcItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    cpu = scrapy.Field()
    ram = scrapy.Field()
    storage = scrapy.Field()
    screen = scrapy.Field()
    integrated_gpu = scrapy.Field()
    dedicated_gpu = scrapy.Field()
    rate = scrapy.Field()
    marque = scrapy.Field()
    source = scrapy.Field()
    location = scrapy.Field()
    date = scrapy.Field() 
    etat = scrapy.Field()
    images = scrapy.Field()


