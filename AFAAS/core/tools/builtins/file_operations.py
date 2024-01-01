"""Tools to perform operations on files"""

from __future__ import annotations

import contextlib
import hashlib
import os
import os.path
from pathlib import Path
from typing import Generator, Literal

from langchain_community.tools.file_management.file_search import FileSearchTool
from langchain_core.vectorstores import VectorStore

TOOL_CATEGORY = "file_operations"
TOOL_CATEGORY_TITLE = "File Operations"

from AFAAS.core.tools.tool_decorator import tool
from AFAAS.core.tools.tools import Tool
from AFAAS.interfaces.agent.main import BaseAgent
from AFAAS.lib.sdk.errors import DuplicateOperationError
from AFAAS.lib.sdk.logger import AFAASLogger
from AFAAS.lib.task.task import Task
from AFAAS.lib.utils.json_schema import JSONSchema

from .decorators import sanitize_path_arg
from .file_operations_utils import decode_textual_file #FIXME: replace with Langchain
COMMAND_CATEGORY = "file_operations"
COMMAND_CATEGORY_TITLE = "File Operations"

LOG = AFAASLogger(name=__name__)

Operation = Literal["write", "append", "delete"]


def text_checksum(text: str) -> str:
    """Get the hex checksum for the given text."""
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def operations_from_log(
    log_path: str | Path,
) -> Iterator[
    tuple[Literal["write", "append"], str, str] | tuple[Literal["delete"], str, None]
]:
    """Parse the file operations log and return a tuple containing the log entries"""
    try:
        log = open(log_path, "r", encoding="utf-8")
    except FileNotFoundError:
        return

    for line in log:
        line = line.replace("File Operation Logger", "").strip()
        if not line:
            continue
        operation, tail = line.split(": ", maxsplit=1)
        operation = operation.strip()
        if operation in ("write", "append"):
            try:
                path, checksum = (x.strip() for x in tail.rsplit(" #", maxsplit=1))
            except ValueError:
                LOG.warn(f"File log entry lacks checksum: '{line}'")
                path, checksum = tail.strip(), None
            yield (operation, path, checksum)
        elif operation == "delete":
            yield (operation, tail.strip(), None)

    log.close()


def file_operations_state(log_path: str | Path) -> dict[str, str]:
    """Iterates over the operations log and returns the expected state.

    Parses a log file at file_manager.file_ops_log_path to construct a dictionary
    that maps each file path written or appended to its checksum. Deleted files are
    removed from the dictionary.

    Returns:
        A dictionary mapping file paths to their checksums.

    Raises:
        FileNotFoundError: If file_manager.file_ops_log_path is not found.
        ValueError: If the log file content is not in the expected format.
    """
    state = {}
    for operation, path, checksum in operations_from_log(log_path):
        if operation in ("write", "append"):
            state[path] = checksum
        elif operation == "delete":
            del state[path]
    return state


@sanitize_path_arg("file_path", make_relative=True)
def is_duplicate_operation(
    operation: Operation, file_path: Path, agent: BaseAgent, checksum: str | None = None
) -> bool:
    """Check if the operation has already been performed

    Args:
        operation: The operation to check for
        file_path: The name of the file to check for
        agent: The agent
        checksum: The checksum of the contents to be written

    Returns:
        True if the operation has already been performed on the file
    """
    state = file_operations_state(agent._setting.Config.file_logger_path)
    if operation == "delete" and file_path not in state:
        return True
    if operation == "write" and state.get(str(file_path)) == checksum:
        return True
    return False


@sanitize_path_arg("file_path", make_relative=True)
def log_operation(
    operation: Operation,
    file_path: str | Path,
    agent: BaseAgent,
    checksum: str | None = None,
) -> None:
    """Log the file operation to the file_LOG.log

    Args:
        operation: The operation to log
        file_path: The name of the file the operation was performed on
        checksum: The checksum of the contents to be written
    """
    log_entry = f"{operation}: {file_path}"
    if checksum is not None:
        log_entry += f" #{checksum}"
    LOG.trace(f"Logging file operation: {log_entry}")
    append_to_file(
        agent._setting.Config.file_logger_path,
        f"{log_entry}\n",
        agent,
        should_log=False,
    )


@tool(
    "read_file",
    "Read an existing file",
    {
        "filename": JSONSchema(
            type=JSONSchema.Type.STRING,
            description="The path of the file to read",
            required=True,
        )
    },
)
def read_file(filename:  str | Path, task: Task, agent: BaseAgent) -> str:
    """Read a file and return the contents

    Args:
        filename (Path): The name of the file to read

    Returns:
        str: The contents of the file
    """
    file = agent.workspace.open_file(filename, binary=True)
    content = decode_textual_file(file, os.path.splitext(filename)[1])

    # TODO: invalidate/update memory when file is edited
    # file_memory = MemoryItem.from_text_file(content, str(filename), agent.config)
    # if len(file_memory.chunks) > 1:
    #     return file_memory.summary

    #cf : ingest_file
    agent.vectorstore.adelete(id=str(filename))
    agent.vectorstore.aadd_texts(texts=[content],
                                #  ids=[str(filename)],
                                #  lang="en",
                                #  title=str(filename),
                                #  description="",
                                #  tags=[],
                                #  metadata={},
                                #  source="",
                                #  author="",
                                #  date="",
                                #  license="",
                                #  url="",
                                #  chunk_size=100,
                                #  chunk_overlap=0,
                                #  chunking_strategy="fixed",
                                #  chunking_strategy_args={},
                                #  chunking_strategy_kwargs={},
    )

    return content


def ingest_file(
    filename: str,
    vectorstore: VectorStore,
) -> None:
    """
    Ingest a file by reading its content, splitting it into chunks with a specified
    maximum length and overlap, and adding the chunks to the memory storage.

    Args:
        filename: The name of the file to ingest
        memory: An object with an add() method to store the chunks in memory
    """
    try:
        LOG.info(f"Ingesting file {filename}")
        content = read_file(filename)

        # TODO: Move to langchain
        raise ("Not implemented error")

        file_memory = MemoryItemFactory.from_text_file(content, filename)
        LOG.trace(f"Created memory: {file_memory.dump(True)}")
        vectorstore.add(file_memory)

        LOG.info(f"Ingested {len(file_memory.e_chunks)} chunks from {filename}")
    except Exception as err:
        LOG.warn(f"Error while ingesting file '{filename}': {err}")


@tool(
    "write_file",
    "Write a file, creating it if necessary. If the file exists, it is overwritten.",
    {
        "filename": JSONSchema(
            type=JSONSchema.Type.STRING,
            description="The name of the file to write to",
            required=True,
        ),
        "contents": JSONSchema(
            type=JSONSchema.Type.STRING,
            description="The contents to write to the file",
            required=True,
        ),
    },
    aliases=["write_file", "create_file"],
)
async def write_to_file(
    filename: Path, contents: str, task: Task, agent: BaseAgent
) -> str:
    """Write contents to a file

    Args:
        filename (Path): The name of the file to write to
        contents (str): The contents to write to the file

    Returns:
        str: A message indicating success or failure
    """
    checksum = text_checksum(contents)
    if is_duplicate_operation("write", Path(filename), agent, checksum):
        raise DuplicateOperationError(f"File {filename} has already been updated.")

    if directory := os.path.dirname(filename):
        agent.workspace.get_path(directory).mkdir(exist_ok=True)
    await agent.workspace.write_file(filename, contents)
    log_operation("write", filename, agent, checksum)
    return f"File {filename} has been written successfully."


def append_to_file(
    filename: Path, text: str, agent: BaseAgent, should_log: bool = True
) -> None:
    """Append text to a file

    Args:
        filename (Path): The name of the file to append to
        text (str): The text to append to the file
        should_log (bool): Should log output
    """
    directory = os.path.dirname(filename)
    os.makedirs(directory, exist_ok=True)
    with open(filename, "a") as f:
        f.write(text)

    if should_log:
        with open(filename, "r") as f:
            checksum = text_checksum(f.read())
        log_operation("append", filename, agent, checksum=checksum)


@tool(
    "list_folder",
    "List the items in a folder",
    {
        "folder": JSONSchema(
            type=JSONSchema.Type.STRING,
            description="The folder to list files in",
            required=True,
        )
    },
)
def list_folder(folder: Path, task: Task, agent: BaseAgent) -> list[str]:
    """Lists files in a folder recursively

    Args:
        folder (Path): The folder to search in

    Returns:
        list[str]: A list of files found in the folder
    """
    return [str(p) for p in agent.workspace.list(folder)]


def file_search_args(input_args: dict[str, any], agent: BaseAgent):
    # Force only searching in the workspace root
    input_args["dir_path"] = str(agent.workspace.get_path(input_args["dir_path"]))

    return input_args


file_search = Tool.generate_from_langchain_tool(
    tool=FileSearchTool(), arg_converter=file_search_args
)
