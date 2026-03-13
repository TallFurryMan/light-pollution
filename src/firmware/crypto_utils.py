"""AES-128 helpers for the LoRaWAN firmware.

MicroPython boards are expected to provide ``cryptolib`` / ``ucryptolib``.
CPython test runs use the pure-Python fallback implemented here.
"""

try:
    import cryptolib as _cryptolib  # type: ignore
except ImportError:
    try:
        import ucryptolib as _cryptolib  # type: ignore
    except ImportError:  # pragma: no cover - exercised via the pure-python path
        _cryptolib = None  # type: ignore


_ZERO_BLOCK = b"\x00" * 16
_RB = 0x87

_SBOX = (
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16,
)

_RCON = (0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36)
_ROUND_KEY_CACHE = {}
_INV_SBOX = None


def _xor_bytes(left, right):
    return bytes(a ^ b for a, b in zip(left, right))


def _left_shift_128(block):
    value = int.from_bytes(block, "big") << 1
    value &= (1 << 128) - 1
    return value.to_bytes(16, "big")


def _generate_cmac_subkeys(key):
    l_block = aes128_encrypt_block(key, _ZERO_BLOCK)
    k1 = bytearray(_left_shift_128(l_block))
    if l_block[0] & 0x80:
        k1[-1] ^= _RB
    k2 = bytearray(_left_shift_128(k1))
    if k1[0] & 0x80:
        k2[-1] ^= _RB
    return bytes(k1), bytes(k2)


def _pad_cmac_block(block):
    return block + b"\x80" + (b"\x00" * (15 - len(block)))


def _xtime(value):
    value <<= 1
    if value & 0x100:
        value ^= 0x11B
    return value & 0xFF


def _expand_round_keys(key):
    cached = _ROUND_KEY_CACHE.get(key)
    if cached is not None:
        return cached

    expanded = bytearray(key)
    round_index = 0
    while len(expanded) < 176:
        temp = bytearray(expanded[-4:])
        if len(expanded) % 16 == 0:
            temp = temp[1:] + temp[:1]
            for idx in range(4):
                temp[idx] = _SBOX[temp[idx]]
            temp[0] ^= _RCON[round_index]
            round_index += 1
        for idx in range(4):
            expanded.append(expanded[-16] ^ temp[idx])

    keys = tuple(bytes(expanded[offset:offset + 16]) for offset in range(0, 176, 16))
    _ROUND_KEY_CACHE[key] = keys
    return keys


def _add_round_key(state, round_key):
    for index in range(16):
        state[index] ^= round_key[index]


def _sub_bytes(state):
    for index in range(16):
        state[index] = _SBOX[state[index]]


def _shift_rows(state):
    state[1], state[5], state[9], state[13] = state[5], state[9], state[13], state[1]
    state[2], state[6], state[10], state[14] = state[10], state[14], state[2], state[6]
    state[3], state[7], state[11], state[15] = state[15], state[3], state[7], state[11]


def _mix_columns(state):
    for base in range(0, 16, 4):
        a0, a1, a2, a3 = state[base:base + 4]
        mix = a0 ^ a1 ^ a2 ^ a3
        state[base] ^= mix ^ _xtime(a0 ^ a1)
        state[base + 1] ^= mix ^ _xtime(a1 ^ a2)
        state[base + 2] ^= mix ^ _xtime(a2 ^ a3)
        state[base + 3] ^= mix ^ _xtime(a3 ^ a0)


def _mul(value, factor):
    result = 0
    while factor:
        if factor & 1:
            result ^= value
        value = _xtime(value)
        factor >>= 1
    return result


def _get_inv_sbox():
    global _INV_SBOX
    if _INV_SBOX is None:
        values = [0] * 256
        for index, value in enumerate(_SBOX):
            values[value] = index
        _INV_SBOX = tuple(values)
    return _INV_SBOX


def _inv_sub_bytes(state):
    inv_sbox = _get_inv_sbox()
    for index in range(16):
        state[index] = inv_sbox[state[index]]


def _inv_shift_rows(state):
    state[1], state[5], state[9], state[13] = state[13], state[1], state[5], state[9]
    state[2], state[6], state[10], state[14] = state[10], state[14], state[2], state[6]
    state[3], state[7], state[11], state[15] = state[7], state[11], state[15], state[3]


def _inv_mix_columns(state):
    for base in range(0, 16, 4):
        a0, a1, a2, a3 = state[base:base + 4]
        state[base] = _mul(a0, 14) ^ _mul(a1, 11) ^ _mul(a2, 13) ^ _mul(a3, 9)
        state[base + 1] = _mul(a0, 9) ^ _mul(a1, 14) ^ _mul(a2, 11) ^ _mul(a3, 13)
        state[base + 2] = _mul(a0, 13) ^ _mul(a1, 9) ^ _mul(a2, 14) ^ _mul(a3, 11)
        state[base + 3] = _mul(a0, 11) ^ _mul(a1, 13) ^ _mul(a2, 9) ^ _mul(a3, 14)


def _aes128_encrypt_block_sw(key, block):
    state = bytearray(block)
    round_keys = _expand_round_keys(key)

    _add_round_key(state, round_keys[0])
    for round_key in round_keys[1:-1]:
        _sub_bytes(state)
        _shift_rows(state)
        _mix_columns(state)
        _add_round_key(state, round_key)
    _sub_bytes(state)
    _shift_rows(state)
    _add_round_key(state, round_keys[-1])
    return bytes(state)


def _aes128_decrypt_block_sw(key, block):
    state = bytearray(block)
    round_keys = _expand_round_keys(key)

    _add_round_key(state, round_keys[-1])
    for round_key in reversed(round_keys[1:-1]):
        _inv_shift_rows(state)
        _inv_sub_bytes(state)
        _add_round_key(state, round_key)
        _inv_mix_columns(state)
    _inv_shift_rows(state)
    _inv_sub_bytes(state)
    _add_round_key(state, round_keys[0])
    return bytes(state)


def aes128_encrypt_block(key, block):
    if len(key) != 16 or len(block) != 16:
        raise ValueError("AES-128 operates on 16-byte keys and blocks")
    if _cryptolib is not None:
        cipher = _cryptolib.aes(key, 1)
        return cipher.encrypt(block)
    return _aes128_encrypt_block_sw(key, block)


def aes128_decrypt_block(key, block):
    if len(key) != 16 or len(block) != 16:
        raise ValueError("AES-128 operates on 16-byte keys and blocks")
    if _cryptolib is not None:
        cipher = _cryptolib.aes(key, 1)
        decrypt = getattr(cipher, "decrypt", None)
        if callable(decrypt):
            return decrypt(block)
    return _aes128_decrypt_block_sw(key, block)


def aes128_cmac(key, message):
    if len(key) != 16:
        raise ValueError("AES-CMAC requires a 16-byte key")

    k1, k2 = _generate_cmac_subkeys(key)
    if len(message) == 0:
        last_block = _xor_bytes(_pad_cmac_block(b""), k2)
        blocks = []
    else:
        block_count = (len(message) + 15) // 16
        last_index = (block_count - 1) * 16
        blocks = [message[offset:offset + 16] for offset in range(0, last_index, 16)]
        tail = message[last_index:]
        if len(tail) == 16:
            last_block = _xor_bytes(tail, k1)
        else:
            last_block = _xor_bytes(_pad_cmac_block(tail), k2)

    state = _ZERO_BLOCK
    for block in blocks:
        state = aes128_encrypt_block(key, _xor_bytes(state, block))
    return aes128_encrypt_block(key, _xor_bytes(state, last_block))
