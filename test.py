import unittest
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pyperclip
import json
import time


def convert_floats_to_ints(obj):
    if isinstance(obj, dict):
        return {k: convert_floats_to_ints(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_ints(i) for i in obj]
    elif isinstance(obj, float) and obj.is_integer():
        return int(obj)
    else:
        return obj


class RaindropDustAutomaticTest(unittest.TestCase):
    def setUp(self):
        self.service = EdgeService(executable_path= EdgeChromiumDriverManager().install())
        self.driver = webdriver.Edge(service=self.service)
        self.driver.implicitly_wait(0.5)
        self.wait = WebDriverWait(self.driver, 30)

    def table_template(self, x_path, http):
        self.driver.get("http://localhost:8501/dataset")
        time.sleep(2)

        self.wait.until(
            EC.presence_of_element_located((By.XPATH, x_path))
        )
        summary = self.driver.find_element(By.XPATH, x_path)
        summary.click()
        time.sleep(2)

        table_values = []

        for i in range(4):
            element = self.wait.until(
                EC.presence_of_element_located((By.ID, f"glide-cell-{i + 1}-0"))
            )
            value = element.get_attribute("textContent").strip()
            table_values.append(value)

        self.driver.get(http)
        time.sleep(2)

        pre_element = self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "pre"))
        )
        json_text = pre_element.text

        data = json.loads(json_text)
        clean_data = convert_floats_to_ints(data)
        data_format = json.dumps(clean_data, separators=(',', ':'))
        parsed_data = json.loads(data_format)
        if parsed_data:
            values = [str(v) for v in list(parsed_data[0].values())[:4]]

        self.assertTrue(values == table_values, msg="The table values don't match the expected values.")

    def api_endpoint_template(self, api_endpoint, http, valid):
        self.driver.get("http://localhost:8501/api")
        time.sleep(2)

        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(text(), 'timestamp') or contains(text(), '[]')]")
            )
        )
        input_element = self.wait.until(
            EC.element_to_be_clickable((By.ID, "text_input_1"))
        )
        input_element.click()
        time.sleep(2)

        self.driver.execute_script("arguments[0].value = '';", input_element)
        time.sleep(2)

        input_element.send_keys(api_endpoint, Keys.ENTER)
        time.sleep(2)

        if valid != 1:
            error_text = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[text()='Invalid API Path']"))
            )
            time.sleep(2)

            self.assertTrue("Invalid API Path" == error_text.text, msg="The Invalid API Path text doesn't show up.")
        else:
            self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(text(), 'timestamp') or contains(text(), '[]')]")
                )
            )
            time.sleep(2)

            json_element = self.driver.find_element(By.CLASS_NAME, "pretty-json-container")
            actions = ActionChains(self.driver)
            actions.move_to_element(json_element).perform()
            time.sleep(2)

            copy_icon = self.driver.find_element(By.CSS_SELECTOR, "span.copy-icon svg")
            copy_icon.click()
            time.sleep(2)

            copied_data = pyperclip.paste()
            time.sleep(2)

            self.driver.get(http)
            time.sleep(2)

            pre_element = self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "pre"))
            )
            json_text = pre_element.text

            data = json.loads(json_text)
            clean_data = convert_floats_to_ints(data)
            data_format = json.dumps(clean_data, separators=(',', ':'))

            self.assertTrue(data_format == copied_data, msg="The data doesn't match the expected data.")

    def test_open_home_page(self):
        self.driver.get("http://localhost:8501/")
        time.sleep(2)

        title = self.wait.until(
            EC.presence_of_element_located((By.ID, "current-condition"))
        )

        self.assertEqual("Current Condition", title.text)

    def test_open_descriptive(self):
        self.driver.get("http://localhost:8501/descriptive")
        time.sleep(2)

        title = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='AQI Line Chart']"))
        )

        self.assertEqual("AQI Line Chart", title.text)

    def test_open_dataset(self):
        self.driver.get("http://localhost:8501/dataset")
        time.sleep(2)

        heading = self.wait.until(
            EC.presence_of_element_located((By.ID, "dataset-tables"))
        )

        self.assertEqual("Dataset & Tables", heading.text)

    def test_open_api(self):
        self.driver.get("http://localhost:8501/api")
        time.sleep(2)

        title = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[text()='Enter API Path']"))
        )

        self.assertEqual("Enter API Path", title.text)

    def test_chart(self):
        self.driver.get("http://localhost:8501/descriptive")
        time.sleep(2)

        zoom_in_button = self.wait.until(
            EC.presence_of_element_located((By.XPATH, "//a[@data-title='Zoom in']"))
        )

        before = self.driver.execute_script("""
        const rect = Array.from(document.querySelectorAll('rect'))
        .find(r => r.getAttribute('class') === 'nsewdrag drag');
        if (!rect) return null;
        return {
        width: rect.getAttribute('width'),
        x: rect.getAttribute('x')
        };
        """)

        for _ in range(3):
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", zoom_in_button)
            time.sleep(1)

        after = self.driver.execute_script("""
        const rect = Array.from(document.querySelectorAll('rect'))
        .find(r => r.getAttribute('class') === 'nsewdrag drag');
        if (!rect) return null;
        return {
        width: rect.getAttribute('width'),
        x: rect.getAttribute('x')
        };
        """)

        self.assertTrue((before['width'] != after['width']) or (before['x'] != after['x']))

    def test_primary_table(self):
        self.table_template("//div[@data-testid='stExpander']//p[text()='Primary Table']",
                            "http://localhost:8000/raw/primary")

    def test_secondary_table(self):
        self.table_template("//div[@data-testid='stExpander']//p[text()='Secondary Table']",
                            "http://localhost:8000/raw/secondary")

    def test_hourly_table(self):
        self.table_template("//div[@data-testid='stExpander']//p[text()='Hourly Table']",
                            "http://localhost:8000/raw/hourly")

    def test_valid_api(self):
        self.api_endpoint_template("/data/latest?limit=2",
                                   "http://localhost:8000/data/latest?limit=2",
                                   1)

    def test_invalid_api(self):
        self.api_endpoint_template("/data/late?",
                                   "http://localhost:8000/data/late?",
                                   0)

    def test_data_latest(self):
        self.api_endpoint_template("/data/latest?limit=5",
                                   "http://localhost:8000/data/latest?limit=5",
                                   1)

    def test_data(self):
        self.api_endpoint_template("/data?start_date=2025-04-01&end_date=2025-04-03&skip=0&limit=2",
                                   "http://localhost:8000/data?start_date=2025-04-01&end_date=2025-04-03&skip=0&limit=2",
                                   1)

    def test_forecast_1day(self):
        self.api_endpoint_template("/forecast/1day?limit=5",
                                   "http://localhost:8000/forecast/1day?limit=5",
                                   1)

    def test_raw_secondary(self):
        self.api_endpoint_template("/raw/secondary?limit=3&sort=1",
                                   "http://localhost:8000/raw/secondary?limit=3&sort=1",
                                   1)

    def test_boundary_api(self):
        self.api_endpoint_template("/data/aqi?start_date=2025-04-11&end_date=2025-04-11",
                                   "http://localhost:8000/data/aqi?start_date=2025-04-11&end_date=2025-04-11",
                                   1)

    def tearDown(self):
        self.driver.quit()


if __name__ == '__main__':
    unittest.main()
