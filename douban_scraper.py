import requests
from bs4 import BeautifulSoup
import re
from mysql_helper import MySqlHelper

class DoubanScraper:
    def __init__(self, db_password):
        self.base_url="https://movie.douban.com/top250?start={}"
        self.headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        self.db=MySqlHelper('localhost', 3306, 'root', db_password, 'crawler_db')

    def get_movies(self):
        movie_list=[]
        
        for page in range(4):
            start_num=page * 25
            url=self.base_url.format(start_num)
            
            try:
                response=requests.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    soup=BeautifulSoup(response.text, 'lxml')
                    items=soup.find_all('div', class_='item')
                    
                    if not items:
                        continue
                        
                    for item in items:
                        try:
                            #1.Extract rank
                            em_tag=item.find('em')
                            rank=int(em_tag.get_text()) if em_tag else 0
                            
                            #2.Extract movie title
                            title_tag=item.find('span', class_='title')
                            title=title_tag.get_text() if title_tag else "Unknown"
                            
                            bd=item.find('div', class_='bd')
                            if not bd:
                                continue
                            
                            #3.Extract release_year, country, genre using regex global match
                            release_year=0
                            country="Unknown"
                            genre="Unknown"
                            
                            p_tag=bd.find('p')
                            if p_tag:
                                p_text=p_tag.get_text(separator=' ')
                                #Regex match for the 4-digit year / country / genre pattern
                                match=re.search(r'(\d{4})\s*/\s*([^/]+)\s*/\s*([^/\n]+)', p_text)
                                if match:
                                    release_year=int(match.group(1))
                                    country=match.group(2).strip()
                                    genre=match.group(3).strip()
                            
                            #4.Extract rating
                            rating=0.0
                            rating_tag=bd.find('span', class_='rating_num')
                            if rating_tag:
                                try:
                                    rating=float(rating_tag.get_text().strip())
                                except ValueError:
                                    pass
                            
                            #5.Extract review count
                            review_count = 0
                            star_div = bd.find('div', class_='star')
                            if star_div:
                                review_match=re.search(r'(\d+)', star_div.get_text())
                                if review_match:
                                    review_count=int(review_match.group(1))
                            
                            #Assemble data and append to list
                            movie_list.append((rank, title, release_year, country, genre, rating, review_count))
                            
                        except Exception as e:
                            print(f"[Data extraction error] Movie: {title}, Error: {e}")
                            continue
                            
            except Exception as e:
                print(f"Network error - Page {page}: {e}")
                
        return movie_list

    def save_to_database(self, data_list):
        if not data_list:
            print("No data available to save.")
            return
            
        self.db.execute("TRUNCATE TABLE douban_top_100")
        insert_sql="""INSERT INTO douban_top_100 (rank_num, title, release_year, country, genre, rating, review_count) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        
        success_count=0
        for item in data_list:
            rows=self.db.execute(insert_sql, item)
            if rows>0:
                success_count+=1
                
        print(f"Successfully saved {success_count} records.")

    def run(self):
        print("Scraping Douban Top 100...")
        movies_data=self.get_movies()
        
        if movies_data:
            self.save_to_database(movies_data)

if __name__ == '__main__':
    password = input("Enter local MySQL root password: ")
    scraper = DoubanScraper(password)
    scraper.run()