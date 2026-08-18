from douban_scraper import DoubanScraper

def test_douban_scraper():
    print("Starting Unit Test for DoubanScraper")
    db_password = input("Enter local MySQL 'root' password for testing: ")
    
    scraper = DoubanScraper(db_password)
    movies_data = scraper.get_movies()
    
    expected_length = 100
    expected_first_rank = 1
    
    if len(movies_data) == expected_length:
        print(f"Pass: Extracted ({len(movies_data)}) == Expected ({expected_length}) movies")
    else:
        print(f"Fail: Extracted ({len(movies_data)}) != Expected ({expected_length}) movies")
        
    if len(movies_data) > 0 and movies_data[0][0] == expected_first_rank:
        print(f"Pass: First rank ({movies_data[0][0]}) == Expected ({expected_first_rank})")
    else:
        print(f"Fail: First rank does not match Expected.")

if __name__ == '__main__':
    test_douban_scraper()