import io
import re
from contextlib import redirect_stdout
from pathlib import Path

from packaging.utils import parse_wheel_filename
from wheel.cli.pack import pack as pack_wheel
from wheel.cli.unpack import unpack as unpack_wheel

# Copied from auditwheel
WHEEL_INFO_RE = re.compile(
    r"""^(?P<namever>(?P<name>.+?)-(?P<ver>\d.*?))(-(?P<build>\d.*?))?
     -(?P<pyver>[a-z].+?)-(?P<abi>.+?)-(?P<plat>.+?)(\.whl|\.dist-info)$""",
    re.VERBOSE,
)


def is_emscripten_wheel(filename: str) -> bool:
    _, _, _, tags = parse_wheel_filename(filename)
    tag = list(tags)[0]
    platform = tag.platform
    return platform.startswith("emscripten")


def parse_wheel_extract_dir(wheel_file: str | Path) -> str:
    """Parse the wheel file name and return the directory name where the wheel
    will be extracted.
    """
    wheel_file = Path(wheel_file)
    m = WHEEL_INFO_RE.match(wheel_file.name)
    if m is None:
        raise ValueError(f"Invalid wheel file name: {wheel_file.name}")

    return m.group("namever")


def unpack(path: str, dest: str = ".") -> Path:
    """Unpack a wheel.
    Wheel content will be unpacked to {dest}/{name}-{ver}, where {name}
    is the package name and {ver} its version.
    :param path: The path to the wheel.
    :param dest: Destination directory (default to current directory).
    """
    with io.StringIO() as buf, redirect_stdout(buf):
        unpack_wheel(path, dest)

    return Path(dest) / parse_wheel_extract_dir(path)


def pack(directory: str, dest_dir: str, build_number: str | None) -> None:
    """Repack a previously unpacked wheel directory into a new wheel file.
    The .dist-info/WHEEL file must contain one or more tags so that the target
    wheel file name can be determined.
    :param directory: The unpacked wheel directory
    :param dest_dir: Destination directory (defaults to the current directory)
    """
    with io.StringIO() as buf, redirect_stdout(buf):
        pack_wheel(directory, dest_dir, build_number)
