import logging
import platform
import re
import stat
from asyncio import iscoroutinefunction
from asyncio.runners import run
from functools import wraps
from pathlib import Path
from subprocess import PIPE, Popen
from tempfile import gettempdir
from typing import Callable, Coroutine, Optional, Sequence, Union
import requests

__all__ = ["Megatools", "MegaError"]

logger = logging.getLogger(Path(__file__).stem)


class MegaError(Exception):
    """Exception for all errors with megatools"""


Stream = list[str]


def to_string(*seq: Sequence) -> tuple[str, ...]:
    return tuple("".join(s) for s in seq)


def parse_options(command: list[str], **options):
    for option, value in options.items():
        option = option.replace("_", "-")
        if value is True:
            command.append(f"--{option}")
            continue
        command.append(f"--{option}={value}")


def execute(command: list[str], on_read: Optional[Callable] = None, *args) -> tuple:
    if on_read:
        assert not iscoroutinefunction(on_read), "`on_read` function must be sync!"
    process = Popen(command, stdout=PIPE, stderr=PIPE)
    streams: list[Stream] = []
    for f in (process.stdout, process.stderr):
        stream = Stream()
        for char in iter(lambda: f.readline(), b""):
            stream.append(char.decode(errors="ignore"))
            if on_read:
                on_read(stream, process, *args)
        streams.append(stream)
    return (*to_string(*streams), process.wait())


async def async_execute(
    command: list[str], on_read: Optional[Callable] = None, *args
) -> tuple:
    if on_read:
        assert iscoroutinefunction(on_read), "`on_read` function must be async!"
    process = Popen(command, stdout=PIPE, stderr=PIPE)
    streams: list[Stream] = []
    for f in (process.stdout, process.stderr):
        stream = Stream()
        for char in iter(lambda: f.readline(), b""):
            stream.append(char.decode(errors="ignore"))
            if on_read:
                await on_read(stream, process, *args)
        streams.append(stream)
    return (*to_string(*streams), process.wait())


def default_callback(stream: Stream, _) -> None:
    print(end=stream[-1])


@wraps(default_callback)
async def default_async_callback(*args, **kwargs) -> None:
    default_callback(*args, **kwargs)


def parse_and_raise(error: str) -> None:
    pattern = re.compile(r"\w+: ")
    match = pattern.search(error)
    if match:
        error = error.replace(match.group(0), "", 1)
    raise MegaError(error)


class Megatools:
    def __init__(self, executable: Union[Path, str] = None) -> None:
        """Setup new instance of Megatools

        Args:
            executable (Union[Path, str], optional): Path to the megatools executable. Downloads executable if this is None (default)
        """
        self.tmp_directory = Path(gettempdir())
        if not executable:
            executable = self.tmp_directory / "megatools"
            if not executable.exists():
                logger.info("Downloading executable..")
                url = "https://raw.githubusercontent.com/justaprudev/megatools/master/megatools"
                binary = requests.get(
                    f"{url}.exe" if platform.system() == "Windows" else url
                )
                with open(executable, "wb") as f:
                    f.write(binary.content)
                executable.chmod(
                    executable.stat().st_mode
                    | stat.S_IXUSR
                    | stat.S_IXGRP
                    | stat.S_IXOTH
                )
        self.executable = str(executable)

    def download(
        self,
        url: str,
        progress: Optional[Callable] = default_callback,
        progress_arguments: tuple = (),
        assume_async: bool = False,
        **options,
    ) -> Union[str, Coroutine]:
        """Download a file from mega.nz

        Args:
            url (str): A valid mega.nz download url
            progress (Callable, optional): A function that accepts the `output stream` and `process` and uses it display progress. Defaults to default_callback
            async (bool, optional): Assume that `progress` is async
            *args: Optional arguments to be passed on to `progress` function

        Switches (ex. no_progress=True):
            no_progress:               Disable progress bar
            print_names:               Print names of downloaded files
            choose_files:              Choose which files to download when downloading folders (interactive)
            disable_resume:            Disable resume when downloading file
            no_ask_password:           Never ask interactively for a password
            reload:                    Reload filesystem cache
            ignore_config_file:        Disable loading mega.ini
            version:                   Show version information

        Options (ex. path='path/to/file'):
            path=PATH:                 Local directory or file name, to save data to.
            u, username=USERNAME:      Account username (email)
            p, password=PASSWORD:      Account password
            limit_speed=SPEED:         Limit transfer speed (KiB/s)
            proxy=PROXY:               Proxy setup string
            netif=NAME:                Network interface or local IP address used for outgoing connections
            ip_proto=PROTO:            Which protocol to prefer when connecting to mega.nz (v4, v6, or any)
            config=PATH:               Load configuration from a file
            debug=OPTS:                Enable debugging output

        Raises:
            MegaError: Any error that occurs while execution

        Returns:
            Union[str, Coroutine]: A coroutine if `progress` is async or `assume_async` is True, otherwise the stdout.
        """
        if assume_async or iscoroutinefunction(progress):
            if progress is default_callback:
                progress = default_async_callback
            return self.async_download(url, progress, *progress_arguments, **options)
        command = [self.executable, "dl", url, "--no-ask-password"]
        parse_options(command, **options)
        logger.info(f"Executing: {command}")
        stdout, stderr, returncode = execute(command, progress, *progress_arguments)
        if stderr:
            parse_and_raise(f"[returnCode {returncode}] {stderr}")
        return stdout

    @wraps(download)
    async def async_download(
        self,
        url: str,
        progress: Optional[Callable] = default_callback,
        progress_arguments: tuple = (),
        **options,
    ) -> str:
        command = [self.executable, "dl", url, "--no-ask-password"]
        parse_options(command, **options)
        logger.info(f"Executing: {command}")
        stdout, stderr, returncode = await async_execute(
            command, progress, *progress_arguments
        )
        if stderr:
            parse_and_raise(f"[returnCode {returncode}] {stderr}")
        return stdout

    @property
    def version(self) -> str:
        """Get version information of megatools

        Returns:
            str: Megatools version number as a string. (Ex 1.11.0)
        """
        return self.download("", progress=None, version=True).split()[1]

    def filename(self, url: str) -> str:
        """Get the name of a file from a valid mega.nz url

        Args:
            url (str): A valid mega.nz url

        Returns:
            str: The name of the file
        """
        return self.download(
            url,
            progress=lambda stream, process: stream[-1] and process.terminate(),
            print_names=True,
            limit_speed=1,
            path=str(self.tmp_directory),
        ).split(":")[0]
