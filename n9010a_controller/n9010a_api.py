from ast import literal_eval
from typing import Literal


class N9010A_API:

    @staticmethod
    def parse_measured_data(data: bytes) -> list[tuple[float, float]]:
        elements: list[str] = data.decode().split(',')
        peaks_amount: int = literal_eval(elements[0])
        if peaks_amount > 0:
            values: list[float] = [literal_eval(el) for el in elements[1:]]
            return [tuple(values[i: i + 2]) for i in range(0, len(values), 2)]  # type: ignore
        return []

    @staticmethod
    def identification_query() -> bytes:
        """Returns a string of instrument identification information.
        The string will contain the model number, serial number,
        and firmware revision."""
        return '*IDN?\n'.encode('ascii')

    @staticmethod
    def wait_to_continue() -> bytes:
        """This command causes the instrument to wait until all
        overlapped commands are completed before executing
        any additional commands."""
        return '*WAI\n'.encode('ascii')

    @staticmethod
    def abort() -> bytes:
        """This command is used to stop the current measurement. It aborts
        the current measurement as quickly as possible, resets the sweep
        and trigger systems, and puts the measurement into an "idle" state."""
        return '*ABOR\n'.encode('ascii')

    @staticmethod
    def calculate_peaks(ch: int, threshold: int, excursion: int,
                        order: Literal['AMPL', 'FREQ', 'TIME'] = 'AMPL',
                        peaks: Literal['ALL', 'GTDL', 'LTDL'] = 'GTDL') -> bytes:
        """Returns a list of all the peaks for the currently selected
        measurement and sub-opcode [n]. The peaks must meet the requirements
        of the peak threshold and excursion values"""
        cmd = f":CALC:DATA{ch}:PEAK? {threshold},{excursion},{order},{peaks}\n"
        return cmd.encode('ascii')

    @staticmethod
    def restart_measure() -> bytes:
        return ':INIT:REST\n'.encode('ascii')

    @staticmethod
    def set_continues_peak_search(marker_num: int, enable: bool) -> bytes:
        """Turns Continuous Peak Search on or off. When Continuous Peak Search
        is on, a peak search is automatically performed for the selected marker
        after each sweep. """
        cmd: str = f":CALC:MARK{marker_num}:CPS {'ON' if enable else 'OFF'}\n"
        return cmd.encode('ascii')

    @staticmethod
    def get_current_measure_config():
        return 'CONF?\n'.encode('ascii')

    @staticmethod
    def set_continues_sweep() -> bytes:
        return ':INIT:CONT ON\n'.encode('ascii')

    @staticmethod
    def start_swept_sa_measures() -> bytes:
        return 'INIT:SAN\n'.encode('ascii')

    @staticmethod
    def get_continues_peak_search_state(marker_num: int) -> bytes:
        return f":CALC:MARK{marker_num}:CPS?\n".encode('ascii')

    @staticmethod
    def set_peak_table_state(state: bool) -> bytes:
        """Turns Peak Table on/off. When turned on, the display is split into
        a measurement window and a peak table display window"""
        cmd: str = f":CALC:MARK:PEAK:TABL:STAT {'ON' if state else 'OFF'}\n"
        return cmd.encode('ascii')

    @staticmethod
    def set_trace_type(trace_num: int,
                       trace_type: Literal['WRIT', 'AVER', 'MAXH', 'MINH']):
        return f':TRAC{trace_num}:TYPE {trace_type}\n'.encode('ascii')

    @staticmethod
    def set_mode(mode: Literal['SA', 'BASIC', 'WCDMA', 'CDMA2K', 'EDGEGSM','BT',
                               'PNOISE', 'CDMA1XEV', 'CWLAN', 'WIM', 'AXOFDMA',
                               'CWIMAXOFDM', 'SEQAN', 'VSA89601', 'LTE', 'IDEN',
                               'WIMAXFIXED', 'LTE', 'TDD', 'TDSCDMA', 'NFIGURE',
                               'VSA', 'ADEMOD', 'DVB', 'DTMB', 'ISDBT', 'CMMB',
                               'RLC', 'SCPI', 'LC', 'SAN', 'REC']) -> bytes:
        """
        Spectrum Analyzer -SA \n
        I/Q Analyzer (Basic) - BASIC \n
        WCDMA with HSPA+ - WCDMA \n
        cdma2000 - CDMA2K \n
        GSM/EDGE/EDGE Evo - EDGEGSM \n
        Phase Noise - PNOISE \n
        1xEV-DO - CDMA1XEV \n
        Combined WLAN - CWLAN \n
        802.16 OFDMA (WiMAX/WiBro) - WIMAXOFDMA \n
        Combined Fixed WiMAX - CWIMAXOFDM \n
        Vector Signal Analyzer (VXA) - VSA \n
        89601 VSA - VSA89601 \n
        LTE - LTE \n
        iDEN/WiDEN/MotoTalk - IDEN \n
        802.16 OFDM (Fixed WiMAX) - WIMAXFIXED \n
        LTE TDD - LTETDD \n
        EMI Receiver - EMI \n
        TD-SCDMA with HSPA/8PSK - TDSCDMA \n
        Noise Figure - NFIGURE \n
        Bluetooth - BT \n
        Analog Demod - ADEMOD \n
        DVB-T/H with T2 - DVB \n
        DTMB (CTTB) - DTMB \n
        Digital Cable TV - DCATV \n
        ISDB-T - ISDBT \n
        CMMB - CMMB \n
        Remote Language Compatibility - RLC \n
        SCPI Language Compatibility - SCPILC \n
        Sequence Analyzer - SEQAN \n
        """
        return f":INST {mode}\n".encode('ascii')

    @staticmethod
    def get_mode_catalogue() -> bytes:
        """Returns a string containing a comma separated list of names of all
        the installed and licensed measurement modes (applications)."""
        return ":INST:CAT?\n".encode('ascii')

    @staticmethod
    def set_start_freq(val: int,
                       units: Literal['HZ', 'KHZ', 'MHZ', 'GHZ'] = 'HZ'):
        """Sets the frequency at the left side of the graticule. While
        adjusting the start frequency, the stop frequency is held constant,
        which means that both the center frequency and span will change"""
        return f":SENS:FREQ:STAR {val} {units}\n".encode('ascii')

    @staticmethod
    def get_start_freq() -> bytes:
        return ":SENS:FREQ:STAR?\n".encode('ascii')

    @staticmethod
    def set_stop_freq(val: int,
                      units: Literal['HZ', 'KHZ', 'MHZ', 'GHZ'] = 'HZ'):
        """Sets the frequency at the right side of the graticule. While a
        djusting the stop Frequency, the start frequency is held constant,
        which means that both the center frequency and span will change."""
        return f":SENS:FREQ:STOP {val} {units}\n".encode('ascii')

    @staticmethod
    def get_stop_freq() -> bytes:
        return ":SENS:FREQ:STOP?\n".encode('ascii')

    @staticmethod
    def set_freq_span(val: int,
                      units: Literal['HZ', 'KHZ', 'MHZ', 'GHZ'] = 'HZ'):
        """Changes the displayed frequency range symmetrically about the
        center frequency."""
        return f":SENS:FREQ:SPAN {val} {units}\n".encode('ascii')

    @staticmethod
    def get_freq_span() -> bytes:
        return ":SENS:FREQ:SPAN?\n".encode('ascii')

    @staticmethod
    def set_center_freq(val: int,
                        units: Literal['HZ', 'KHZ', 'MHZ', 'GHZ'] = 'HZ'):
        """This command will set the Center Frequency to be used when the RF
        input is selected, even if the RF input is not the input which is
        selected at the time the command is sent. """
        return f":SENS:FREQ:RF:CENT {val} {units}\n".encode('ascii')

    @staticmethod
    def get_center_freq() -> bytes:
        return ":SENS:FREQ:RF:CENT?\n".encode('ascii')

    @staticmethod
    def save_screenshot(name: str) -> bytes:
        """Saves the screen image to the specified file using the selected
        theme. """
        return f":MMEM:STOR:SCR \"{name}\"\n".encode('ascii')

    @staticmethod
    def set_screenshot_theme(theme: Literal['TDC', 'TDM', 'FCOL', 'FMON']):
        return f":MMEM:STOR:SCR:THEM {theme}\n".encode('ascii')

    @staticmethod
    def get_screenshot_theme() -> bytes:
        return ":MMEM:STOR:SCR:THEM?\n".encode('ascii')

    @staticmethod
    def read_mass_storage_catalog(dir_name: str) -> bytes:
        """Query disk usage information (drive capacity, free space available)
        and obtain  a list of files and directories in a specified directory in
        the following format: <numeric_value>,<numeric_value>,{<file_entry>}"""
        return f":MMEM:CAT? {dir_name}\n".encode('ascii')

    @staticmethod
    def mkdir(dir_name: str) -> bytes:
        """Creates a new directory."""
        return f":MMEM:MDIR {dir_name}\n".encode('ascii')

    @staticmethod
    def power_down(mode: Literal['NORMAL', 'FORCE']) -> bytes:
        return f":SYST:PDOW {mode}\n".encode('ascii')

if __name__ == '__main__':
    raw_data = b'2.0000e0,8.68800000e5,-1.532131e1,8.67800000e5,-1.522131e1'
    print(N9010A_API.parse_measured_data(raw_data))