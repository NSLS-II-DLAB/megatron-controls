from types import SimpleNamespace

_device_mapping = {
    "Galil RBV": "galil_rbv",
    "Galil VAL": "galil_val",
    "ION Power": "ION_Pump_PS.Pwr_I",
    "ION Current": "ION_Pump_PS.I_I",
    "ION Voltage": "ION_Pump_PS.E_I",
    "ION Arc Rate": "ION_Pump_PS.Rate_Arc_I",
    "ION KWH Count": "ION_Pump_PS.Cnt_Target_KwHr_RB",
    "ION Output Enable": "ION_Pump_PS.Enbl_Out_Cmd",
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
        script_dir="",
        fail_condition_triggered=False,
        _name_to_device={},
    )
