#!/bin/sh

# Raspberry Pi OS-compatible replacement for Semtech's reset_lgw.sh.
# The upstream script still relies on the legacy sysfs GPIO interface, which is
# not dependable on recent Raspberry Pi OS kernels. This variant uses pinctrl.

set -eu

SX1302_RESET_PIN="${SX1302_RESET_PIN:-17}"
SX1302_POWER_EN_PIN="${SX1302_POWER_EN_PIN:-18}"
SX1261_RESET_PIN="${SX1261_RESET_PIN:-22}"
AD5338R_RESET_PIN="${AD5338R_RESET_PIN:-13}"

WAIT_GPIO() {
    sleep 0.1
}

require_pinctrl() {
    if ! command -v pinctrl >/dev/null 2>&1; then
        echo "ERROR: pinctrl not found. On Raspberry Pi OS Bookworm/Trixie it should be available." >&2
        exit 1
    fi
}

set_output_high() {
    pinctrl set "$1" op dh
}

set_output_low() {
    pinctrl set "$1" op dl
}

release_pin() {
    pinctrl set "$1" ip pn
}

reset() {
    echo "CoreCell reset through GPIO${SX1302_RESET_PIN}..."
    echo "SX1261 reset through GPIO${SX1261_RESET_PIN}..."
    echo "CoreCell power enable through GPIO${SX1302_POWER_EN_PIN}..."
    echo "CoreCell ADC reset through GPIO${AD5338R_RESET_PIN}..."

    set_output_high "${SX1302_POWER_EN_PIN}"
    WAIT_GPIO

    set_output_high "${SX1302_RESET_PIN}"
    WAIT_GPIO
    set_output_low "${SX1302_RESET_PIN}"
    WAIT_GPIO

    set_output_low "${SX1261_RESET_PIN}"
    WAIT_GPIO
    set_output_high "${SX1261_RESET_PIN}"
    WAIT_GPIO

    set_output_low "${AD5338R_RESET_PIN}"
    WAIT_GPIO
    set_output_high "${AD5338R_RESET_PIN}"
    WAIT_GPIO
}

term() {
    echo "GPIO term"
    release_pin "${SX1302_RESET_PIN}"
    release_pin "${SX1302_POWER_EN_PIN}"
    release_pin "${SX1261_RESET_PIN}"
    release_pin "${AD5338R_RESET_PIN}"
}

usage() {
    echo "Usage: $0 {start|stop}"
    exit 1
}

require_pinctrl

case "${1:-}" in
    start)
        term
        reset
        ;;
    stop)
        reset
        term
        ;;
    *)
        usage
        ;;
esac

exit 0
