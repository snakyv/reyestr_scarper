import scrapy

class DecisionItem(scrapy.Item):
    case_number = scrapy.Field()  # номер справи
    date        = scrapy.Field()  # дата ухвалення/постановлення
    summary     = scrapy.Field()  # короткий опис (зі сторінки рішення)
    url         = scrapy.Field()  # посилання на рішення (Review/..)
