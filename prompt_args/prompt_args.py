import functools
import inspect
from dataclasses import MISSING
from typing import Any, Callable, Optional


class Prompt:
    converters = {}

    no_prompt = None

    @classmethod
    def register_type_converter(cls, type_annotation, converter, prompt_help=None):
        cls.converters[type_annotation] = (converter, prompt_help)

    def __init__(
        self,
        prompt: Optional[str] = MISSING,
        default: Any = MISSING,
        converter: Any = MISSING,
        required: bool = MISSING,
        prompt_help: Optional[str] = MISSING,
        name: str = "",
    ):
        self.name = name
        self.prompt = prompt
        self.default = default
        self.converter = converter

        if required == MISSING:
            required = default == MISSING
        self.required = required
        self.prompt_help = prompt_help

    def get_prompt(self):
        prompt_helper = ""
        if self.prompt_help != MISSING:
            prompt_helper = f" [{self.prompt_help}]"
        elif self.default != MISSING:
            prompt_helper = f" [{self.default!r}]"

        if isinstance(self.prompt, str):
            prompt = self.prompt
            if prompt_helper:
                for end in [":", "?"]:
                    if prompt.rstrip().endswith(end):
                        # Insert the prompt helper
                        col_idx = prompt.rindex(end)
                        prompt = prompt[:col_idx] + prompt_helper + prompt[col_idx:]

            return prompt

        name = self.name.replace("_", " ").title()
        return f"Enter {name}{prompt_helper}: "

    @classmethod
    def decorate(cls, _func: Callable = None, **prompts):
        if _func is None:

            def decorator(_func):
                return cls.decorate(_func=_func, **prompts)

            return decorator

        # Get the function signature
        sig = inspect.signature(_func)
        params = sig.parameters
        param_names = list(params)

        # Create prompts for all known arguments
        accepts_any_keyword = False
        for name, param in params.items():
            # Check *args and **kwargs
            if param.kind in [param.VAR_POSITIONAL, param.VAR_KEYWORD]:
                if param.kind == param.VAR_KEYWORD:
                    accepts_any_keyword = True
                # Skip *args and **kwargs if no prompt given
                if name not in prompts:
                    continue

            # Parse possible Prompt values
            required = param.default == param.empty
            default = param.default if not required else MISSING
            converter = MISSING
            prompt_help = MISSING
            if callable(param.annotation) and not hasattr(param.annotation, "__args__"):
                converter = param.annotation
                if converter in cls.converters:
                    converter, prompt_help = cls.converters[converter]

            # Get or create new Prompt
            try:
                prompt = prompts[name]
                if prompt is None:
                    continue
            except KeyError:
                prompt = prompts[name] = cls()

            # Set Prompt attributes based on annotation and defaults
            prompt.name = name
            if prompt.default == MISSING:
                prompt.default = default
            if prompt.converter == MISSING:
                prompt.converter = converter
            if prompt.required == MISSING:
                prompt.required = required
            if prompt.prompt_help == MISSING:
                prompt.prompt_help = prompt_help

        # Check for problems with the given prompts and the defined function
        if not accepts_any_keyword:
            for name in prompts:
                if name not in param_names:
                    raise ValueError(f"Detected Prompt {name!r} with no corresponding function argument!")

        # Create the function wrapper using the prompts
        @functools.wraps(_func)
        def wrapper(*args, **kwargs):
            # Convert all args to key word arguments
            for i in range(len(args)):
                kwargs[str(param_names[i])] = args[i]

            # Get input for all arguments not given
            for name, prompt in prompts.items():
                if name not in kwargs and prompt:
                    value = input(prompt.get_prompt()).strip()
                    if callable(prompt.converter):
                        value = prompt.converter(value)
                    value = value or prompt.default
                    if prompt.required and value == MISSING:
                        raise ValueError(f"Invalid value {value!r} for {name}")
                    kwargs[name] = value

            return _func(**kwargs)

        return wrapper


def is_yes(value):
    try:
        v = str(value)[0].lower()
        return v == "y"
    except IndexError:
        return False


Prompt.register_type_converter(bool, is_yes, prompt_help="Y/n")
