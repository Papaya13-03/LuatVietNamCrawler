from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from dataclasses import dataclass
from typing import List
import json
import os
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@dataclass
class Question:
    title: str
    link: str
    create_date: str
    id: int

class Crawler:
    def __init__(self, questions: List[Question]):
        self.questions = questions  
        self.driver = self.init_driver()

    def init_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')  # hoặc thử --headless nếu vẫn lỗi
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )

        return webdriver.Chrome(options=chrome_options)

    def get_answer(self, question: Question):
        try:
            self.driver.get(question.link)

            wait = WebDriverWait(self.driver, 10)
            answer_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.the-article-body'))
            )
            answer = answer_element.text

            link_elements = self.driver.find_elements(By.CSS_SELECTOR, '.the-article-body a')
            related_links = [
                {
                    "tag": link.text,
                    "url": link.get_attribute("href")
                }
                for link in link_elements
            ]

            transformed_related_links = [
                link for link in related_links
                if link["url"] and not link["url"].startswith("tel:")
            ]

            return {
                "question_id": question.id,
                "answer": answer,
                "related_links": transformed_related_links
            }

        except Exception as e:
            print(f"Error fetching data from {question.id}: {e}")
            return None


    def write_to_file(self, data: dict, file_path: str):
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        existing_data.append(data)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)

    def process_qna(self, output_file="result.json"):
        for question in self.questions:
            print(f"Processing QnA ID: {question.id}")
            data = self.get_answer(question)
            self.write_to_file(data, output_file)
        self.shutdown()

    def shutdown(self):
        self.driver.quit()



def load_qna_from_json(file_path: str) -> List[Question]:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)  
        qna_list = [Question(**item) for item in data]  
    return qna_list

if __name__ == "__main__":
    qna_list = load_qna_from_json('QnA_links.json')  
    crawler = Crawler(questions=qna_list)
    crawler.process_qna()
