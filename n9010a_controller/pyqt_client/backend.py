from ast import literal_eval
from threading import Thread
import time
from pathlib import Path
from PyQt6 import QtWidgets, QtCore
from PyQt6.uic.load_ui import loadUi
from n9010a_controller.n9010a_api import N9010A_API
from n9010a_controller.socket_client import SocketClient


class N9010A_Controller(QtWidgets.QWidget):
    ip_line_edit: QtWidgets.QLineEdit
    connection_status_line_edit: QtWidgets.QLineEdit
    screenshot_filename_line_edit: QtWidgets.QLineEdit

    meas_result_table: QtWidgets.QTableWidget

    connect_button: QtWidgets.QPushButton
    save_screen_button: QtWidgets.QPushButton
    set_color_theme_button: QtWidgets.QPushButton
    set_freq_button: QtWidgets.QPushButton
    set_freq_span_button: QtWidgets.QPushButton
    measure_peaks_button: QtWidgets.QPushButton
    power_down_button: QtWidgets.QPushButton
    restart_measure_button: QtWidgets.QPushButton

    start_freq_spin_box: QtWidgets.QSpinBox
    stop_freq_spin_box: QtWidgets.QSpinBox
    center_freq_spin_box: QtWidgets.QSpinBox
    span_freq_spin_box: QtWidgets.QSpinBox
    trig_max_spin_box: QtWidgets.QSpinBox
    trig_min_spin_box: QtWidgets.QSpinBox
    port_spin_box: QtWidgets.QSpinBox

    start_freq_units_combo_box: QtWidgets.QComboBox
    stop_freq_units_combo_box: QtWidgets.QComboBox
    center_freq_units_combo_box: QtWidgets.QComboBox
    span_freq_units_combo_box: QtWidgets.QComboBox
    peak_order_combo_box: QtWidgets.QComboBox
    theme_combo_box: QtWidgets.QComboBox

    auto_restart_check_box: QtWidgets.QCheckBox

    def __init__(self, ip: str = '') -> None:
        super().__init__()
        loadUi(Path(__file__).parent.joinpath('N9010A.ui'), self)
        self.api = N9010A_API()
        self.device = SocketClient()
        self.device.connected.connect(self.on_successfull_connection)
        self.ip_line_edit.setText(ip)
        self.peaks: list[tuple[float, float]] = []
        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(lambda: self.fill_table(self.peaks))
        self._timer.start(100)

    def connection_status(self) -> bool:
        return self.device.connection_status()

    def fill_table(self, values: list) -> None:
        if not values:
            return
        self.meas_result_table.setRowCount(len(values))
        self.meas_result_table.setColumnCount(2)
        header_labels: list[str] = ["Amplitude, dBm", "Frequency, Hz"]
        self.meas_result_table.setHorizontalHeaderLabels(header_labels)
        for i, (freq, ampl) in enumerate(values):
            self.meas_result_table.setItem(i, 0, QtWidgets.QTableWidgetItem(f"{freq}"))
            self.meas_result_table.setItem(i, 1, QtWidgets.QTableWidgetItem(f"{ampl}"))
        header = self.meas_result_table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)
            header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

    def on_connect_button_pressed(self) -> None:
        connection_thread = Thread(name='N9010A_Connection_thread',
                                   target=self.device.connect,
                                   args=(self.ip_line_edit.text(),
                                         self.port_spin_box.value()),
                                   daemon=True)
        connection_thread.start()

    def on_successfull_connection(self) -> None:
        self.device.send((self.api.identification_query(), None))
        self.device.send((self.api.set_mode('SA'), None))
        self.device.send((self.api.start_swept_sa_measures(), None))
        # self.device.send((self.api.set_start_freq(867, 'MHZ'), None))
        # self.device.send((self.api.set_stop_freq(869, 'MHZ'), None))
        # self.device.send((self.api.set_center_freq(869, 'MHZ'), None))
        # self.device.send((self.api.set_freq_span(150, 'KHZ'), None))
        self.device.send((self.api.get_center_freq(), self.center_freg_handler))
        self.device.send((self.api.get_freq_span(), self.span_handler))
        self.device.send((self.api.get_start_freq(), self.start_freq_handler))
        self.device.send((self.api.get_stop_freq(), self.stop_freq_handler))
        self.device.send((self.api.get_threshold(), self.threshold_handler))
        self.device.send((self.api.set_continues_sweep(), None))
        self.device.send((self.api.set_trace_type(1, 'MAXH'), None))
        self.device.send((self.api.set_continues_peak_search(1, True), None))
        self.device.send((self.api.set_peak_table_state(True), None))

    def center_freg_handler(self, data: bytes) -> None:
        self.center_freq_spin_box.setValue(int(literal_eval(data.decode()) // 1e6))

    def span_handler(self, span_data: bytes) -> None:
        self.span_freq_spin_box.setValue(int(literal_eval(span_data.decode()) // 1e3))

    def start_freq_handler(self, start_freq: bytes) -> None:
        self.start_freq_spin_box.setValue(int(literal_eval(start_freq.decode()) // 1e6))

    def stop_freq_handler(self, stop_freq: bytes) -> None:
        self.stop_freq_spin_box.setValue(int(literal_eval(stop_freq.decode()) // 1e6))

    def threshold_handler(self, threshold: bytes) -> None:
        self.trig_min_spin_box.setValue(int(literal_eval(threshold.decode())))

    def on_set_freq_button_pressed(self) -> None:
        units_start: str = self.start_freq_units_combo_box.currentText().upper()
        start_freq: int = self.start_freq_spin_box.value()
        units_stop: str = self.stop_freq_units_combo_box.currentText().upper()
        stop_freq: int = self.stop_freq_spin_box.value()

        self.device.send((self.api.set_start_freq(start_freq,
                                                 units_start), None))  # type: ignore
        self.device.send((self.api.set_stop_freq(stop_freq,
                                                units_stop), None))  # type: ignore


    def on_set_freq_span_button_pressed(self) -> None:
        units_cent: str = self.center_freq_units_combo_box.currentText().upper()
        start_freq: int = self.center_freq_spin_box.value()
        units_span: str = self.span_freq_units_combo_box.currentText().upper()
        span_freq: int = self.span_freq_spin_box.value()

        self.device.send((self.api.set_center_freq(start_freq,
                                                  units_cent), None))  # type: ignore
        self.device.send((self.api.set_freq_span(span_freq,
                                                units_span), None))  # type: ignore

    def parse_peak_data(self, data: bytes) -> None:
        self.peaks = self.api.parse_measured_data(data)

    def on_measure_peaks_button_pressed(self) -> None:
        trig_max: int = self.trig_max_spin_box.value()
        trig_min: int = self.trig_min_spin_box.value()
        order_list: list[str] = ['AMPL', 'FREQ', 'TIME']
        peak_order: str = order_list[self.peak_order_combo_box.currentIndex()]
        self.device.send((self.api.calculate_peaks(1, trig_min, trig_max,
                                                   peak_order),  # type: ignore
                          self.parse_peak_data))
        if self.auto_restart_check_box.isChecked():
            time.sleep(0.1)
            self.device.send((self.api.restart_measure(), None))

    def on_set_color_theme_button_pressed(self) -> None:
        themes: list[str] = ['TDC', 'TDM', 'FCOL', 'FMON']
        theme: str = themes[self.theme_combo_box.currentIndex()]
        self.device.send((self.api.set_screenshot_theme(theme), None))  # type: ignore

    def on_save_screen_button_pressed(self) -> None:
        filename: str = self.screenshot_filename_line_edit.text()
        self.device.send((self.api.save_screenshot(filename), None))

    def on_power_down_button_pressed(self) -> None:
        self.device.send((self.api.power_down('NORMAL'), None))

    def on_restart_measure_button_pressed(self):
        self.device.send((self.api.restart_measure(), None))

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = N9010A_Controller('169.254.135.110')
    w.show()
    app.exec()
