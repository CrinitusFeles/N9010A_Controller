from ast import literal_eval
import asyncio
from datetime import datetime
from pathlib import Path
import struct
from PyQt6 import QtWidgets
import qasync
import numpy as np
import matplotlib.pyplot as plt
from PyQt6.uic.load_ui import loadUi
from n9010a_controller.n9010a_api import N9010A_API
from n9010a_controller.pyqt_client._widgets import _Widgets
from python_tcp.aio.client import SocketClient


class N9010A_Controller(QtWidgets.QWidget, _Widgets):
    def __init__(self, ip: str = '') -> None:
        super().__init__()
        loadUi(Path(__file__).parent.joinpath('N9010A.ui'), self)
        self.api = N9010A_API()
        self.device = SocketClient(ip, 5025)
        self.device.connected.subscribe(self.on_successfull_connection)
        self.device.received.subscribe(lambda x: print(x))
        self.ip_line_edit.setText(ip)
        self.peaks: list[tuple[float, float]] = []
        self.processing_label.setVisible(False)
        self.peak_group_box.setVisible(False)
        self.stitching_progress_bar.setVisible(False)
        self.mech_att_check_box.toggled.connect(self.on_auto_att_toggled)

    def connection_status(self) -> bool:
        return self.device._connection_status

    def on_auto_att_toggled(self, state: bool):
        self.mech_att_spin_box.setEnabled(not state)

    @qasync.asyncSlot()
    async def on_send_cmd_button_pressed(self):
        cmd = self.custom_cmd_line_edit.text() + '\n'
        if '?' in cmd:
            print(await self.device.txrx(cmd.encode('ascii')))
        else:
            await self.device.send(cmd.encode('ascii'))

    @qasync.asyncSlot()
    async def on_read_button_pressed(self):
        try:
            buffer = await asyncio.wait_for(self.device.reader.read(1024), 1.5)
            print(buffer)
        except TimeoutError:
            print('timeout')

    @qasync.asyncSlot()
    async def on_sweep_config_button_pressed(self):
        rbw = int(self.rbw_dspin_box.value() * 1e3)
        vbw = int(self.vbw_dspin_box.value() * 1e3)
        points: int = self.points_spin_box.value()
        aver_count: int = self.aver_count_spin_box.value()

        await self.device.send(self.api.set_points_amount(points))
        await self.device.send(self.api.set_res_bandwidth(rbw, 'HZ'))
        await self.device.send(self.api.set_video_bandwidth(vbw, 'HZ'))
        await self.device.send(self.api.set_averaging(True))
        await self.device.send(self.api.set_averaging_amount(aver_count))

    @qasync.asyncSlot()
    async def on_read_san_button_pressed(self):
        result = await self._single_sweep()
        if result is not None:
            data = result.reshape((-1, 2)).T
            self._save_result(data)
            plt.scatter(data[0], data[1], s=5)
            plt.plot(*data)
            plt.show()

    def _save_result(self, data: np.ndarray):
        folder_path: Path = Path.cwd() / 'Measurements'
        folder_path.mkdir(exist_ok=True)
        ts: str = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        filename: str = ts + '.csv'
        np.savetxt(folder_path / filename, data.T, delimiter=';', fmt='%.3f')

    @qasync.asyncSlot()
    async def on_start_stitching_button_pressed(self):
        from_hz = int(self.from_dspin_box.value() * 1e6)
        to_hz = int(self.to_dspin_box.value() * 1e6)
        step_hz = int(self.step_dspin_box.value() * 1e6)
        steps: int = (to_hz - from_hz) // step_hz
        self.stitching_progress_bar.setValue(0)
        self.stitching_progress_bar.setVisible(True)
        result = np.array([])
        for i, freq in enumerate(range(from_hz, to_hz, step_hz), 1):
            await self.device.send(self.api.set_start_freq(freq, 'HZ'))
            await self.device.send(self.api.set_stop_freq(freq + step_hz, 'HZ'))
            step_result = await self._single_sweep()
            if step_result is not None:
                result = np.append(result, step_result)
            progress = i / steps * 100
            self.stitching_progress_bar.setValue(int(progress))
        self.stitching_progress_bar.setVisible(False)
        self._save_result(result)
        data = result.reshape((-1, 2)).T
        plt.scatter(data[0], data[1], s=5)
        plt.plot(*data)
        plt.show()

    async def _single_sweep(self):
        buffer = b''
        await self.device.send(self.api.read_san(1))
        self.processing_label.setVisible(True)
        try:
            buffer += await asyncio.wait_for(self.device.reader.read(1024), 15)
            header: int = literal_eval(buffer[1:2].decode('ascii')) + 2
            # bytes_amount: int = literal_eval(buffer[2: val + 2].decode('ascii')) // 8
        except TimeoutError:
            print('timeout')
            self.processing_label.setVisible(False)
            return
        while True:
            try:
                buffer += await asyncio.wait_for(self.device.reader.read(1024), 0.1)
            except TimeoutError:
                break
        self.processing_label.setVisible(False)
        result = np.array([struct.unpack('>f', buffer[i:i + 4])[0]
                           for i in range(header, len(buffer), 4)
                           if len(buffer[i:i + 4]) == 4])
        return result



    @qasync.asyncSlot()
    async def on_connect_button_pressed(self) -> None:
        if not self.device.is_connected():
            if await self.device.connect(self.ip_line_edit.text(),
                                        self.port_spin_box.value(),
                                        False):
                self.connect_button.setText('Disconnect')
        else:
            await self.device.disconnect()
            self.connect_button.setText('Connect')


    async def on_successfull_connection(self) -> None:
        print(await self.device.txrx(self.api.identification_query()))
        await self.device.send(self.api.set_mode('SA'))
        await self.device.send(self.api.set_averaging(True))

        center_freq: int = await self._decode_answer(self.api.get_center_freq())
        span: int = await self._decode_answer(self.api.get_freq_span())
        start_freq: int = await self._decode_answer(self.api.get_start_freq())
        stop_freq: int = await self._decode_answer(self.api.get_stop_freq())
        threshold: float = await self._decode_answer(self.api.get_threshold())
        points: int = await self._decode_answer(self.api.get_points_amount())
        rbw: int = await self._decode_answer(self.api.get_res_bandwidth())
        vbw: int = await self._decode_answer(self.api.get_video_bandwidth())
        aver_amount: int = await self._decode_answer(self.api.get_averaging_amount())
        mech_auto: int = await self._decode_answer(self.api.get_mech_attenuation_auto_status())
        self.on_auto_att_toggled(bool(mech_auto))
        mech: int = await self._decode_answer(self.api.get_mech_attenuation())
        elec: int = await self._decode_answer(self.api.get_electronic_attenuation())
        self.rbw_dspin_box.setValue(rbw / 1000)
        self.vbw_dspin_box.setValue(vbw / 1000)
        self.aver_count_spin_box.setValue(aver_amount)
        self.points_spin_box.setValue(points)
        self.center_freq_dspin_box.setValue(center_freq // 1e6)
        self.start_freq_dspin_box.setValue(start_freq // 1e6)
        self.trig_min_spin_box.setValue(int(threshold))
        self.stop_freq_dspin_box.setValue(stop_freq // 1e6)
        self.span_freq_dspin_box.setValue(span // 1e6)
        self.mech_att_check_box.setChecked(bool(mech_auto))
        self.mech_att_spin_box.setValue(mech)
        self.elec_att_spin_box.setValue(elec)
        await self.device.send(self.api.set_continuous_sweep(False))
        await self.device.send(self.api.set_trace_type(1, 'MAXH'))
        # await self.device.send(self.api.set_continues_peak_search(1, True))
        # await self.device.send(self.api.set_peak_table_state(True))

    async def _decode_answer(self, cmd: bytes):
        answer: bytes = await self.device.txrx(cmd)
        return literal_eval(answer.decode())

    @qasync.asyncSlot()
    async def on_set_freq_button_pressed(self) -> None:
        start_freq: int = int(self.start_freq_dspin_box.value() * 1e6)
        stop_freq: int = int(self.stop_freq_dspin_box.value() * 1e6)
        await self.device.send(self.api.set_start_freq(start_freq, 'HZ'))
        await self.device.send(self.api.set_stop_freq(stop_freq, 'HZ'))

    @qasync.asyncSlot()
    async def on_set_freq_span_button_pressed(self) -> None:
        start_freq: int = int(self.center_freq_dspin_box.value() * 1e6)
        span_freq: int = int(self.span_freq_dspin_box.value() * 1e6)
        await self.device.send(self.api.set_center_freq(start_freq, 'HZ'))
        await self.device.send(self.api.set_freq_span(span_freq, 'HZ'))

    @qasync.asyncSlot()
    async def on_mech_att_button_pressed(self):
        auto: bool = self.mech_att_check_box.isChecked()
        if not auto:
            att: int = self.mech_att_spin_box.value()
            await self.device.send(self.api.set_mech_attenuation(att))
        else:
            await self.device.send(self.api.set_mech_attenuation_auto_status(auto))

    @qasync.asyncSlot()
    async def on_elec_att_button_pressed(self):
        att: int = self.elec_att_spin_box.value()
        await self.device.send(self.api.set_electronic_attenuation(att))

    def parse_peak_data(self, data: bytes) -> None:
        self.peaks = self.api.parse_measured_data(data)
        self.meas_result_table.setRowCount(len(self.peaks))
        self.meas_result_table.setColumnCount(2)
        header_labels: list[str] = ["Amplitude, dBm", "Frequency, Hz"]
        self.meas_result_table.setHorizontalHeaderLabels(header_labels)
        for i, (freq, ampl) in enumerate(self.peaks):
            self.meas_result_table.setItem(i, 0, QtWidgets.QTableWidgetItem(f"{freq}"))
            self.meas_result_table.setItem(i, 1, QtWidgets.QTableWidgetItem(f"{ampl}"))
        header = self.meas_result_table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)
            header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

    @qasync.asyncSlot()
    async def on_measure_peaks_button_pressed(self) -> None:
        trig_max: int = self.trig_max_spin_box.value()
        trig_min: int = self.trig_min_spin_box.value()
        order_list: list[str] = ['AMPL', 'FREQ', 'TIME']
        peak_order: str = order_list[self.peak_order_combo_box.currentIndex()]
        cmd: bytes = self.api.calculate_peaks(1, trig_min, trig_max, peak_order) # type: ignore
        data: bytes = await self.device.txrx(cmd)
        self.parse_peak_data(data)
        if self.auto_restart_check_box.isChecked():
            await self.device.txrx(self.api.restart_measure())

    @qasync.asyncSlot()
    async def on_set_color_theme_button_pressed(self) -> None:
        themes: list[str] = ['TDC', 'TDM', 'FCOL', 'FMON']
        theme: str = themes[self.theme_combo_box.currentIndex()]
        await self.device.send(self.api.set_screenshot_theme(theme))  # type: ignore

    @qasync.asyncSlot()
    async def on_save_screen_button_pressed(self) -> None:
        filename: str = self.screenshot_filename_line_edit.text()
        await self.device.send(self.api.save_screenshot(filename))

    @qasync.asyncSlot()
    async def on_power_down_button_pressed(self) -> None:
        await self.device.send(self.api.power_down('NORMAL'))

    @qasync.asyncSlot()
    async def on_restart_measure_button_pressed(self):
        await self.device.send(self.api.restart_measure())

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    w = N9010A_Controller('10.2.63.45')
    event_loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(event_loop)
    app_close_event = asyncio.Event()
    app.aboutToQuit.connect(app_close_event.set)
    w.show()
    with event_loop:
        event_loop.run_until_complete(app_close_event.wait())
