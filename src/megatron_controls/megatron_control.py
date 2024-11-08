import os
import bluesky.plan_stubs as bps
from megatron.exceptions import CommandNotFoundError, StopScript
from megatron.support import wait_for_condition
import inspect

active_failif_conditions = {}

def process_megatron_command(command, args, context, current_script_path=None):
    command_dispatcher = {
        "email": email,
        "exit": exit_command,
        "failif": failif,
        "failifoff": failifoff,
        "l": l_command,
        "log": log,
        "lograte": lograte,
        "print": print_command,
        "run": run,
        "setao": setao,
        "setdo": setdo,
        "stop": stop,
        "t": t_command,
        "var": var,
        "waitai": waitai,
        "waitdi": waitdi
    }

    if command in command_dispatcher:
        command_function = command_dispatcher[command]

        sig = inspect.signature(command_function)
        params = list(sig.parameters)

        kwargs = {"args": args, "context": context, "current_script_path": current_script_path}
        dynamic_args = [kwargs[param] for param in params if param in kwargs]

        yield from command_function(*dynamic_args)
    else:
        raise CommandNotFoundError(command)

def l_command(block, context):
    for line in block:
        yield from process_megatron_command(line[0], line[1:], context)

def t_command(args):
    timer_duration = float(args[0])
    print(f"Executing timer for {timer_duration} seconds")
    yield from bps.sleep(timer_duration)

def exit_command():
    print("Exiting the interpreter.")
    raise SystemExit

def lograte(args):
    print(f"Setting lograte to {args[0]}")
    yield from bps.null()

def email(args):
    subject = args[0]
    message = args[1]
    recipients = args[2:]
    print(f"Sending email with subject '{subject}' to {recipients}")
    yield from bps.null()

def failif(args, context):
    pv_name, expected_value, fail_script = args
    print(f"Setting failif on {pv_name} for value {expected_value}.")

    device_name = context.device_mapping.get(pv_name)
    if not device_name:
        raise RuntimeError(f"PV {pv_name} not found in device mapping.")

    pv_signal = getattr(context.devices, device_name)
    if not pv_signal:
        raise RuntimeError(f"Signal for {pv_name} not found.")

    def check_pv_value(value, **kwargs):
        if value == expected_value:
            print(f"Failif triggered! {pv_name} reached value {expected_value}. Running {fail_script}.")
            called_script_path = os.path.join(context.script_dir, fail_script)
            context.run_script_callback(called_script_path)

    token = pv_signal.subscribe(check_pv_value)
    active_failif_conditions[pv_name] = (pv_signal, token)
    yield from bps.null()

def failifoff(args):
    pv_name = args[0]
    if pv_name in active_failif_conditions:
        pv_signal, token = active_failif_conditions.pop(pv_name)
        pv_signal.clear_sub(token)
        print(f"Failif condition disabled for {pv_name}.")
    else:
        print(f"No active failif condition found for {pv_name}.")
    yield from bps.null()

def log(args, context):
    signal_name = args[0]
    if signal_name in context.device_mapping:
        signal_device_name = context.device_mapping[signal_name]
        signal = getattr(context.devices, signal_device_name)
        context.logged_signals[signal_name] = signal 
        print(f"Added {signal_name} to logging signals.")
    else:
        raise RuntimeError(f"Signal {signal_name} not found in device mapping.")
    yield from bps.null()


def print_command(args):
    text = ' '.join(args)
    print(f"Executing 'print' command with text: {text}")
    yield from bps.null()

def run(args, context):
    script_name = args[0]

    called_script_path = os.path.join(context.script_dir, script_name)
    print(f"Running script: {script_name} ({called_script_path})")

    yield from context.run_script_callback(called_script_path)

def setao(args):
    sp = args[0]
    value = float(args[1])
    print(f"Setting analog output {sp} to {value}")
    yield from bps.null()

def setdo(args):
    pv = args[0]
    value = int(args[1])
    print(f"Setting digital output {pv} to {value}")
    yield from bps.null()

def stop(args):
    print("Stopping the current script.")
    raise StopScript()

def var(args):
    variable = args[0]
    expression = args[1]
    print(f"Setting variable {variable} to {expression}")
    yield from bps.null()

def waitai(args, context):
    source = args[0]
    operator = args[1]
    value = float(args[2])
    tolerance = float(args[3]) if len(args) > 3 else 0
    timeout = float(args[4]) if len(args) > 4 else None

    if source in context.device_mapping:
        device_name = context.device_mapping[source]
        signal = getattr(context.devices, device_name)
    else:
        raise RuntimeError(f"Unrecognized device name: {source!r}")

    yield from wait_for_condition(
        signal=signal, target=value / 1000000, operator=operator, tolerance=tolerance, timeout=timeout
    )

def waitdi(args, context):
    source = args[0]
    value = int(args[1])
    timeout = float(args[2]) if len(args) > 2 else None

    if source in context.device_mapping:
        device_name = context.device_mapping[source]
        signal = getattr(context.devices, device_name)
    else:
        raise RuntimeError(f"Unrecognized device name: {source!r}")

    yield from wait_for_condition(
        signal=signal, target=value / 1000000, operator="==", tolerance=0, timeout=timeout
    )
