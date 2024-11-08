import bluesky.plan_stubs as bps
from megatron.exceptions import CommandNotFoundError
from megatron.support import motor_move, motor_stop, motor_home
import inspect

def process_motor_command(command, args, context):
    command_dispatcher = {
        "ac": ac, "af": af, "ba": ba, "bg": bg, "bi": bi, "bl": bl, "bm": bm,
        "bt": bt, "bz": bz, "cc": cc, "ce": ce, "cn": cn, "dc": dc, "dp": dp,
        "er": er, "fa": fa, "fe": fe, "fl": fl, "fv": fv, "hm": hm, "hv": hv, 
        "ib": ib, "iht": iht, "il": il, "kd": kd, "ki": ki, "kp": kp, "ld": ld, 
        "mo": mo, "mt": mt, "op": op, "pa": pa, "pr": pr, "pv": pv, "sc": sc, 
        "sh": sh, "sp": sp, "st": st, "ta": ta, "tp": tp, "xq": xq
    }

    if command in command_dispatcher:
        command_function = command_dispatcher[command]

        sig = inspect.signature(command_function)
        params = list(sig.parameters)

        kwargs = {"args": args, "context": context}
        dynamic_args = [kwargs[param] for param in params if param in kwargs]

        yield from command_function(*dynamic_args)
    else:
        raise CommandNotFoundError(command)

def ac(args, context):
    acceleration = float(args[0])
    print(f"Setting acceleration to {acceleration}")
    galil = context.devices.galil
    yield from bps.mv(galil.acceleration, acceleration)

def af(args):
    print(f"Executing 'af' (Analog Feedback Select) command with args: {args}")
    yield from bps.null()

def ba(args):
    print(f"Executing 'ba' command with args: {args}")
    yield from bps.null()

def bg(context):
    print(f"Begin movement")
    galil = context.devices.galil
    yield from bps.mv(galil.velocity, context.galil_speed / 1000000)
    yield from bps.checkpoint()
    yield from motor_move(galil, context.galil_pos / 1000000, is_rel=context.galil_abs_rel)

def bi(args):
    print(f"Executing 'bi' command with args: {args}")
    yield from bps.null()

def bl(args):
    print(f"Executing 'bl' (Reverse Software Limit) command with args: {args}")
    yield from bps.null()

def bm(args):
    print(f"Executing 'bm' command with args: {args}")
    yield from bps.null()

def bt(args):
    print(f"Executing 'bt' command with args: {args}")
    yield from bps.null()

def bz(args):
    print(f"Executing 'bz' (Brushless Zero) command with args: {args}")
    yield from bps.null()

def cc(args):
    print(f"Executing 'cc' (Configure Communications) command with args: {args}")
    yield from bps.null()

def ce(args):
    print(f"Executing 'ce' (Configure Encoder) command with args: {args}")
    yield from bps.null()

def cn(args):
    print(f"Executing 'cn' command with args: {args}")
    yield from bps.null()

def dc(args, context):
    deceleration = float(args[0])
    print(f"Setting deceleration to {deceleration}")
    galil = context.devices.galil
    yield from bps.mv(galil.acceleration, deceleration)  

def dp(args, context):
    position = float(args[0])
    print(f"Defining position: {position}")
    galil = context.devices.galil
    galil.set_current_position(position)
    yield from bps.null()

def er(args, context):
    error_limit = float(args[0])
    print(f"Setting error limit to {error_limit}")
    galil = context.devices.galil
    yield from bps.mv(galil.error_limit, error_limit)  # placeholder, depends on the motor configuration

def fa(args):
    print(f"Executing 'fa' (Acceleration Feedforward) command with args: {args}")
    yield from bps.null()

def fe(args):
    print(f"Executing 'fe' (Find Edge) command with args: {args}")
    yield from bps.null()

def fl(args):
    print(f"Executing 'fl' (Forward Software Limit) command with args: {args}")
    yield from bps.null()

def fv(args, context):
    velocity_feedforward = float(args[0])
    print(f"Setting velocity feedforward to {velocity_feedforward}")
    galil = context.devices.galil
    yield from bps.mv(galil.velocity, velocity_feedforward)

def hm(context):
    print("Homing device")
    galil = context.devices.galil
    yield from motor_home(galil)

def hv(args, context):
    homing_velocity = float(args[0])
    print(f"Setting homing velocity to {homing_velocity}")
    galil = context.devices.galil
    yield from bps.mv(galil.homing_velocity, homing_velocity)

def ib(args):
    print(f"Executing 'ib' command with args: {args}")
    yield from bps.null()

def iht(args):
    print(f"Executing 'iht' (Close IP Handle) command with args: {args}")
    yield from bps.null()

def il(args, context):
    integrator_limit = float(args[0])
    print(f"Setting integrator limit to {integrator_limit}")
    galil = context.devices.galil
    yield from bps.mv(galil.integrator_limit, integrator_limit)

def kd(args, context):
    derivative_gain = float(args[0])
    print(f"Setting derivative gain to {derivative_gain}")
    galil = context.devices.galil
    yield from bps.mv(galil.kd, derivative_gain)

def ki(args, context):
    integrator_gain = float(args[0])
    print(f"Setting integrator gain to {integrator_gain}")
    galil = context.devices.galil
    yield from bps.mv(galil.ki, integrator_gain)

def kp(args, context):
    proportional_gain = float(args[0])
    print(f"Setting proportional gain to {proportional_gain}")
    galil = context.devices.galil
    yield from bps.mv(galil.kp, proportional_gain)

def ld(args):
    print(f"Executing 'ld' (Limit Disable) command with args: {args}")
    yield from bps.null()

def mo():
    print(f"Turning motor off")
    galil.stop()  # assume motor off is the same as stop
    yield from bps.null()

def mt(args):
    motor_type = args[0]
    print(f"Setting motor type to {motor_type}")
    yield from bps.null()

def op(args):
    output_port = int(args[0])
    print(f"Setting output port: {output_port}")
    yield from bps.null()

def pa(args, context):
    position = float(args[0])
    print(f"Setting absolute position to {position}")
    context.galil_abs_rel = 0
    context.galil_pos = position
    yield from bps.null()

def pr(args, context):
    position = float(args[0])
    print(f"Setting relative position to {position}")
    context.galil_abs_rel = 1
    context.galil_pos = position
    yield from bps.null()

def pv(args):
    print(f"Executing 'pv' command with args: {args}")
    yield from bps.null()

def sc(context):
    print(f"Executing 'sc' (stop motor) command")
    galil = context.devices.galil
    galil.stop()
    yield from bps.null()

def sh():
    print(f"Executing 'sh' (Servo Here) command")
    yield from bps.null()

def sp(args, context):
    speed = float(args[0])
    context.galil_speed = speed;
    print(f"Setting speed to {speed}")
    yield from bps.null()

def st(context):
    print(f"Stopping motor")
    yield from motor_stop(context.devices.galil)

def ta(args):
    print(f"Executing 'ta' command with args: {args}")
    yield from bps.null()

def tp(context):
    galil = context.devices.galil
    current_position = galil.position
    print(f"Executing 'tp' (tell position), current position: {current_position}")
    yield from bps.null()

def xq(args):
    print(f"Executing 'xq' (execute program) command with args: {args}")
    yield from bps.null()
