import json
from datetime import datetime

from features.managers import DG4202Manager
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class DG4202ExperimentWidget(QWidget):
    def __init__(
        self, dg4202_manager: DG4202Manager, parent=None, args_dict: dict = None
    ):
        super().__init__(parent=parent)
        self.dg4202_manager = dg4202_manager
        self.my_generator = self.dg4202_manager.get_device()
        self.all_parameters = self.dg4202_manager.data_source.query_data()
        self.input_params = {1: {}, 2: {}}
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        # Checkbox to enable Channel 2
        self.enable_channel_checkbox = QCheckBox("Enable Channel 2")
        self.enable_channel_checkbox.stateChanged.connect(self.toggle_channel_2)
        self.layout.addWidget(self.enable_channel_checkbox)

        # Create input fields for both channels using a grid layout
        self.grid_layout = QGridLayout()

        # Initialize input fields for both channels
        for channel in range(1, 3):
            row = (channel - 1) * 8  # Start new channel setup at a new row
            self.initialize_channel_controls(channel, row)

        # Add layouts to main layout
        self.layout.addLayout(self.grid_layout)
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
            self.input_params[channel].update(
                {
                    "TIME": sweep_time_input,
                    "RTIME": return_time_input,
                    "FSTART": start_freq_input,
                    "FSTOP": stop_freq_input,
                }
            )

    def toggle_channel_2(self, state):
        # Enable or disable Channel 2 controls based on the checkbox state
        self.toggle_channel_controls(2, state == Qt.CheckState.Checked)

    def toggle_channel_controls(self, channel, enabled):
        for control in self.input_params[channel].values():
            control.setEnabled(enabled)
            if not enabled:
                control.setStyleSheet("background-color: #e0e0e0; color: #a0a0a0;")
            else:
                control.setStyleSheet("")
