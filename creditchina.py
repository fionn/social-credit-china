#!/usr/bin/env python3
"""Get the social credit list"""

from dataclasses import dataclass
from typing import List, Dict, Generator

import requests

@dataclass
class Person:
    """
    "xm": "姓名",
    "lrsj": "列入时间",
    "tmzjhm": "证件号码",
    "lrbm": "列入部门"
    """

    xm: str # pylint: disable=invalid-name
    lrsj: str
    tmzjhm: str
    lrbm: str

class CreditChina:
    """Just a getter"""

    def __init__(self) -> None:
        self.base_url = "https://public.creditchina.gov.cn"
        self.endpoint = "/private-api/catalogSearchPerson"
        self.url = self.base_url + self.endpoint
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "curl/7.67.0"})

    def _get(self, payload: dict) -> requests.models.Response:
        """HTTP GET"""
        response = self.session.get(self.url, params=payload)
        response.raise_for_status()
        return response

    def get_human_data_by_page(self, page: int, size: int) -> List[Dict[str, str]]:
        """Returns a list of people data"""
        payload = {"searchState": 1,
                   "page": page,
                   "pageSize": size,
                   "tableName": "credit_zgf_zrr_sxbzxr_jb",
                   "scenes": "defaultscenario"}
        if page * size > 10000:
            raise RuntimeError("Requested {} which exceeds capacity"
                               .format(page * size))
        response_json = self._get(payload).json()
        if response_json["message"] != "成功":
            raise RuntimeError("TODO: standard error message")
        return response_json["data"]["list"]

    def yield_humans(self) -> Generator[Person, None, None]:
        """Here's a person"""
        for i in range(1, 1000):
            humans = self.get_human_data_by_page(page=i, size=2)
            for human in humans:
                yield Person(**human)

def main() -> None:
    """Entry point"""

    cc = CreditChina() # pylint: disable=invalid-name

    for person in cc.yield_humans():
        print(person)

if __name__ == "__main__":
    main()
