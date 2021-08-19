import logging
from argparse import ArgumentParser
from datetime import date, datetime
from typing import Optional

import requests
from requests import Session

logger = logging.getLogger(__name__)


class AnimalNotFound(Exception):
    pass


class Crsz:
    _DATE_FORMAT = '%Y-%m-%dT00:00:00.000Z'

    def __init__(self, username: str, password: str) -> None:
        self._username = username
        self._password = password
        self.__session: Optional[str] = None

    def vaccinate(self, file_name: str, vaccination_date: date, manufacturer: str, vaccine_name: str, bach_number: str,
                  ) -> None:
        chip_numbers = self._get_chip_numbers(file_name)
        date_from = vaccination_date.strftime(self._DATE_FORMAT)
        date_to = vaccination_date.replace(year=vaccination_date.year + 1).strftime(self._DATE_FORMAT)
        user_id = self._username[2:]

        for chip_number in chip_numbers:
            try:
                try:
                    animal_id = self._get_animal_id(chip_number)
                except AnimalNotFound:
                    print(f'Animal {chip_number} not found')
                    continue

                self._vaccinate(animal_id, date_from, date_to, user_id, manufacturer, vaccine_name, bach_number)
            except Exception:
                logger.exception(f'\nError on vaccinate {chip_number}')

            print('.')

    @staticmethod
    def _get_chip_numbers(file_name: str) -> list[str]:
        with open(file_name) as h:
            return [line.strip() for line in h.readlines()
                    if not line.startswith('Microchip')]

    def _vaccinate(self, animal_id, date_from: str, date_to: str, user_id: str, manufacturer: str,
                   vaccine_name: str, batch_number: str) -> None:
        vaccination = {'vaccineDate': date_from, 'vaccineManufacturer': manufacturer, 'vaccineName': vaccine_name,
                       'batchNumber': batch_number, 'validFromSelection': 'NOW', 'validUntilSelection': 'VALID1YEAR'}
        last_vaccination = vaccination.copy()
        last_vaccination['validFrom'] = date_from
        last_vaccination['validUntil'] = date_to
        data = {'id': animal_id, 'userId': user_id, 'changeId': user_id, 'vaccination': vaccination,
                'lastVaccination': last_vaccination}

        url = f'https://www.crsz.sk/admin/api/animals-register/animals/add-vaccination/{animal_id}'
        resp = self._session.put(url, json=data)
        assert resp.status_code == 200

    def _get_animal_id(self, chip_no: str) -> int:
        url = f'https://www.crsz.sk/admin/api/animals-register/animals/transponder/{chip_no}'
        resp = self._session.get(url)
        assert resp.status_code == 200
        data = resp.json()

        if len(data) != 1:
            raise AnimalNotFound()

        return data[0]['id']

    @property
    def _session(self) -> Session:
        if self.__session is None:
            self.__session = Session()
            self.__session.headers.update({'authorization': self._login()})

        return self.__session

    def _login(self) -> str:
        resp = requests.post('https://www.crsz.sk/admin/api/authenticate',
                             json={'username': self._username, 'password': self._password})
        assert resp.status_code == 200

        return resp.headers['Authorization']


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('username')
    parser.add_argument('password')
    parser.add_argument('date', type=lambda s: datetime.strptime(s, '%Y-%m-%d').date())
    parser.add_argument('manufacturer')
    parser.add_argument('vaccine_name')
    parser.add_argument('batch_number')
    parser.add_argument('file')
    args = parser.parse_args()

    crsz = Crsz(args.username, args.password)
    crsz.vaccinate(args.file, args.date, args.manufacturer, args.vaccine_name, args.batch_number)

    print('OK')
