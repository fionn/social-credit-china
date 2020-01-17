#!/usr/bin/env python3

from selenium import webdriver # type: ignore
from selenium.webdriver.support.wait import WebDriverWait # type: ignore

URL = "https://www.creditchina.gov.cn/gerenxinyong/personsearch/index.html"

#"#page-500"

class CreditChina:
    """CC wrapper"""

    def __init__(self) -> None:
        self.url = "https://www.creditchina.gov.cn/gerenxinyong/personsearch/"
        self.driver = self._make_driver()

    @staticmethod
    def _make_driver() -> webdriver.Firefox:
        profile = webdriver.FirefoxProfile()
        profile.set_preference("http.response.timeout", 30)
        profile.set_preference("dom.max_script_run_time", 30)
        driver = webdriver.Firefox(firefox_profile=profile)
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(30)
        return driver

    def get(self, payload: str) -> None:
        """Getter"""
        response = self.driver.get(payload)
        wait = WebDriverWait(self.driver, timeout=30)
        wait.until(lambda x: x.find_element_by_id("gsr"))
        print(type(response))
        print(response)

def main() -> None:
    """Entry point"""
    ccn = CreditChina()

    payload = {"tablename": "credit_zgf_zrr_sxbzxr",
               "gsName": "%E5%A4%B1%E4%BF%A1%E8%A2%AB%E6%89%A7%E8%A1%8C%E4%BA%BA%E5%90%8D%E5%8D%95%E6%9F%A5%E8%AF%A2"}

    payload_str = f"?tablename={payload['tablename']}&gsName={payload['gsName']}"

    ccn.get(ccn.url + payload_str)
    ccn.driver.close()

if __name__ == "__main__":
    main()
