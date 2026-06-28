"""
Annunciator Panel — Sensor Alarm Visualisation
===============================================
Monitors a DAQ sensor for 60 seconds and drives a BlinkStick indicator:
  • GREEN when voltage > +4.27 V  (high alarm)
  • RED   when voltage < −2.56 V  (low alarm)
  • OFF   otherwise
A real-time Matplotlib graph displays voltage vs time with alarm thresholds.
Author : Ping Fan Teng (rewritten)
License: CC-BY — The University of Edinburgh, 2021
"""
# ──────────────────────────────────────────────────────────────────────────────
# 1. IMPORTS
# ──────────────────────────────────────────────────────────────────────────────
from scada import DAQ                   # Coursework DAQ interface
from blinkstick import blinkstick       # USB LED controller
import matplotlib.pyplot as plt         # Plotting
# ──────────────────────────────────────────────────────────────────────────────
# 2. CONSTANTS
#    Centralising magic numbers makes tuning and auditing straightforward.
# ──────────────────────────────────────────────────────────────────────────────
HIGH_ALARM_V   = 4.27          # Voltage threshold for GREEN (high alarm)
LOW_ALARM_V    = -2.56         # Voltage threshold for RED   (low alarm)
RUN_DURATION_S = 60            # Total acquisition window (seconds)
LED_INDEX      = 1             # BlinkStick LED index used for alarms
COLOUR_GREEN   = "#003200"     # Hex colour for high-alarm indicator
COLOUR_RED     = "#460000"     # Hex colour for low-alarm indicator
COLOUR_OFF     = "black"       # Colour representing LED off
# DAQ quantisation step (10-bit ADC spanning ±5 V)
Q = (5.0 - (-5.0)) / (2 ** 10)  # ≈ 0.009765625 V per bit
ADC_MID = 1023 / 2              # Midpoint reading (0 V)
# ──────────────────────────────────────────────────────────────────────────────
# 3. HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────
def reading_to_volts(raw: int) -> float:
    """
    Convert a raw 10-bit ADC reading to actual voltage.
    The DAQ encodes voltage in the range [−5 V, +5 V] as integers 0–1023.
    Formula:  V = (raw − 511.5) × Q
    """
    return (raw - ADC_MID) * Q
def determine_alarm_state(voltage: float) -> str | None:
    """
    Decide which alarm state applies for the given voltage.
    Returns
    -------
    "green" : voltage exceeds high threshold
    "red"   : voltage falls below low threshold
    None    : voltage is within safe band (no alarm)
    """
    if voltage > HIGH_ALARM_V:
        return "green"
    if voltage < LOW_ALARM_V:
        return "red"
    return None
def set_led(stick, state: str | None) -> None:
    """
    Set the BlinkStick LED to reflect the alarm state.
    Accepts "green", "red", or None (off).
    """
    if state == "green":
        stick.set_color(index=LED_INDEX, hex=COLOUR_GREEN)
    elif state == "red":
        stick.set_color(index=LED_INDEX, hex=COLOUR_RED)
    else:
        stick.set_color(index=LED_INDEX, name=COLOUR_OFF)
def all_leds_off(stick) -> None:
    """Turn off every LED on the BlinkStick (indices 0–7)."""
    for idx in range(8):
        stick.set_color(index=idx, name=COLOUR_OFF)
def configure_plot(ax) -> None:
    """
    Apply static styling to the live plot:
      • Axis labels and title
      • Horizontal alarm-threshold lines
      • Fixed y-axis limits for consistent visualisation
    """
    ax.set_xlabel("Time (s)", fontsize=14)
    ax.set_ylabel("Voltage (V)", fontsize=14)
    ax.set_title("DAQ Output — Annunciator Panel", fontsize=16)
    ax.axhline(y=HIGH_ALARM_V, color="green", linestyle="--", label="High alarm")
    ax.axhline(y=LOW_ALARM_V, color="red", linestyle="--", label="Low alarm")
    ax.set_ylim(-6, 6)
    ax.legend(loc="upper right")
# ──────────────────────────────────────────────────────────────────────────────
# 4. MAIN ACQUISITION LOOP
# ──────────────────────────────────────────────────────────────────────────────
def main() -> None:
    # ── 4a. Locate BlinkStick ─────────────────────────────────────────────────
    bstick = blinkstick.find_first()
    if bstick is None:
        raise RuntimeError(
            "BlinkStick not found. Check the USB connection and cable."
        )
    # ── 4b. Initialise DAQ ────────────────────────────────────────────────────
    daq = DAQ()
    daq.connect("coursework")
    daq.trigger()
    # ── 4c. Prepare real-time plot ────────────────────────────────────────────
    # Interactive mode allows the figure to update without blocking.
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 5))
    configure_plot(ax)
    (line,) = ax.plot([], [], color="blue", linewidth=1.2)
    fig.canvas.draw()
    fig.show()
    times: list[float] = []
    voltages: list[float] = []
    prev_state: str | None = None  # Track LED state to avoid redundant writes
    # ── 4d. Acquisition loop ──────────────────────────────────────────────────
    try:
        all_leds_off(bstick)  # Ensure a known starting state
        while daq.time < RUN_DURATION_S:
            # Fetch next sample (blocks until DELTA_T has elapsed)
            timestamp, raw_reading = daq.next_reading()
            voltage = reading_to_volts(raw_reading)
            # Determine and apply alarm state (only update LED if changed)
            state = determine_alarm_state(voltage)
            if state != prev_state:
                set_led(bstick, state)
                prev_state = state
            # Append data and refresh plot
            times.append(daq.time)
            voltages.append(voltage)
            line.set_data(times, voltages)
            ax.set_xlim(0, max(RUN_DURATION_S, daq.time + 1))
            fig.canvas.draw()
            fig.canvas.flush_events()
            # Console feedback
            print(f"t = {daq.time:5.1f} s | V = {voltage:+6.2f} V | alarm = {state or 'none'}")
        print("\n✓ Acquisition complete.")
    finally:
        # ── 4e. Cleanup ───────────────────────────────────────────────────────
        # Guarantee LEDs are off and plot is closed even if an error occurs.
        all_leds_off(bstick)
        plt.ioff()
        plt.close(fig)
        print("LEDs off, plot closed.")
# ──────────────────────────────────────────────────────────────────────────────
# 5. ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
