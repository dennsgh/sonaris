import json
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QLabel, QLineEdit, QWidget


class SchedulerWidget(QWidget):
    def __init__(self, parent=None, args_dict: dict = None):
        super().__init__(parent=parent)
        self.initUI()

    def initUI(self):
        self.setLayout(self.layout)

        # Initially, Channel 2 controls will be disabled
        self.toggle_channel_controls(2, False)

    def initialize_channel_controls(self, channel, start_row):
        # Set up controls for channel using values from self.all_parameters
        mode = self.all_parameters[str(channel)]["mode"]["current_mode"]
        frequency = str(self.all_parameters[str(channel)]["waveform"]["frequency"])
        amplitude = str(self.all_parameters[str(channel)]["waveform"]["amplitude"])
        offset = str(self.all_parameters[str(channel)]["waveform"]["offset"])

        # Add controls to the grid
        mode_combo = QComboBox()
        mode_combo.addItems(["Default", "Sweep"])
        mode_combo.setCurrentText(mode)
        self.grid_layout.addWidget(mode_combo, start_row, 0, 1, 2)  # Span two columns

        freq_input = QLineEdit(frequency)
        self.grid_layout.addWidget(
            QLabel(f"Channel {channel} Frequency (Hz)"), start_row + 1, 0
        )
        self.grid_layout.addWidget(freq_input, start_row + 1, 1)

        amp_input = QLineEdit(amplitude)
        self.grid_layout.addWidget(
            QLabel(f"Channel {channel} Amplitude (V)"), start_row + 2, 0
        )
        self.grid_layout.addWidget(amp_input, start_row + 2, 1)

        offset_input = QLineEdit(offset)
        self.grid_layout.addWidget(
            QLabel(f"Channel {channel} Offset (V)"), start_row + 3, 0
        )
        self.grid_layout.addWidget(offset_input, start_row + 3, 1)

        # Store the controls for later access
        self.channels_params[channel] = {
            "mode_combo": mode_combo,
            "freq_input": freq_input,
            "amp_input": amp_input,
            "offset_input": offset_input,
            # Initialize remaining controls similarly...
        }

        # If Sweep mode, initialize sweep-specific controls
        if mode == "Sweep":
            sweep_time_input = QLineEdit(
                str(
                    self.all_parameters[str(channel)]["mode"]["parameters"]["sweep"][
                        "TIME"
                    ]
                )
            )
            self.grid_layout.addWidget(
                QLabel(f"Channel {channel} Sweep Time (s)"), start_row + 4, 0
            )
            self.grid_layout.addWidget(sweep_time_input, start_row + 4, 1)

            return_time_input = QLineEdit(
                str(
                    self.all_parameters[str(channel)]["mode"]["parameters"]["sweep"][
                        "RTIME"
                    ]
                )
            )
            self.grid_layout.addWidget(
                QLabel(f"Channel {channel} Return Time (s)"), start_row + 5, 0
            )
            self.grid_layout.addWidget(return_time_input, start_row + 5, 1)

            start_freq_input = QLineEdit(
                str(
                    self.all_parameters[str(channel)]["mode"]["parameters"]["sweep"][
                        "FSTART"
                    ]
                )
            )
            self.grid_layout.addWidget(
                QLabel(f"Channel {channel} Start Frequency (Hz)"), start_row + 6, 0
            )
            self.grid_layout.addWidget(start_freq_input, start_row + 6, 1)

            stop_freq_input = QLineEdit(
                str(
                    self.all_parameters[str(channel)]["mode"]["parameters"]["sweep"][
                        "FSTOP"
                    ]
                )
            )
            self.grid_layout.addWidget(
                QLabel(f"Channel {channel} Stop Frequency (Hz)"), start_row + 7, 0
            )
            self.grid_layout.addWidget(stop_freq_input, start_row + 7, 1)

            # Add sweep-specific controls to channels_params
            self.channels_params[channel].update(
                {
                    "sweep_time_input": sweep_time_input,
                    "return_time_input": return_time_input,
                    "start_freq_input": start_freq_input,
                    "stop_freq_input": stop_freq_input,
                }
            )

    def toggle_channel_2(self, state):
        # Enable or disable Channel 2 controls based on the checkbox state
        self.toggle_channel_controls(2, state == Qt.CheckState.Checked)

    def toggle_channel_controls(self, channel, enabled):
        for control in self.channels_params[channel].values():
            control.setEnabled(enabled)
            if not enabled:
                control.setStyleSheet("background-color: #e0e0e0; color: #a0a0a0;")
            else:
                control.setStyleSheet("")

    def start_experiment(self):
        # Gather the parameters for both channels
        ch1_params = self.get_channel_parameters(1)
        ch2_params = (
            self.get_channel_parameters(2)
            if self.enable_channel_checkbox.isChecked()
            else None
        )

        # Log experiment start
        self.log_experiment_details(ch1_params, ch2_params)

        # TODO: Configure the generator with the collected parameters
        # self.dg4202_manager.configure_experiment(ch1_params, ch2_params)

    def get_channel_parameters(self, channel: int):
        params = self.all_parameters[channel]
        return {
            "mode": params["mode_combo"].currentText(),
            "frequency": params["freq_input"].text(),
            "amplitude": params["amp_input"].text(),
            "offset": params["offset_input"].text(),
            "sweep_time": params["sweep_time_input"].text(),
            "return_time": params["return_time_input"].text(),
            "start_frequency": params["start_freq_input"].text(),
            "stop_frequency": params["stop_freq_input"].text(),
        }

    def log_experiment_details(self, ch1_params, ch2_params):
        log_details = {
            "timestamp": datetime.now().isoformat(),
            "channel_1": ch1_params,
            "channel_2": ch2_params,
        }
        with open("experiment_log.json", "w") as log_file:
            json.dump(log_details, log_file, indent=4)
