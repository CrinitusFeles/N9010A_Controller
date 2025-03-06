from PyQt6 import QtWidgets


class _Widgets:
    ip_line_edit: QtWidgets.QLineEdit
    screenshot_filename_line_edit: QtWidgets.QLineEdit
    custom_cmd_line_edit: QtWidgets.QLineEdit

    meas_result_table: QtWidgets.QTableWidget

    connect_button: QtWidgets.QPushButton
    save_screen_button: QtWidgets.QPushButton
    set_color_theme_button: QtWidgets.QPushButton
    set_freq_button: QtWidgets.QPushButton
    set_freq_span_button: QtWidgets.QPushButton
    measure_peaks_button: QtWidgets.QPushButton
    power_down_button: QtWidgets.QPushButton
    restart_measure_button: QtWidgets.QPushButton
    send_cmd_button: QtWidgets.QPushButton
    read_san_button: QtWidgets.QPushButton
    read_button: QtWidgets.QPushButton
    start_stitching_button: QtWidgets.QPushButton
    sweep_config_button: QtWidgets.QPushButton
    mech_att_button: QtWidgets.QPushButton
    elec_att_button: QtWidgets.QPushButton

    start_freq_dspin_box: QtWidgets.QDoubleSpinBox
    stop_freq_dspin_box: QtWidgets.QDoubleSpinBox
    center_freq_dspin_box: QtWidgets.QDoubleSpinBox
    span_freq_dspin_box: QtWidgets.QDoubleSpinBox
    trig_max_spin_box: QtWidgets.QSpinBox
    trig_min_spin_box: QtWidgets.QSpinBox
    port_spin_box: QtWidgets.QSpinBox
    points_spin_box: QtWidgets.QSpinBox
    aver_count_spin_box: QtWidgets.QSpinBox
    mech_att_spin_box: QtWidgets.QSpinBox
    elec_att_spin_box: QtWidgets.QSpinBox
    vbw_dspin_box: QtWidgets.QDoubleSpinBox
    rbw_dspin_box: QtWidgets.QDoubleSpinBox
    from_dspin_box: QtWidgets.QDoubleSpinBox
    to_dspin_box: QtWidgets.QDoubleSpinBox
    step_dspin_box: QtWidgets.QDoubleSpinBox

    peak_order_combo_box: QtWidgets.QComboBox
    theme_combo_box: QtWidgets.QComboBox

    auto_restart_check_box: QtWidgets.QCheckBox
    mech_att_check_box: QtWidgets.QCheckBox
    processing_label: QtWidgets.QLabel
    peak_group_box: QtWidgets.QGroupBox
    stitching_progress_bar: QtWidgets.QProgressBar