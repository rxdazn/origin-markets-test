#!/usr/bin/env python

import requests
import os
import sys

BONDS = [
    {
        "isin": "FR0000131104",
        "size": 100000000,
        "currency": "EUR",
        "maturity": "2025-03-27",
        "lei": "R0MUWSFPU8MPRO8K5P83",
    },
    {
        "isin": "FR0000131104",
        "size": 200000000,
        "currency": "USD",
        "maturity": "2023-08-23",
        "lei": "353800279ADEFGKNTV65",
    },
]


def main():
    api_key = os.environ.get("OM_TEST_API_KEY")
    if not api_key:
        print(
            "Make sure to set your API key in this shell's environemnt before running this command\n"
            "Usage: OM_TEST_API_KEY=your_api_key_here ./utils/populate_db.py"
        )
        sys.exit()

    for bond in BONDS:
        response = requests.post(
            "http://localhost:8000/bonds/",
            json=bond,
            headers={"Authorization": f"Token {api_key}"},
        )
        try:
            assert response.status_code == 201
            print("Created bond.")
        except AssertionError:
            print(f"Error creating bond.: {response.content}")


if __name__ == "__main__":
    main()
