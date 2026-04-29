#!/bin/sh

# Raspberry Pi OS-compatible replacement for Semtech's reset_lgw.sh.
# The upstream script still relies on the legacy sysfs GPIO interface, which is
# not dependable on recent Raspberry Pi OS kernels. This variant uses pinctrl.

set -eu

SX1302_RESET_PIN="${SX1302_RESET_PIN:-17}"
SX1302_POWER_EN_PIN="${SX1302_POWER_EN_PIN:-18}"
SX1261_RESET_PIN="${SX1261_RESET_PIN:-22}"
AD5338R_RESET_PIN="${AD5338R_RESET_PIN:-13}"
SX1302_POWER_EN_ACTIVE="${SX1302_POWER_EN_ACTIVE:-high}"

WAIT_GPIO_SEC="${WAIT_GPIO_SEC:-0.1}"
WAIT_POWER_DOWN_SEC="${WAIT_POWER_DOWN_SEC:-0.3}"
WAIT_POWER_UP_SEC="${WAIT_POWER_UP_SEC:-0.3}"
DEBUG_RESET="${DEBUG_RESET:-0}"

WAIT_GPIO() {
    sleep "${WAIT_GPIO_SEC}"
}

WAIT_POWER_DOWN() {
    sleep "${WAIT_POWER_DOWN_SEC}"
}

WAIT_POWER_UP() {
    sleep "${WAIT_POWER_UP_SEC}"
}

require_pinctrl() {
    if ! command -v pinctrl >/dev/null 2>&1; then
        echo "ERROR: pinctrl not found. On Raspberry Pi OS Bookworm/Trixie it should be available." >&2
        exit 1
    fi
}

show_pin() {
    if [ "${DEBUG_RESET}" = "1" ]; then
        pinctrl get "$1"
    fi
}

show_all_pins() {
    if [ "${DEBUG_RESET}" = "1" ]; then
        show_pin "${SX1302_RESET_PIN}"
        show_pin "${SX1302_POWER_EN_PIN}"
        show_pin "${SX1261_RESET_PIN}"
        show_pin "${AD5338R_RESET_PIN}"
    fi
}

set_output_high() {
    pinctrl set "$1" op dh
    show_pin "$1"
}

set_output_low() {
    pinctrl set "$1" op dl
    show_pin "$1"
}

release_pin() {
    pinctrl set "$1" ip pn
    show_pin "$1"
}

power_enable_on() {
    case "${SX1302_POWER_EN_ACTIVE}" in
        high)
            set_output_high "${SX1302_POWER_EN_PIN}"
            ;;
        low)
            set_output_low "${SX1302_POWER_EN_PIN}"
            ;;
        *)
            echo "ERROR: SX1302_POWER_EN_ACTIVE must be 'high' or 'low'" >&2
            exit 1
            ;;
    esac
}

power_enable_off() {
    case "${SX1302_POWER_EN_ACTIVE}" in
        high)
            set_output_low "${SX1302_POWER_EN_PIN}"
            ;;
        low)
            set_output_high "${SX1302_POWER_EN_PIN}"
            ;;
        *)
            echo "ERROR: SX1302_POWER_EN_ACTIVE must be 'high' or 'low'" >&2
            exit 1
            ;;
    esac
}

reset() {
    echo "CoreCell reset through GPIO${SX1302_RESET_PIN}..."
    echo "SX1261 reset through GPIO${SX1261_RESET_PIN}..."
    echo "CoreCell power enable through GPIO${SX1302_POWER_EN_PIN}..."
    echo "CoreCell ADC reset through GPIO${AD5338R_RESET_PIN}..."
    show_all_pins

    # Force a real power cycle first. This avoids the "first run works, second
    # run returns 0x05" pattern seen when the concentrator stays half-alive
    # across successive tool invocations.
    power_enable_off
    WAIT_POWER_DOWN

    power_enable_on
    WAIT_POWER_UP

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
    show_all_pins
}

term() {
    echo "GPIO term"
    power_enable_off
    WAIT_POWER_DOWN
    release_pin "${SX1302_RESET_PIN}"
    release_pin "${SX1302_POWER_EN_PIN}"
    release_pin "${SX1261_RESET_PIN}"
    release_pin "${AD5338R_RESET_PIN}"
    show_all_pins
}

status() {
    show_all_pins
}

pulse() {
    echo "Debug pulse on GPIO${SX1302_POWER_EN_PIN}"
    power_enable_off
    WAIT_POWER_DOWN
    power_enable_on
    WAIT_POWER_UP
    show_all_pins
}

usage() {
    echo "Usage: $0 {start|stop|status|pulse}"
    echo "Optional env: DEBUG_RESET=1 WAIT_POWER_DOWN_SEC=2 WAIT_POWER_UP_SEC=2 WAIT_GPIO_SEC=0.2 SX1302_POWER_EN_ACTIVE=high"
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
    status)
        status
        ;;
    pulse)
        pulse
        ;;
    *)
        usage
        ;;
esac

exit 0
