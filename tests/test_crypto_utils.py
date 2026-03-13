import os
import sys
import unittest


sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src", "firmware"))

import crypto_utils


class CryptoUtilsTests(unittest.TestCase):
    def test_aes128_encrypt_matches_known_vector(self):
        key = bytes.fromhex("2B7E151628AED2A6ABF7158809CF4F3C")
        block = bytes.fromhex("6BC1BEE22E409F96E93D7E117393172A")
        expected = bytes.fromhex("3AD77BB40D7A3660A89ECAF32466EF97")
        self.assertEqual(crypto_utils.aes128_encrypt_block(key, block), expected)

    def test_aes128_cmac_matches_rfc4493_vectors(self):
        key = bytes.fromhex("2B7E151628AED2A6ABF7158809CF4F3C")
        self.assertEqual(
            crypto_utils.aes128_cmac(key, b""),
            bytes.fromhex("BB1D6929E95937287FA37D129B756746"),
        )
        message = bytes.fromhex("6BC1BEE22E409F96E93D7E117393172A")
        self.assertEqual(
            crypto_utils.aes128_cmac(key, message),
            bytes.fromhex("070A16B46B4D4144F79BDD9DD04A287C"),
        )


if __name__ == "__main__":
    unittest.main()
