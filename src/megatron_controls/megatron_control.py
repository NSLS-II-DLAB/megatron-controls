import asyncio
import inspect
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import bluesky.plan_stubs as bps
import matplotlib
import pandas as pd
from dotenv import load_dotenv

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .exceptions import CommandNotFoundError, StopScript
from .support import wait_for_condition

active_failif_conditions = {}

load_dotenv()

EMAIL_ADDRESS = str(os.getenv("GMAIL_USER"))
EMAIL_PASSWORD = str(os.getenv("GMAIL_PASS"))


def process_megatron_command(command, args, context, current_script_path=None):
    command_dispatcher = {
        "email": email,
        "exit": exit_command,
        "failif": failif,
        "failifoff": failifoff,
        "l": l_command,
        "log": log,
        "lograte": lograte,
        "plot": plot,
        "print": print_command,
        "run": run,
        "set": set,
        "setao": setao,
        "setdo": setdo,
        "stop": stop,
        "t": t_command,
        "var": var,
        "waitai": waitai,
        "waitdi": waitdi,
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


def lograte(args, context):
    try:
        log_rate = float(args[0])
        print(f"Setting log rate to {log_rate} seconds.")

        if hasattr(context, "logging_stop_event") and context.logging_stop_event:
            print("Stopping existing logging...")
            context.logging_stop_event.set()

        context.logging_stop_event = asyncio.Event()

        async def logging_coro():
            await asyncio.sleep(0)
            stop_event = context.logging_stop_event
            while not stop_event.is_set():
                is_new_file = False
                log_file_path = context.log_file_path
                signals = context.logged_signals

                if not os.path.isfile(log_file_path):
                    dir, _ = os.path.split(log_file_path)
                    os.makedirs(dir, exist_ok=True)
                    is_new_file = True

                timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

                with open(log_file_path, "at") as f:
                    if is_new_file:
                        headers = ",".join([f'"{_}"' for _ in signals.keys()])
                        f.write(f"Timestamp,{headers}\n")

                    values = [signals[_].value for _ in signals.keys()]
                    row = ",".join([f"{_:.6f}" if isinstance(_, float) else f"{_}" for _ in values])
                    f.write(f"{timestamp},{row}\n")

                await asyncio.sleep(log_rate)

        print("Starting periodic logging with new log rate.")
        yield from bps.sleep(0)
        asyncio.ensure_future(logging_coro())

    except ValueError:
        print(f"Invalid log rate: {args[0]}. Must be a number.")
    except Exception as e:
        print(f"Failed to set log rate: {e}")

    yield from bps.null()


def email(args):
    subject = args[0]
    message = args[1]
    recipients = args[2:]

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, recipients, msg.as_string())
        print(f"Email sent successfully to {', '.join(recipients)}")
    except Exception as e:
        print(f"Failed to send email: {e}")

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


def log(args):
    pv_name = args[0]
    print(f"Logging for {pv_name} has been set up.")
    yield from bps.null()


def plot(args, context):
    if len(args) == 1 and args[0].lower() == "dump":
        print("Dumping current logged signals:")
        for pv_name, signal in context.logged_signals.items():
            print(f"{pv_name}: {signal.value}")
        yield from bps.null()
        return

    pv_names = []
    geometry_args = []
    for arg in args:
        if arg.startswith("+"):
            geometry_args.extend(arg[1:].split(","))
        elif all(char.isdigit() or char == "," for char in arg):
            geometry_args.extend(arg.split(","))
        else:
            pv_names.append(arg)

    if not pv_names:
        print("Error: No PVs specified for plotting.")
        yield from bps.null()
        return

    if not os.path.isfile(context.log_file_path):
        print("Error: Log file does not exist. Please ensure logging is enabled.")
        yield from bps.null()
        return

    try:
        df = pd.read_csv(context.log_file_path, comment=None, header=0, skip_blank_lines=True)
        df.columns = df.columns.str.strip('"')
        df = df.reset_index(drop=True)
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    except Exception as e:
        print(f"Error reading log file: {e}")
        yield from bps.null()
        return

    missing_pvs = [pv for pv in pv_names if pv not in df.columns]
    if missing_pvs:
        print(f"Error: The following PVs are not in the log file: {', '.join(missing_pvs)}")
        yield from bps.null()
        return

    plt.figure(figsize=(8, 6))
    for pv_name in pv_names:
        plt.plot(df["Timestamp"], df[pv_name], label=pv_name)

    plt.title("PV Data Over Time")
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.legend()

    if geometry_args:
        try:
            x, y, w, h = map(int, geometry_args)
            plt.gcf().set_size_inches(w / 100, h / 100)
        except ValueError:
            print(f"Invalid geometry format: {geometry_args}")
            yield from bps.null()
            return

    plot_dir = os.path.join(context.logging_dir, "plots")
    os.makedirs(plot_dir, exist_ok=True)

    plot_filename = os.path.join(plot_dir, f"plot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
    plt.savefig(plot_filename)
    plt.close()

    print(f"Plot saved to {plot_filename}")
    yield from bps.null()


def print_command(args):
    text = " ".join(args)
    print(f"Executing 'print' command with text: {text}")
    yield from bps.null()


def run(args, context):
    script_name = args[0]

    called_script_path = os.path.join(context.script_dir, script_name)
    print(f"Running script: {script_name} ({called_script_path})")

    yield from context.run_script_callback(called_script_path)


def set(args, context):
    dev_name = args[0]
    v = args[1]
    value = v if isinstance(v, str) else int(v)
    device = context._name_to_device[dev_name]
    print(f"Setting digital output: device={dev_name!r} value={value!r}")
    yield from bps.abs_set(device, value, wait=True)


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
