import json
from device.dg4202 import DG4202, DG4202Detector, DG4202Mock
from datetime import datetime, timedelta
import time
from features.scheduler import Scheduler
from features.managers import StateManager, DG4202Manager, EDUX1002AManager
from pathlib import Path
import os
from device.data import DataBuffer
import threading
import pyvisa
#DG4202_MOCK_DEVICE = DG4202Mock()
STATE_FILE = Path(os.getenv("DATA"), "state.json")
app_start_time = time.time()
# ======================================================== #
# Place holder globals, these are initialized in app.py
# ======================================================== #
resource_manager: pyvisa.ResourceManager = None
state_manager: StateManager = None
dg4202_manager: DG4202Manager = None
edux1002a_manager: EDUX1002AManager = None
DG4202SCHEDULER: Scheduler = None
# ======================================================== #
# ===================DATA BUFFERS========================= #
# ======================================================== #
