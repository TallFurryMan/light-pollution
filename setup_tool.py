"""Provision a pre-flashed classroom node over the MicroPython serial REPL."""

import argparse
import json
import sys
import time

DEFAULT_BAUD = 115200
DEFAULT_BOARD_PROFILE = "pico_lora_sx1262_868m"
DEFAULT_SENSOR = "TSL2591"
DEFAULT_CHARGER = "CN3065"
DEFAULT_POLL_INTERVAL = 900


def fallback_port():
    if sys.platform.startswith("win"):
        return "COM3"
    if sys.platform == "darwin":
        return "/dev/cu.usbmodem*"
    return "/dev/ttyACM0"


def detect_default_port():
    try:
        from serial.tools import list_ports
    except ImportError:
        return fallback_port()

    candidates = [port.device for port in list_ports.comports()]
    preferred_prefixes = (
        "/dev/cu.usbmodem",
        "/dev/cu.usbserial",
        "/dev/ttyACM",
        "/dev/ttyUSB",
        "COM",
    )
    for prefix in preferred_prefixes:
        for candidate in candidates:
            if candidate.startswith(prefix):
                return candidate
    return candidates[0] if candidates else fallback_port()


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Write config.json to a pre-flashed classroom node.",
    )
    parser.add_argument("friendly_name", help="Short node name shown in Home Assistant")
    parser.add_argument("latitude", type=float, help="Latitude in decimal degrees")
    parser.add_argument("longitude", type=float, help="Longitude in decimal degrees")
    parser.add_argument("--port", help="Serial port, for example /dev/ttyACM0 or COM3")
    parser.add_argument("--baud", type=int, default=DEFAULT_BAUD, help="Serial baud rate")
    parser.add_argument(
        "--board-profile",
        default=DEFAULT_BOARD_PROFILE,
        help="Firmware board profile stored in config.json",
    )
    parser.add_argument(
        "--sensor-type",
        default=DEFAULT_SENSOR,
        choices=("TSL2591", "BH1750", "TEMT6000"),
        help="Light sensor used on the node",
    )
    parser.add_argument(
        "--charger-type",
        default=DEFAULT_CHARGER,
        choices=("CN3065", "MCP73871", "TP4056", "none"),
        help="Charging board used on the node",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=DEFAULT_POLL_INTERVAL,
        help="Measurement interval in seconds",
    )
    parser.add_argument(
        "--freq",
        type=int,
        default=868_000_000,
        help="Radio frequency in Hz",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the config.json payload without opening the serial port",
    )
    return parser.parse_args(argv)


def build_config(args):
    return {
        "board_profile": args.board_profile,
        "name": args.friendly_name,
        "lat": args.latitude,
        "lon": args.longitude,
        "sensor_type": args.sensor_type,
        "charger_type": args.charger_type,
        "poll_interval": args.poll_interval,
        "freq": args.freq,
    }


def build_remote_script(cfg):
    payload = json.dumps(cfg, separators=(",", ":"), ensure_ascii=True)
    return (
        "import ujson\r\n"
        f"config = ujson.loads({payload!r})\r\n"
        "with open('config.json', 'w') as handle:\r\n"
        "    ujson.dump(config, handle)\r\n"
        "print('CONFIG_OK')\r\n"
    )


def open_serial(port, baud, timeout=5):
    try:
        import serial
    except ImportError as exc:
        raise RuntimeError("pyserial is required: pip install pyserial") from exc
    return serial.Serial(port, baud, timeout=timeout)


def provision_device(ser, script):
    ser.write(b"\x03\x03\r\n")
    ser.flush()
    time.sleep(0.5)
    reset_buffer = getattr(ser, "reset_input_buffer", None)
    if callable(reset_buffer):
        reset_buffer()
    ser.write(script.encode("utf-8"))
    ser.flush()
    time.sleep(1)
    response = ser.read(256)
    if b"CONFIG_OK" not in response:
        raise RuntimeError("MicroPython did not confirm that config.json was written")


def main(argv=None):
    args = parse_args(argv)
    cfg = build_config(args)

    if args.dry_run:
        print(json.dumps(cfg, indent=2, sort_keys=True))
        return 0

    port = args.port or detect_default_port()
    script = build_remote_script(cfg)

    print(f"Sending config to node on {port} ...")
    with open_serial(port, args.baud, timeout=5) as ser:
        provision_device(ser, script)
    print("Configuration written successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
