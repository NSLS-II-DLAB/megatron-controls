import os
import re

from bluesky import plan_stubs as bps

from .exceptions import CommandNotFoundError, LoopSyntaxError, StopScript
from .megatron_control import process_megatron_command
from .motor_control import process_motor_command


class MegatronInterpreter:
    def __init__(self, *, shared_context):
        self.context = shared_context
        self.context.run_script_callback = self.execute_script  # Set the callback for running sub-scripts
        self._process_supported_devices()

        self.megatron_commands = [
            "email",
            "exit",
            "failif",
            "failifoff",
            "l",
            "log",
            "lograte",
            "plot",
            "print",
            "run",
            "set",
            "setao",
            "setdo",
            "stop",
            "t",
            "var",
            "waitai",
            "waitdi",
        ]
        self.motor_commands = [
            "ac",
            "af",
            "ba",
            "bg",
            "bi",
            "bl",
            "bm",
            "bt",
            "bz",
            "cc",
            "ce",
            "cn",
            "dc",
            "dp",
            "er",
            "fa",
            "fe",
            "fl",
            "fv",
            "hm",
            "hv",
            "ib",
            "iht",
            "il",
            "kd",
            "ki",
            "kp",
            "ld",
            "mo",
            "mt",
            "op",
            "pa",
            "pr",
            "pv",
            "sc",
            "sh",
            "sp",
            "st",
            "ta",
            "tp",
            "xq",
        ]

    def _process_supported_devices(self):
        for desc, nm in self.context.device_mapping.items():
            parts = nm.split(".")
            obj = self.context.devices
            for part in parts:
                obj = getattr(obj, part)
            self.context._name_to_device[desc] = obj

    def execute_script(self, script_path):
        with open(script_path) as script_file:
            script_lines = script_file.readlines()

        def plan():
            i = 0
            while i < len(script_lines):
                line = script_lines[i].strip()
                if line.startswith("#"):  # Ignore comments
                    i += 1
                    continue

                if not line:
                    yield from bps.null()
                    i += 1
                    continue

                match_t = re.match(r"t([\d.]+)", line, re.IGNORECASE)
                match_l = re.match(r"l(\d+)", line, re.IGNORECASE)

                try:
                    if match_t:
                        timer_value = match_t.group(1)
                        yield from self.handle_timer(timer_value)
                    elif match_l:
                        loop_count = int(match_l.group(1))
                        loop_end = self.find_end_of_loop(script_lines, i)
                        if loop_end == -1:
                            raise LoopSyntaxError()
                        loop_block = script_lines[i + 1 : loop_end]
                        yield from self.handle_loop(loop_count, loop_block)
                        i = loop_end
                    else:
                        command, *args = self.tokenize_command(line)
                        if command in self.megatron_commands:
                            yield from process_megatron_command(command, args, self.context)
                        elif command in self.motor_commands:
                            yield from process_motor_command(command, args, self.context)
                        else:
                            raise CommandNotFoundError(command)
                except StopScript:
                    break
                except (CommandNotFoundError, LoopSyntaxError) as e:
                    print(e)
                    yield from bps.null()
                i += 1

                if self.context.fail_condition_triggered:
                    self.context.fail_condition_triggered = False
                    fail_script_path = self.context.fail_script_path
                    yield from self.execute_script(fail_script_path)
                    return

        yield from plan()

    def tokenize_command(self, line):
        regex = r'(?:(?:"([^"]+)")|([^\s,]+))'
        tokens = re.findall(regex, line)
        return [t[0] or t[1] for t in tokens if t[0] or t[1]]

    def handle_timer(self, timer_value):
        print(f"Processing timer for {timer_value} seconds")
        yield from process_megatron_command("t", [timer_value], self.context)

    def handle_loop(self, loop_count, block):
        for _ in range(loop_count):
            print(f"Executing loop iteration {_ + 1} of {loop_count}")
            yield from self.execute_block(block)

    def find_end_of_loop(self, lines, start_index):
        loop_depth = 0
        for i in range(start_index + 1, len(lines)):
            line = lines[i].strip().lower()
            if line.startswith("l"):
                loop_depth += 1
            elif line == "n":
                if loop_depth == 0:
                    return i
                else:
                    loop_depth -= 1
        return -1

    def execute_block(self, block):
        i = 0
        while i < len(block):
            line = block[i].strip()
            if not line:
                yield from bps.null()
                i += 1
                continue

            match_t = re.match(r"t([\d.]+)", line, re.IGNORECASE)
            match_l = re.match(r"l(\d+)", line, re.IGNORECASE)

            if match_t:
                timer_value = match_t.group(1)
                yield from self.handle_timer(timer_value)
                i += 1
                continue

            elif match_l:
                loop_count = int(match_l.group(1))
                loop_end = self.find_end_of_loop(block, i)

                if loop_end == -1:
                    raise LoopSyntaxError()

                nested_block = block[i + 1 : loop_end]
                yield from self.handle_loop(loop_count, nested_block)
                i = loop_end + 1
                continue

            command, *args = self.tokenize_command(line)

            if command in self.megatron_commands:
                yield from process_megatron_command(command, args, self.context)
            elif command in self.motor_commands:
                yield from process_motor_command(command, args, self.context)

            i += 1

            if self.context.fail_condition_triggered:
                self.context.fail_condition_triggered = False
                fail_script_path = self.context.fail_script_path
                yield from self.execute_script(fail_script_path)
                return

    def scan_script_for_logs(self, script_path, scanned_scripts=None):
        if scanned_scripts is None:
            scanned_scripts = set()
        if script_path in scanned_scripts:
            return set()  # Avoid infinite recursion

        scanned_scripts.add(script_path)

        with open(script_path) as script_file:
            script_lines = script_file.readlines()

        logged_pvs = set()
        for line in script_lines:
            line = line.strip()
            if line.startswith("#") or not line:
                continue

            tokens = self.tokenize_command(line)
            if not tokens:
                continue
            command = tokens[0].lower()
            args = tokens[1:]
            if command == "log" and args:
                pv_name = args[0].strip('"')
                logged_pvs.add(pv_name)
            elif command == "run" and args:
                sub_script_name = args[0].strip('"')
                sub_script_path = os.path.join(self.context.script_dir, sub_script_name)
                logged_pvs.update(self.scan_script_for_logs(sub_script_path, scanned_scripts))

        return logged_pvs
