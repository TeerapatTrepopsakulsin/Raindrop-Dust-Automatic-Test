import unittest
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


class RaindropDustAutomaticTest(unittest.TestCase):
    def setUp(self):
        self.service = EdgeService(executable_path= EdgeChromiumDriverManager().install())
        self.driver = webdriver.Edge(service=self.service)
        self.driver.implicitly_wait(0.5)

    def test_open_home_page(self):
        self.driver.get("http://localhost:8501/")
        time.sleep(3)
        title = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='AQI Line Chart']"))
        )
        self.assertEqual("AQI Line Chart", title.text)

    # def test_open_predictive(self):
        # self.driver.get("http://localhost:8501/predictive")
        # time.sleep(3)

    def test_open_dataset(self):
        self.driver.get("http://localhost:8501/dataset")
        time.sleep(3)
        heading = self.driver.find_element(By.ID, "dataset-tables")
        self.assertEqual("Dataset & Tables", heading.text)

    def test_open_api(self):
        self.driver.get("http://localhost:8501/api")
        time.sleep(3)
        title = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Enter API Path']"))
        )
        self.assertEqual("Enter API Path", title.text)

    # def test_open_api_docs(self):
        # self.driver.get("http://localhost:8501/api_docs")
        # time.sleep(3)

    def test_chart_zoom_in(self):
        self.driver.get("http://localhost:8501/")
        wait = WebDriverWait(self.driver, 20)

        zoom_in_button = wait.until(
            EC.presence_of_element_located((By.XPATH, "//a[@data-title='Zoom in']"))
        )

        rect = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "g.xy > rect.nsewdrag")))
        initial_width = float(rect.get_attribute("width"))

        for i in range(5):
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", zoom_in_button)

        time.sleep(1)

        rect_after = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "g.xy > rect.nsewdrag")))
        new_width = float(rect_after.get_attribute("width"))

        self.assertTrue(new_width > initial_width)

    def test_primary_table(self):
        self.driver.get("http://localhost:8501/dataset")

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-testid='stExpander']//p[text()='Primary Table']"))
        )

        summary = self.driver.find_element(
            By.XPATH,
            "//div[@data-testid='stExpander']//p[text()='Primary Table']"
        )
        summary.click()
        time.sleep(1)

        # check data

    def test_secondary_table(self):
        self.driver.get("http://localhost:8501/dataset")

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-testid='stExpander']//p[text()='Secondary Table']"))
        )

        summary = self.driver.find_element(
            By.XPATH,
            "//div[@data-testid='stExpander']//p[text()='Secondary Table']"
        )
        summary.click()
        time.sleep(1)

        # check data

    def test_hourly_table(self):
        self.driver.get("http://localhost:8501/dataset")

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@data-testid='stExpander']//p[text()='Hourly Table']"))
        )

        summary = self.driver.find_element(
            By.XPATH,
            "//div[@data-testid='stExpander']//p[text()='Hourly Table']"
        )
        summary.click()
        time.sleep(1)

        # check data

    def test_valid_api_path(self):
        self.driver.get("http://localhost:8501/api")

        wait = WebDriverWait(self.driver, 20)

        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'timestamp') or contains(text(), '[]')]")
            )
        )
        time.sleep(2)

        input_element = wait.until(
            EC.element_to_be_clickable((By.ID, "text_input_1"))
        )

        input_element.click()
        self.driver.execute_script("arguments[0].value = '';", input_element)
        time.sleep(2)

        input_element.send_keys("/data/latest?limit=2", Keys.ENTER)
        time.sleep(5)
        # check data

    def test_invalid_api_path(self):
        self.driver.get("http://localhost:8501/api")

        wait = WebDriverWait(self.driver, 20)

        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'timestamp') or contains(text(), '[]')]")
            )
        )
        time.sleep(2)

        input_element = wait.until(
            EC.element_to_be_clickable((By.ID, "text_input_1"))
        )

        input_element.click()
        self.driver.execute_script("arguments[0].value = '';", input_element)
        time.sleep(2)

        input_element.send_keys("/data/late?", Keys.ENTER)
        time.sleep(5)

        error_text = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Invalid API Path']"))
        )
        self.assertEqual("Invalid API Path", error_text.text)

    def test_data_latest(self):
        self.driver.get("http://localhost:8501/api")

        wait = WebDriverWait(self.driver, 20)

        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'timestamp') or contains(text(), '[]')]")
            )
        )
        time.sleep(2)

        input_element = wait.until(
            EC.element_to_be_clickable((By.ID, "text_input_1"))
        )

        input_element.click()
        self.driver.execute_script("arguments[0].value = '';", input_element)
        time.sleep(2)

        input_element.send_keys("/data/latest?limit=5", Keys.ENTER)
        time.sleep(5)
        # check data

    def test_data(self):
        self.driver.get("http://localhost:8501/api")

        wait = WebDriverWait(self.driver, 20)

        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'timestamp') or contains(text(), '[]')]")
            )
        )
        time.sleep(2)

        input_element = wait.until(
            EC.element_to_be_clickable((By.ID, "text_input_1"))
        )

        input_element.click()
        self.driver.execute_script("arguments[0].value = '';", input_element)
        time.sleep(2)

        input_element.send_keys("/data?start_date=2025-04-01&end_date=2025-04-03&skip=0&limit=2", Keys.ENTER)
        time.sleep(5)
        # check data

    def test_forecast_1day(self):
        self.driver.get("http://localhost:8501/api")

        wait = WebDriverWait(self.driver, 20)

        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'timestamp') or contains(text(), '[]')]")
            )
        )
        time.sleep(2)

        input_element = wait.until(
            EC.element_to_be_clickable((By.ID, "text_input_1"))
        )

        input_element.click()
        self.driver.execute_script("arguments[0].value = '';", input_element)
        time.sleep(2)

        input_element.send_keys("/forecast/1day?limit=5", Keys.ENTER)
        time.sleep(5)
        # check data

    def test_raw_secondary(self):
        self.driver.get("http://localhost:8501/api")

        wait = WebDriverWait(self.driver, 20)

        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'timestamp') or contains(text(), '[]')]")
            )
        )
        time.sleep(2)

        input_element = wait.until(
            EC.element_to_be_clickable((By.ID, "text_input_1"))
        )

        input_element.click()
        self.driver.execute_script("arguments[0].value = '';", input_element)
        time.sleep(2)

        input_element.send_keys("/raw/secondary?limit=3&sort=1", Keys.ENTER)
        time.sleep(5)
        # check data


if __name__ == '__main__':
    unittest.main()
