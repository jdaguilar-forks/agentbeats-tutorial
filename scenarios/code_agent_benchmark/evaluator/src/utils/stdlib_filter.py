"""Define Python standard library modules for filtering BigCodeBench tasks."""

# Python 3.11+ standard library modules
# Source: https://docs.python.org/3/library/
PYTHON_STDLIB = {
    # Built-in functions (always available)
    "__future__",
    "__main__",
    "_thread",
    # Text Processing
    "string",
    "re",
    "difflib",
    "textwrap",
    "unicodedata",
    "stringprep",
    "readline",
    "rlcompleter",
    # Binary Data
    "struct",
    "codecs",
    # Data Types
    "datetime",
    "zoneinfo",
    "calendar",
    "collections",
    "heapq",
    "bisect",
    "array",
    "weakref",
    "types",
    "copy",
    "pprint",
    "reprlib",
    "enum",
    "graphlib",
    # Numeric and Mathematical
    "numbers",
    "math",
    "cmath",
    "decimal",
    "fractions",
    "random",
    "statistics",
    # Functional Programming
    "itertools",
    "functools",
    "operator",
    # File and Directory Access
    "pathlib",
    "os.path",
    "fileinput",
    "stat",
    "filecmp",
    "tempfile",
    "glob",
    "fnmatch",
    "linecache",
    "shutil",
    # Data Persistence
    "pickle",
    "copyreg",
    "shelve",
    "marshal",
    "dbm",
    "sqlite3",
    # Data Compression and Archiving
    "zlib",
    "gzip",
    "bz2",
    "lzma",
    "zipfile",
    "tarfile",
    # File Formats
    "csv",
    "configparser",
    "tomllib",
    "netrc",
    "plistlib",
    # Cryptographic Services
    "hashlib",
    "hmac",
    "secrets",
    # Generic Operating System Services
    "os",
    "io",
    "time",
    "argparse",
    "getopt",
    "logging",
    "getpass",
    "curses",
    "platform",
    "errno",
    "ctypes",
    # Concurrent Execution
    "threading",
    "multiprocessing",
    "concurrent",
    "subprocess",
    "sched",
    "queue",
    # Networking and Interprocess Communication
    "asyncio",
    "socket",
    "ssl",
    "select",
    "selectors",
    "signal",
    "mmap",
    # Internet Data Handling
    "email",
    "json",
    "mailbox",
    "mimetypes",
    "base64",
    "binascii",
    "quopri",
    # Structured Markup Processing Tools
    "html",
    "xml",
    # Internet Protocols and Support
    "webbrowser",
    "urllib",
    "http",
    "ftplib",
    "poplib",
    "imaplib",
    "smtplib",
    "uuid",
    "socketserver",
    "xmlrpc",
    # Multimedia Services
    "wave",
    "colorsys",
    # Internationalization
    "gettext",
    "locale",
    # Program Frameworks
    "turtle",
    "cmd",
    "shlex",
    # Graphical User Interfaces
    "tkinter",
    # Development Tools
    "typing",
    "pydoc",
    "doctest",
    "unittest",
    "test",
    "trace",
    "tracemalloc",
    # Debugging and Profiling
    "bdb",
    "faulthandler",
    "pdb",
    "timeit",
    "cProfile",
    "profile",
    "pstats",
    # Software Packaging and Distribution
    "distutils",
    "ensurepip",
    "venv",
    "zipapp",
    # Python Runtime Services
    "sys",
    "sysconfig",
    "builtins",
    "warnings",
    "dataclasses",
    "contextlib",
    "abc",
    "atexit",
    "traceback",
    "__future__",
    "gc",
    "inspect",
    "site",
    # Custom Python Interpreters
    "code",
    "codeop",
    # Importing Modules
    "zipimport",
    "pkgutil",
    "modulefinder",
    "runpy",
    "importlib",
    # Python Language Services
    "ast",
    "symtable",
    "token",
    "keyword",
    "tokenize",
    "tabnanny",
    "pyclbr",
    "py_compile",
    "compileall",
    "dis",
    "pickletools",
    # MS Windows Specific
    "msilib",
    "msvcrt",
    "winreg",
    "winsound",
    # Unix Specific
    "posix",
    "pwd",
    "grp",
    "termios",
    "tty",
    "pty",
    "fcntl",
    "resource",
    "syslog",
    # Superseded Modules
    "aifc",
    "audioop",
    "cgi",
    "cgitb",
    "chunk",
    "crypt",
    "imghdr",
    "mailcap",
    "nis",
    "nntplib",
    "optparse",
    "ossaudiodev",
    "pipes",
    "smtpd",
    "sndhdr",
    "spwd",
    "sunau",
    "telnetlib",
    "uu",
    "xdrlib",
}


def is_stdlib_only(required_libs: list) -> bool:
    """
    Check if all required libraries are from Python standard library.

    Args:
        required_libs: List of library names

    Returns:
        True if all libraries are stdlib, False otherwise
    """
    return all(lib in PYTHON_STDLIB for lib in required_libs)


def filter_stdlib_tasks(tasks: list) -> list:
    """
    Filter tasks to only include those using standard library.

    Args:
        tasks: List of task dictionaries

    Returns:
        Filtered list of stdlib-only tasks
    """
    return [task for task in tasks if is_stdlib_only(task.get("required_libs", []))]
