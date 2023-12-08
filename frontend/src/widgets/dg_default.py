from datetime import datetime

import pyqtgraph as pg
from features.managers import DG4202Manager
from pages import plotter
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from device.dg4202 import DG4202

NOT_FOUND_STRING = "Device not found!"
TIMER_INTERVAL = 1000.0  # in ms
TIMER_INTERVAL_S = TIMER_INTERVAL / 1000.0  # in ms

DEFAULT_TAB_STYLE = {"height": "30px", "padding": "2px"}


class DG4202DefaultWidget(QWidget):
    def check_connection(self) -> bool:
        self.my_generator = self.dg4202_manager.get_device()
        self.all_parameters = self.dg4202_manager.get_data()
        if self.my_generator is not None:
            is_alive = self.my_generator.is_connection_alive()
            if not is_alive:
                self.my_generator = None
            return is_alive
        return False

    def __init__(
        self, dg4202_manager: DG4202Manager, parent=None, args_dict: dict = None
    ):
        super().__init__(parent=parent)
        self.args_dict = args_dict
        self.channel_count = 2
        self.link_channel = False
        self.dg4202_manager = dg4202_manager
        self.my_generator = self.dg4202_manager.get_device()
        self.all_parameters = self.dg4202_manager.get_data()
        # Init UI
        self.initUI()

    def create_widgets(self):
        # A dictionary to store widgets for each channel by channel number
        self.controls = {}

        for channel in range(1, self.channel_count + 1):
            # Main controls widget
            main_controls_widget = self.generate_main_controls(channel)

            # Individual control widgets
            waveform_control = self.generate_waveform_control(channel)
            sweep_control = self.generate_sweep_control(channel)

            # Store widgets in dictionary
            self.controls[channel] = {
                "main_controls": main_controls_widget,
                "waveform_control": waveform_control,
                "sweep_control": sweep_control,
            }

    def initUI(self):
        self.create_widgets()
        self.main_layout = QVBoxLayout()
        self.check_connection()
        self.connection_status_label = QLabel(
            f"Connection Status: {self.all_parameters['connected']}"
        )  # Placeholder for connection status
        self.main_layout.addWidget(self.connection_status_label)
        self.status_label = QLabel("")
        self.main_layout.addWidget(self.status_label)
        for _, widgets in self.controls.items():
            # Add main controls for the channel

            tab_widget = QTabWidget()
            tab_widget.addTab(widgets["waveform_control"], "Default")
            tab_widget.addTab(widgets["sweep_control"], "Sweep")
            self.main_layout.addWidget(tab_widget)
            tab_widget.currentChanged.connect(self.on_tab_changed)
            self.main_layout.addWidget(widgets["main_controls"])

        self.setLayout(self.main_layout)

    def generate_main_controls(self, channel: int) -> QWidget:
        # Setting up Timer Modal (Dialog)
        timer_modal = QDialog(self)
        timer_modal.setWindowTitle("Timer")

        timer_layout = QVBoxLayout()

        duration_layout = QHBoxLayout()
        duration_layout.addWidget(QLabel("Duration"))
        duration_input = QLineEdit()
        duration_layout.addWidget(duration_input)

        timer_units = QComboBox()
        timer_units.addItems(["ms", "s", "m", "h"])
        duration_layout.addWidget(timer_units)
        timer_layout.addLayout(duration_layout)

        # ... (more widgets and layouts can be added in a similar manner)

        timer_modal.setLayout(timer_layout)

        # Setting up Scheduler Modal (Dialog)
        scheduler_modal = QDialog(self)
        scheduler_modal.setWindowTitle("Scheduler")

        # ... (similarly, add layouts and widgets for this modal)

        # Setting up main layout
        main_layout = QVBoxLayout()

        control_layout = QHBoxLayout()
        # Adding tabs for modes
        # Add more tabs as needed
        output_btn = QPushButton(f"Output CH{channel}")
        output_btn.clicked.connect(lambda: self.toggle_output(output_btn, channel))
        self.update_button_state(output_btn, channel)
        control_layout.addWidget(output_btn)

        timer_btn = QPushButton(f"Timer CH{channel}")
        timer_btn.clicked.connect(timer_modal.exec)
        control_layout.addWidget(timer_btn)

        scheduler_btn = QPushButton(f"Scheduler CH{channel}")
        scheduler_btn.clicked.connect(scheduler_modal.exec)
        control_layout.addWidget(scheduler_btn)
        # ... (more buttons/widgets to be added)

        main_layout.addLayout(control_layout)

        # Create a QWidget to return
        main_controls_widget = QWidget()
        main_controls_widget.setLayout(main_layout)
        return main_controls_widget

    def generate_sweep_control(self, channel: int) -> QWidget:
        """
        Generate the control components for the sweep mode.

        Parameters:
            channel (int): The channel number.

        Returns:
            QWidget: The widget containing the sweep control components.
        """

        # ---- LEFT COLUMN ---- #
        left_column_layout = QFormLayout()

        # Sweep input
        sweep_input = QLineEdit(self)
        sweep_input.setPlaceholderText(f"Sweep duration frequency CH{channel}")
        left_column_layout.addRow("Sweep (s):", sweep_input)

        # Return time input
        rtime_input = QLineEdit(self)
        rtime_input.setPlaceholderText(f"Sweep return time CH{channel}")
        left_column_layout.addRow("Return (ms):", rtime_input)

        # Start frequency input
        fstart_input = QLineEdit(self)
        fstart_input.setPlaceholderText(f"Sweep start frequency CH{channel}")
        left_column_layout.addRow("Start (Hz):", fstart_input)

        # Stop frequency input
        fstop_input = QLineEdit(self)
        fstop_input.setPlaceholderText(f"Sweep stop frequency CH{channel}")
        left_column_layout.addRow("Stop (Hz):", fstop_input)

        # Set parameters button
        set_parameters_button = QPushButton(f"Set Parameters CH{channel}", self)
        set_parameters_button.clicked.connect(
            lambda: self.update_sweep(
                channel,
                sweep_input.text(),
                rtime_input.text(),
                fstart_input.text(),
                fstop_input.text(),
                plot_data,
            )
        )
        left_column_layout.addWidget(set_parameters_button)

        left_widget = QWidget()
        left_widget.setLayout(left_column_layout)

        # ---- RIGHT COLUMN (Sweep Plot) ---- #
        right_column_layout = QVBoxLayout()
        plot_widget = pg.PlotWidget()
        plot_widget.setLabel("left", "Amplitude", units="V")
        plot_widget.setLabel("bottom", "Time", units="s")
        plot_data = plot_widget.plot([], pen="y")
        right_column_layout.addWidget(
            plot_widget, alignment=Qt.AlignmentFlag.AlignCenter
        )

        right_widget = QWidget()
        right_widget.setLayout(right_column_layout)

        # ---- COMBINE AND RETURN ---- #
        main_layout = QHBoxLayout()
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)

        widget = QWidget()
        widget.setLayout(main_layout)
        return widget

    def generate_waveform_control(self, channel: int) -> QWidget:
        """
        Generate the control components for the waveform mode.

        Parameters:
            channel (int): The channel number.

        Returns:
            QWidget: The widget containing the waveform control components.
        """

        # Create main container and layout
        channel_widget = QWidget()
        channel_layout = QHBoxLayout()

        # ---- LEFT COLUMN ---- #
        left_column_layout = QFormLayout()

        # Waveform type dropdown
        waveform_type = QComboBox()
        waveform_type.addItems(DG4202.available_waveforms())
        left_column_layout.addRow(f"Waveform Type CH{channel}", waveform_type)

        # Frequency input
        freq_input = QLineEdit(
            str(self.all_parameters[f"{channel}"]["waveform"]["frequency"])
        )
        left_column_layout.addRow("Frequency (Hz)", freq_input)

        # Amplitude input
        amp_input = QLineEdit(
            str(self.all_parameters[f"{channel}"]["waveform"]["amplitude"])
        )
        left_column_layout.addRow("Amplitude (V)", amp_input)

        # Offset input
        offset_input = QLineEdit(
            str(self.all_parameters[f"{channel}"]["waveform"]["offset"])
        )
        left_column_layout.addRow("Offset (V)", offset_input)

        # Set waveform button
        set_waveform_button = QPushButton(f"Set Waveform CH{channel}")
        set_waveform_button.clicked.connect(
            lambda: self.on_update_waveform(
                channel,
                waveform_type.currentText(),
                float(freq_input.text()),
                float(amp_input.text()),
                float(offset_input.text()),
                plot_data,
            )
        )
        left_column_layout.addRow(set_waveform_button)

        # Add to main layout
        left_widget = QWidget()
        left_widget.setLayout(left_column_layout)
        channel_layout.addWidget(left_widget)

        # ---- RIGHT COLUMN (Waveform Plot) ---- #
        right_column_layout = QVBoxLayout()
        plot_widget = pg.PlotWidget()
        plot_widget.setLabel("left", "Amplitude", units="V")
        plot_widget.setLabel("bottom", "Time", units="s")
        plot_data = plot_widget.plot([], pen="y")
        right_column_layout.addWidget(
            plot_widget, alignment=Qt.AlignmentFlag.AlignCenter
        )

        # Add to main layout
        right_widget = QWidget()
        right_widget.setLayout(right_column_layout)
        channel_layout.addWidget(right_widget)

        # ---- COMBINE AND RETURN ---- #
        channel_widget.setLayout(channel_layout)
        self.update_waveform(channel, plot_data)
        return channel_widget

    def update_sweep(
        self,
        channel: int,
        sweep: float,
        rtime: float,
        fstart: float,
        fstop: float,
        plot_data,
    ):
        if self.check_connection():
            sweep = (
                float(sweep)
                if sweep
                else float(
                    self.all_parameters[f"{channel}"]["mode"]["parameters"]["sweep"][
                        "TIME"
                    ]
                )
            )
            rtime = (
                float(rtime)
                if rtime
                else float(
                    self.all_parameters[f"{channel}"]["mode"]["parameters"]["sweep"][
                        "RTIME"
                    ]
                )
            )
            fstart = (
                float(fstart)
                if fstart
                else float(
                    self.all_parameters[f"{channel}"]["mode"]["parameters"]["sweep"][
                        "FSTART"
                    ]
                )
            )
            fstop = (
                float(fstop)
                if fstop
                else float(
                    self.all_parameters[f"{channel}"]["mode"]["parameters"]["sweep"][
                        "FSTART"
                    ]
                )
            )
            params = {"TIME": sweep, "RTIME": rtime, "FSTART": fstart, "FSTOP": fstop}
            self.my_generator.set_sweep_parameters(channel, params)

    def toggle_output(self, output_btn, channel: int):
        """
        Toggle the output for the given channel.

        Parameters:
            channel (int): The channel number.
        """
        print(channel)
        if self.check_connection():
            set_to = (
                False
                if self.all_parameters[f"{channel}"]["output_status"] == "ON"
                else True
            )
            print(
                f'{channel} is {self.all_parameters[f"{channel}"]["output_status"]} -> {set_to}'
            )
            self.my_generator.output_on_off(channel, set_to)
            self.check_connection()  # updates dictionary
            # Update the button state after toggling the output

        self.update_button_state(output_btn, channel)

    def update_button_state(self, output_btn, channel: int):
        """
        Update the button's appearance and text based on the output status.

        Parameters:
            output_btn (QPushButton): The output button to be updated.
            channel (int): The channel number.
        """
        status = self.all_parameters[f"{channel}"]["output_status"]
        if status == "ON":
            output_btn.setStyleSheet("background-color: green; color: white;")
            output_btn.setText(f"Output CH{channel} ON")
        else:
            output_btn.setStyleSheet("background-color: none; color: black;")
            output_btn.setText(f"Output CH{channel} OFF")

        print(f"Toggling output for CH{channel}")

    def on_tab_changed(self, index):
        # Placeholder for an API call. Replace with actual logic later.
        if index == 0:  # Assuming 0 is the index for the "Sweep" tab
            pass  # API call for "Sweep"
        elif index == 1:  # Assuming 1 is the index for the "Waveform" tab
            pass  # API call for "Waveform"
        # Add more conditions for other tabs

        # Connect the signal

    def on_update_waveform(
        self,
        channel: int,
        waveform_type: str,
        frequency: float,
        amplitude: float,
        offset: float,
        plot_data,
    ):
        """
        Update the waveform parameters and plot.

        Parameters:
            channel (int): The channel number.
            waveform_type (str): The selected waveform type.
            frequency (float): The selected frequency.
            amplitude (float): The selected amplitude.
            offset (float): The selected offset.
            plot_data (float): Plot data reference.
        """
        if self.check_connection():
            frequency = frequency or float(
                self.all_parameters[f"{channel}"]["waveform"]["frequency"]
            )
            amplitude = amplitude or float(
                self.all_parameters[f"{channel}"]["waveform"]["amplitude"]
            )
            offset = offset or float(
                self.all_parameters[f"{channel}"]["waveform"]["offset"]
            )
            waveform_type = (
                waveform_type
                or self.all_parameters[f"{channel}"]["waveform"]["waveform_type"]
            )

            # If a parameter is not set, pass the current value
            self.my_generator.set_waveform(
                channel, waveform_type, frequency, amplitude, offset
            )

            if self.link_channel:
                self.my_generator.set_waveform(
                    2 if channel == 1 else 1,
                    waveform_type,
                    frequency,
                    amplitude,
                    offset,
                )

            # Update some status label or log if you have one
            status_string = f"[{datetime.now().isoformat()}] Waveform updated."
            # Assuming you have a status_label in your UI
            self.status_label.setText(status_string)
            self.update_waveform(channel, plot_data)
        else:
            # Update some status label or log if you have one
            self.status_label.setText(NOT_FOUND_STRING)

    def update_waveform(self, channel, plot_data):
        self.check_connection()
        x_data, y_data = plotter.plot_waveform(
            params=self.all_parameters[f"{channel}"]["waveform"]
        )
        plot_data.setData(x_data, y_data)

    def update_waveform_sweep(self, channel, plot_data):
        self.check_connection()
        x_data, y_data = plotter.plot_sweep(
            start_frequency=self.all_parameters[f"{channel}"]["mode"]["parameters"][
                "sweep"
            ]["FSTART"],
            stop_frequency=self.all_parameters[f"{channel}"]["mode"]["parameters"][
                "sweep"
            ]["FSTOP"],
            sweep=self.all_parameters[f"{channel}"]["mode"]["parameters"]["sweep"][
                "TIME"
            ],
        )
        plot_data.setData(x_data, y_data)
