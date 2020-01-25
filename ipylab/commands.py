# Copyright (c) Jeremy Tuloup.
# Distributed under the terms of the Modified BSD License.

from collections import defaultdict

from ipywidgets import CallbackDispatcher, Widget
from traitlets import List, Unicode

from ._frontend import module_name, module_version


class CommandRegistry(Widget):
    _model_name = Unicode("CommandRegistryModel").tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)

    _commands = List(Unicode, read_only=True).tag(sync=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._execute_callbacks = defaultdict(CallbackDispatcher)
        self.on_msg(self._on_frontend_msg)

    def _on_frontend_msg(self, _, content, buffers):
        if content.get("event", "") == "execute":
            command_id = content.get("id")
            self._execute_callbacks[command_id]()

    def execute(self, command_id, args=None):
        args = args or {}
        self.send({"func": "execute", "payload": {"id": command_id, "args": args}})

    def list_commands(self):
        return self._commands

    def add_command(self, command_id, execute, *, caption="", label="", icon_class=""):
        if command_id in self._execute_callbacks or command_id in self._commands:
            raise Exception(f"Command {command_id} is already registered")
        # TODO: support other parameters (isEnabled, isVisible...)
        self._execute_callbacks[command_id].register_callback(execute, False)
        self.send(
            {
                "func": "addCommand",
                "payload": {
                    "id": command_id,
                    "caption": caption,
                    "label": label,
                    "iconClass": icon_class,
                },
            }
        )
