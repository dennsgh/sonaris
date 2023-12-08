import os
import time
from pathlib import Path

import pyvisa
from features.managers import DG4202Manager, EDUX1002AManager, StateManager

from scheduler.timekeeper import Timekeeper
from scheduler.worker import Worker

# DG4202_MOCK_DEVICE = DG4202Mock()
STATE_FILE = Path(os.getenv("DATA"), "state.json")
app_start_time = time.time()
# ======================================================== #
# Place holder globals, these are initialized in app.py
# ======================================================== #
resource_manager: pyvisa.ResourceManager = None
state_manager: StateManager = None
dg4202_manager: DG4202Manager = None
edux1002a_manager: EDUX1002AManager = None
# ======================================================== #
# ===================Worker Modules======================= #
# ======================================================== #
timekeepeer: Timekeeper = None
worker: Worker = None
