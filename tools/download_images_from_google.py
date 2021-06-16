from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests
import os
import time

class WrongExt(Exception):
    pass

def main(categories):
    driver = webdriver.Chrome('chromedriver.exe')
    for category in categories:
        path = os.path.join("../pics", category)
        if not os.path.exists(path):
            os.makedirs(path)
        with open(f'words/{category}.txt') as f:
            words = f.readlines()

        word_success = False
        index = 1
        word_index = 0
        all_movies = os.listdir(path)
        all_movies = list(map(lambda x: x.lower(), all_movies))
        while not word_success and word_index < len(words):
            word = words[word_index].strip("\n")
            if index > 100 or f"{word}.jpg" in all_movies or f"{word}.jpeg" in all_movies or word == '':
                word_index += 1
                index = 1
                continue

            driver.get('https://www.google.com/imghp?hl=en&tab=ri&authuser=0&ogbl')
            box = driver.find_element_by_xpath('//*[@id="sbtc"]/div/div[2]/input')
            box.send_keys(word)
            box.send_keys(Keys.ENTER)
            # driver.fullscreen_window()
            try:
                driver.find_element_by_xpath(f'//*[@id="islrg"]/div[1]/div[{index}]/a[1]/div[1]/img').click()
                img = driver.find_element_by_xpath('//*[@id="Sva75c"]/div/div/div[3]/div[2]/c-wiz/div/div[1]/div[1]/div/div[2]/a/img')
                no_source = True
                in_counter = 0
                while no_source:
                    try:
                        time.sleep(1)
                        in_counter += 1
                        image_src = img.get_property("src")
                        ext = image_src.split(".")[-1]
                        if ext not in ['jpg', 'jpeg']:
                            raise WrongExt()
                        res = requests.get(image_src)
                        with open(f"{path}/{word}.{ext}", "wb") as f:
                            f.write(res.content)
                        word_index += 1
                        no_source = False
                        index = 1
                    except WrongExt:
                        no_source = False
                        index += 1
                    except Exception:
                        print(f"{word} Failed {in_counter}")
                        if in_counter == 10:
                            no_source = False
                            index += 1

            except:
                index += 1
                print(words[word_index])



    driver.close()

if __name__ == '__main__':
    main(["ספורטאים"])