import csv
import codecs


class CsvPipeline:
    def __init__(self):
        self.file = codecs.open("output/movie.csv", 'w', encoding='utf-8-sig')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['Title', 'Genre', 'Synopsis'])  # CSV 파일의 헤더

    def process_item(self, item, spider):
        title = item.get('title')
        genre = item.get('genre')
        synopsis = item.get('synopsis')

        self.writer.writerow([title, genre, synopsis])

        return item

    def close_spider(self, spider):
        self.file.close()
