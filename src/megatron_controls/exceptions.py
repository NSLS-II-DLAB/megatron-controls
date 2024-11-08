class MegatronError(Exception):
    """Base class for all Megatron-related errors."""
    pass

class CommandNotFoundError(MegatronError):
    """Raised when a command is not recognized."""
    def __init__(self, command):
        self.command = command
        super().__init__(f"Error: Unrecognized command '{command}'")

class InvalidArgumentError(MegatronError):
    """Raised when a command receives invalid arguments."""
    def __init__(self, command, args):
        self.command = command
        self.args = args
        super().__init__(f"Error: Invalid arguments '{args}' for command '{command}'")

class LoopSyntaxError(MegatronError):
    """Raised when a loop is not properly closed."""
    def __init__(self):
        super().__init__("Error: 'l' loop without matching 'n'")

class InvalidScriptPathError(Exception):
    """Raised when the script path is invalid or the script cannot be read."""
    def __init__(self, path):
        self.path = path
        super().__init__(f"Error: Script path '{path}' is invalid or unreadable")

class StopScript(Exception):
    """Exception to signal the interpreter to stop the current script."""
    pass
