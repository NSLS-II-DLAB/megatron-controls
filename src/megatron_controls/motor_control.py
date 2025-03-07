import inspect

import bluesky.plan_stubs as bps

from .exceptions import CommandNotFoundError
from .support import motor_home, motor_move, motor_stop

class MotorControl:
    def __init__(self, context):
        self._context = context

    def __call__(self, command, args):
        command_dispatcher = {
            "ac": self.ac,
            "af": self.af,
            "ba": self.ba,
            "bg": self.bg,
            "bi": self.bi,
            "bl": self.bl,
            "bm": self.bm,
            "bt": self.bt,
            "bz": self.bz,
            "cc": self.cc,
            "ce": self.ce,
            "cn": self.cn,
            "dc": self.dc,
            "dp": self.dp,
            "er": self.er,
            "fa": self.fa,
            "fe": self.fe,
            "fl": self.fl,
            "fv": self.fv,
            "hm": self.hm,
            "hv": self.hv,
            "ib": self.ib,
            "iht": self.iht,
            "il": self.il,
            "kd": self.kd,
            "ki": self.ki,
            "kp": self.kp,
            "ld": self.ld,
            "mo": self.mo,
            "mt": self.mt,
            "op": self.op,
            "pa": self.pa,
            "pr": self.pr,
            "pv": self.pv,
            "sc": self.sc,
            "sh": self.sh,
            "sp": self.sp,
            "st": self.st,
            "ta": self.ta,
            "tp": self.tp,
            "xq": self.xq,
        }

        if command in command_dispatcher:
            command_function = command_dispatcher[command]

            sig = inspect.signature(command_function)
            params = list(sig.parameters)

            kwargs = {"args": args}
            dynamic_args = [kwargs[param] for param in params if param in kwargs]

            yield from command_function(*dynamic_args)
        else:
            raise CommandNotFoundError(command)


    def ac(self, args):
        acceleration = float(args[0])
        print(f"Setting acceleration to {acceleration}")
        galil = self._context.devices.galil
        yield from bps.mv(galil.acceleration, acceleration)


    def af(self, args):
        print(f"Executing 'af' (Analog Feedback Select) command with args: {args}")
        yield from bps.null()


    def ba(self, args):
        print(f"Executing 'ba' command with args: {args}")
        yield from bps.null()


    def bg(self):
        print("Begin movement")
        galil = self._context.devices.galil
        yield from bps.mv(galil.velocity, self._context.galil_speed / 1000000)
        yield from bps.checkpoint()
        yield from motor_move(galil, self._context.galil_pos / 1000000, is_rel=self._context.galil_abs_rel)


    def bi(self, args):
        print(f"Executing 'bi' command with args: {args}")
        yield from bps.null()


    def bl(self, args):
        print(f"Executing 'bl' (Reverse Software Limit) command with args: {args}")
        yield from bps.null()


    def bm(self, args):
        print(f"Executing 'bm' command with args: {args}")
        yield from bps.null()


    def bt(self, args):
        print(f"Executing 'bt' command with args: {args}")
        yield from bps.null()


    def bz(self, args):
        print(f"Executing 'bz' (Brushless Zero) command with args: {args}")
        yield from bps.null()


    def cc(self, args):
        print(f"Executing 'cc' (Configure Communications) command with args: {args}")
        yield from bps.null()


    def ce(self, args):
        print(f"Executing 'ce' (Configure Encoder) command with args: {args}")
        yield from bps.null()


    def cn(self, args):
        print(f"Executing 'cn' command with args: {args}")
        yield from bps.null()


    def dc(self, args):
        deceleration = float(args[0])
        print(f"Setting deceleration to {deceleration}")
        galil = self._context.devices.galil
        yield from bps.mv(galil.acceleration, deceleration)


    def dp(self, args):
        position = float(args[0])
        print(f"Defining position: {position}")
        galil = self._context.devices.galil
        galil.set_current_position(position)
        yield from bps.null()


    def er(self, args):
        error_limit = float(args[0])
        print(f"Setting error limit to {error_limit}")
        galil = self_context.devices.galil
        yield from bps.mv(galil.error_limit, error_limit)  # placeholder, depends on the motor configuration


    def fa(self, args):
        print(f"Executing 'fa' (Acceleration Feedforward) command with args: {args}")
        yield from bps.null()


    def fe(self, args):
        print(f"Executing 'fe' (Find Edge) command with args: {args}")
        yield from bps.null()


    def fl(self, args):
        print(f"Executing 'fl' (Forward Software Limit) command with args: {args}")
        yield from bps.null()


    def fv(self, args):
        velocity_feedforward = float(args[0])
        print(f"Setting velocity feedforward to {velocity_feedforward}")
        galil = self._context.devices.galil
        yield from bps.mv(galil.velocity, velocity_feedforward)


    def hm(self):
        print("Homing device")
        galil = self._context.devices.galil
        yield from motor_home(galil)


    def hv(self, args):
        homing_velocity = float(args[0])
        print(f"Setting homing velocity to {homing_velocity}")
        galil = self._context.devices.galil
        yield from bps.mv(galil.homing_velocity, homing_velocity)


    def ib(self, args):
        print(f"Executing 'ib' command with args: {args}")
        yield from bps.null()


    def iht(self, args):
        print(f"Executing 'iht' (Close IP Handle) command with args: {args}")
        yield from bps.null()


    def il(self, args):
        integrator_limit = float(args[0])
        print(f"Setting integrator limit to {integrator_limit}")
        galil = self._context.devices.galil
        yield from bps.mv(galil.integrator_limit, integrator_limit)


    def kd(self, args):
        derivative_gain = float(args[0])
        print(f"Setting derivative gain to {derivative_gain}")
        galil = self._context.devices.galil
        yield from bps.mv(galil.kd, derivative_gain)


    def ki(self, args):
        integrator_gain = float(args[0])
        print(f"Setting integrator gain to {integrator_gain}")
        galil = self._context.devices.galil
        yield from bps.mv(galil.ki, integrator_gain)


    def kp(self, args, context):
        proportional_gain = float(args[0])
        print(f"Setting proportional gain to {proportional_gain}")
        galil = self._context.devices.galil
        yield from bps.mv(galil.kp, proportional_gain)


    def ld(self, args):
        print(f"Executing 'ld' (Limit Disable) command with args: {args}")
        yield from bps.null()


    def mo(self):
        print("Turning motor off")
        # galil.stop()  # assume motor off is the same as stop
        yield from bps.null()


    def mt(self, args):
        motor_type = args[0]
        print(f"Setting motor type to {motor_type}")
        yield from bps.null()


    def op(self, args):
        output_port = int(args[0])
        print(f"Setting output port: {output_port}")
        yield from bps.null()


    def pa(self, args):
        position = float(args[0])
        print(f"Setting absolute position to {position}")
        self._context.galil_abs_rel = 0
        self._context.galil_pos = position
        yield from bps.null()


    def pr(self, args):
        position = float(args[0])
        print(f"Setting relative position to {position}")
        self._context.galil_abs_rel = 1
        self._context.galil_pos = position
        yield from bps.null()


    def pv(self, args):
        print(f"Executing 'pv' command with args: {args}")
        yield from bps.null()


    def sc(self):
        print("Executing 'sc' (stop motor) command")
        galil = self._context.devices.galil
        galil.stop()
        yield from bps.null()


    def sh(self):
        print("Executing 'sh' (Servo Here) command")
        yield from bps.null()


    def sp(self, args):
        speed = float(args[0])
        self._context.galil_speed = speed
        print(f"Setting speed to {speed}")
        yield from bps.null()


    def st(self):
        print("Stopping motor")
        yield from motor_stop(self._context.devices.galil)


    def ta(self, args):
        print(f"Executing 'ta' command with args: {args}")
        yield from bps.null()


    def tp(self):
        galil = self._context.devices.galil
        current_position = galil.position
        print(f"Executing 'tp' (tell position), current position: {current_position}")
        yield from bps.null()


    def xq(self, args):
        print(f"Executing 'xq' (execute program) command with args: {args}")
        yield from bps.null()
