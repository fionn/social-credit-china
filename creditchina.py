#!/usr/bin/env python3
"""Get the social credit list"""

import datetime
from typing import List, Dict, Generator

import requests
import gb2260 # type: ignore

def truncate_int(year: int) -> int:
    """E.g. 200506 -> 2005"""
    return int(str(year)[:4])

class CCError(Exception):
    """Exception class for CreditChina errors"""

    def __init__(self, message: str, data: Dict = None) -> None:
        super().__init__(message)
        self.data = data

# pylint: disable=too-few-public-methods
class Person:
    """
    "xm": "姓名",
    "lrsj": "列入时间",
    "tmzjhm": "证件号码",
    "lrbm": "列入部门"
    """

    def __init__(self, xm: str, lrsj: str, tmzjhm: str, lrbm: str) -> None:
        self.name = xm
        self.date = datetime.date.fromisoformat(lrsj)
        self.id_str = tmzjhm
        self.dept = lrbm
        self.division = self._get_division(tmzjhm)

    def __repr__(self) -> str:
        return f"人(name={self.name}, date={self.date}, " \
               f"id_str={self.id_str[:6]}***{self.id_str[-1]}, " \
               f"dept={self.dept})"

    @staticmethod
    def _get_division(tmzjhm: str) -> None:
        try:
            return gb2260.get(tmzjhm[:6])
        except ValueError:
            years = [year for year in gb2260.data.data if year is not None]
            years.sort(key=truncate_int, reverse=True)
            for year in years:
                try:
                    return gb2260.get(tmzjhm[:6], year)
                except ValueError:
                    continue
            return None

class CreditChina:
    """Person factory"""

    MAX_CAPACITY = 10000

    def __init__(self) -> None:
        base_url = "https://public.creditchina.gov.cn"
        endpoint = "/private-api/catalogSearchPerson"
        self.url = base_url + endpoint
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "curl/7.67.0"})

    def _get(self, payload: dict) -> requests.models.Response:
        response = self.session.get(self.url, params=payload)
        response.raise_for_status()
        return response

    def _get_person_data_by_page(self, page: int,
                                 size: int) -> List[Dict[str, str]]:
        payload = {"searchState": 1,
                   "page": page,
                   "pageSize": size,
                   "tableName": "credit_zgf_zrr_sxbzxr_jb",
                   "scenes": "defaultscenario"}
        if page * size > self.MAX_CAPACITY:
            raise CCError("Requested {} which exceeds capacity"
                          .format(page * size))
        response_json = self._get(payload).json()
        if response_json["message"] != "成功":
            raise CCError("status: {}, message: {}"
                          .format(response_json["status"],
                                  response_json["message"]),
                          data=response_json)
        return response_json["data"]["list"]

    def person_generator(self, size: int = 200,
                         step: int = 1) -> Generator[Person, None, None]:
        """Here's a person, from present to past (by default)"""
        for i in range(1, int(self.MAX_CAPACITY / size), step):
            people = self._get_person_data_by_page(page=i, size=size)
            for person in people:
                yield Person(**person)

def main() -> None:
    """Entry point"""

    cc = CreditChina() # pylint: disable=invalid-name

    for person in cc.person_generator(size=8):
        print(person)
        print(person.division)

if __name__ == "__main__":
    main()
