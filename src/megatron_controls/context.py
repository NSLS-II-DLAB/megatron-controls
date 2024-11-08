from types import SimpleNamespace

_device_mapping = {
    "Galil RBV": "galil_rbv",
    "Galil VAL": "galil_val"
}

_required_devices = ("galil", "galil_val", "galil_rbv")

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
        script_dir = "",
        fail_condition_triggered = False, 
    )
