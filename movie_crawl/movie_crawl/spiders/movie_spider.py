import re
import time
import scrapy
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MovieSpider(scrapy.Spider):
    name = "movie"
    allowed_domains = ["kobis.or.kr"]
    start_urls = ["https://www.kobis.or.kr/kobis/business/mast/mvie/searchMovieList.do"]

    def __init__(self, *args, **kwargs):
        super(MovieSpider, self).__init__(*args, **kwargs)
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        self.driver = webdriver.Chrome(options=options)

    def closed(self, reason):
        self.driver.quit()

    def parse(self, response, **kwargs):
        url = "https://www.kobis.or.kr/kobis/business/mast/mvie/searchMovieList.do"
        self.driver.get(url)

        # 페이지 로딩될 때까지 잠시 대기
        time.sleep(1)

        # 크롤링 전 필터링
        def click_btn(xpath):
            btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            btn.click()

        def load_item(xpath):
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, xpath))
            )

        # 검색 필터 '더보기' 버튼 클릭
        click_btn('//*[@id="content"]/div[3]/div[2]/a[1]')

        # 제작 상태 '개봉' 필터링
        click_btn('//*[@id="sPrdtStatStr"]')
        click_btn('//*[@id="mul_chk_det0"]')
        click_btn('//*[@id="layerConfirmChk"]')
        time.sleep(1)

        # 장르 제외 필터링
        click_btn('//*[@id="sGenreStr"]')
        load_item('//*[@id="tblChk"]')
        click_btn('//*[@id="chkAllChkBox"]')
        time.sleep(1)
        click_btn('//*[@id="mul_chk_det18"]')
        click_btn('//*[@id="mul_chk_det19"]')
        click_btn('//*[@id="mul_chk_det20"]')
        time.sleep(1)
        click_btn('//*[@id="layerConfirmChk"]')
        time.sleep(1)

        # 국적1(한국) 선택
        click_btn('//*[@id="sNationStr"]')
        load_item('//*[@id="tblChk"]')
        time.sleep(1)
        click_btn('//*[@id="mul_chk_det2"]')
        time.sleep(1)
        click_btn('//*[@id="layerConfirmChk"]')
        time.sleep(1)

        # 국적2(한국) 선택
        click_btn('//*[@id ="sRepNationStr"]')
        load_item('//*[@id="tblChk"]')
        time.sleep(1)
        click_btn('//*[@id="mul_chk_det2"]')
        time.sleep(1)
        click_btn('//*[@id="layerConfirmChk"]')
        time.sleep(1)

        # 등급 필터링
        click_btn('//*[@id="searchForm"]/div[2]/div[5]/div')
        # 2006-10-29~현재
        click_btn('//*[@id="mul_chk_det2"]')
        click_btn('//*[@id="mul_chk_det3"]')
        click_btn('//*[@id="mul_chk_det4"]')
        click_btn('//*[@id="mul_chk_det5"]')
        time.sleep(1)
        # 2002-05-01~2006-10-28
        click_btn('//*[@id="mul_chk_det10"]')
        click_btn('//*[@id="mul_chk_det11"]')
        click_btn('//*[@id="mul_chk_det12"]')
        click_btn('//*[@id="mul_chk_det13"]')
        time.sleep(1)
        # 2002-05-01~2006-10-28
        click_btn('//*[@id="mul_chk_det17"]')
        click_btn('//*[@id="mul_chk_det18"]')
        click_btn('//*[@id="mul_chk_det19"]')
        click_btn('//*[@id="mul_chk_det20"]')
        time.sleep(1)
        click_btn('//*[@id="layerConfirmChk"]')
        time.sleep(1)

        # 영화 종류 필터링
        click_btn('//*[@id="searchForm"]/div[2]/div[8]/div/label[2]')
        click_btn('//*[@id="searchForm"]/div[2]/div[8]/div/label[3]')
        time.sleep(1)

        # 필터링 후 검색
        click_btn('//*[@id="searchForm"]/div[1]/div[5]/button[1]')
        time.sleep(1)

        # 크롤링 시작
        # 페이지 순회
        while True:
            for page_number in range(1, 11):
                page_number_xpath = f'//*[@id="pagingForm"]/div/ul/li[{page_number}]'

                page_number_link = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, page_number_xpath))
                )
                page_number_link.click()

                # 페이지 로딩 대기
                time.sleep(1)

                # 각 페이지 테이블 내용 순회
                movie_rows = self.driver.find_elements(By.XPATH, '//*[@id="content"]/div[4]/table/tbody/tr')
                for idx, row in enumerate(movie_rows, start=1):
                    movie_detail_xpath = f'//*[@id="content"]/div[4]/table/tbody/tr[{idx}]/td[1]/span/a'

                    movie_detail_link = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, movie_detail_xpath))
                    )
                    movie_detail_link.click()

                    # 장르 가져오기
                    genre_info_xpath = '/html/body/div[3]/div[2]/div/div[1]/div[2]/dl/dd[4]'
                    genre_info = self.driver.find_element(By.XPATH, genre_info_xpath).text
                    genre_pattern = re.compile(r'\|\s*[^|]+\s*\|\s*([^|]+)\s*\|')
                    match = genre_pattern.search(genre_info)
                    genre = match.group(1).strip()

                    if '성인물(에로)' in genre or '공연' in genre:
                        # 모달창 닫기
                        close_btn = '/html/body/div[3]/div[1]/div[1]/a[2]'
                        self.driver.find_element(By.XPATH, close_btn).click()
                        continue

                    else:
                        # 제목 가져오기
                        title_xpath = '/html/body/div[3]/div[1]/div[1]/div/strong'
                        title = self.driver.find_element(By.XPATH, title_xpath).text

                        # 시놉시스 가져오기
                        synopsis_xpath = '/html/body/div[3]/div[2]/div/div[1]/div[5]/p'
                        try:
                            synopsis = self.driver.find_element(By.XPATH, synopsis_xpath).text
                        except NoSuchElementException:
                            # 시놉시스가 없는 경우 크롤링 제외(모달창 닫기)
                            close_btn = '/html/body/div[3]/div[1]/div[1]/a[2]'
                            self.driver.find_element(By.XPATH, close_btn).click()
                            continue

                        # 모달창 닫기
                        close_btn = '/html/body/div[3]/div[1]/div[1]/a[2]'
                        self.driver.find_element(By.XPATH, close_btn).click()

                        # 가져온 정보를 yield하여 Scrapy 아이템으로 전달
                        yield {
                            'title': title.strip(),
                            'genre': genre.strip(),
                            'synopsis': synopsis.strip()
                        }

            # 페이지 넘기기 버튼 클릭
            try:
                click_btn('//*[@id="pagingForm"]/div/a[3]')
                time.sleep(1)
            except TimeoutException:
                # 다음 페이지 버튼이 없으면 종료
                self.driver.close()
                return
