import asyncio
from types import SimpleNamespace

_device_mapping = {
    "Galil RBV": "galil_rbv",
    "Galil VAL": "galil_val",
    "ION Power": "ION_Pump_PS.Pwr",
    "ION Current": "ION_Pump_PS.I",
    "ION Voltage": "ION_Pump_PS.E",
    "ION Power SP": "ION_Pump_PS.Pwr_SP",
    "ION Current SP": "ION_Pump_PS.I_SP",
    "ION Voltage SP": "ION_Pump_PS.E_SP",
    "ION Arc Rate": "ION_Pump_PS.Rate_Arc",
    "ION KWH Count": "ION_Pump_PS.Cnt_Target_KwHr",
    "ION Output Enable": "ION_Pump_PS.Enbl_Out_Cmd",
    # "ION Output Status": "ION_Pump_PS.Enbl_Out_Sts",
}

_required_devices = ("galil", "galil_val", "galil_rbv", "ION_Pump_PS")


def create_shared_context(devices):
    for device in _required_devices:
        if device not in devices:
            raise RuntimeError(f"Device {device} is missing in the devices list")

    return SimpleNamespace(
        devices=SimpleNamespace(**devices),
        galil_abs_rel=0,  # 0 - absolute, 1 - relative
        galil_pos=0,
        galil_speed=1000000,
        device_mapping=_device_mapping,
        required_devices=_required_devices,
        logged_signals={},
        logging_stop_event=asyncio.Event(),
        log_file_path="",
        logging_dir="",
        script_dir="",
        fail_condition_triggered=False,
        _name_to_device={},
    )
