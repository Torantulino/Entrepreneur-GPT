from typing_extensions import Optional
from todoist_api_python.api import TodoistAPI

from backend.blocks.todoist._auth import (
    TEST_CREDENTIALS,
    TEST_CREDENTIALS_INPUT,
    TodoistCredentials,
    TodoistCredentialsInput,
    TodoistCredentialsField,
)
from backend.data.block import Block, BlockCategory, BlockOutput, BlockSchema
from backend.data.model import SchemaField


class TodoistCreateCommentBlock(Block):
    """Creates a new comment on a Todoist task or project"""

    class Input(BlockSchema):
        credentials: TodoistCredentialsInput = TodoistCredentialsField([])
        content: str = SchemaField(description="Comment content")
        task_id: Optional[str] = SchemaField(description="Task ID to comment on", default=None)
        project_id: Optional[str] = SchemaField(description="Project ID to comment on", default=None)
        attachment: Optional[dict] = SchemaField(description="Optional file attachment", default=None)

    class Output(BlockSchema):
        id: str = SchemaField(description="ID of created comment")
        content: str = SchemaField(description="Comment content")
        posted_at: str = SchemaField(description="Comment timestamp")
        task_id: Optional[str] = SchemaField(description="Associated task ID", default=None)
        project_id: Optional[str] = SchemaField(description="Associated project ID", default=None)

    def __init__(self):
        super().__init__(
            id="b6a1c724-2e85-4f8a-c4d2-89e12a042def",
            description="Creates a new comment on a Todoist task or project",
            categories={BlockCategory.PRODUCTIVITY},
            input_schema=TodoistCreateCommentBlock.Input,
            output_schema=TodoistCreateCommentBlock.Output,
            test_input={
                "credentials": TEST_CREDENTIALS_INPUT,
                "content": "Test comment",
                "task_id": "2995104339"
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                ("id", "2992679862"),
                ("content", "Test comment"),
                ("posted_at", "2016-09-22T07:00:00.000000Z"),
                ("task_id", "2995104339"),
                ("project_id", None)
            ],
            test_mock={
                "add_comment": lambda *args, **kwargs: (
                    {
                        "id": "2992679862",
                        "content": "Test comment",
                        "posted_at": "2016-09-22T07:00:00.000000Z",
                        "task_id": "2995104339",
                        "project_id": None
                    },
                    None,
                )
            },
        )

    @staticmethod
    def create_comment(credentials: TodoistCredentials, content: str, task_id: Optional[str] = None,
                      project_id: Optional[str] = None, attachment: Optional[dict] = None):
        try:
            api = TodoistAPI(credentials.access_token.get_secret_value())
            comment = api.add_comment(
                content=content,
                task_id=task_id,
                project_id=project_id,
                attachment=attachment
            )
            return comment.__dict__

        except Exception as e:
            raise e

    def run(
        self,
        input_data: Input,
        *,
        credentials: TodoistCredentials,
        **kwargs,
    ) -> BlockOutput:
        try:
            if not input_data.task_id and not input_data.project_id:
                raise ValueError("Either task_id or project_id must be provided")

            comment_data = self.create_comment(
                credentials,
                input_data.content,
                task_id=input_data.task_id,
                project_id=input_data.project_id,
                attachment=input_data.attachment
            )

            if comment_data:
                yield "id", comment_data["id"]
                yield "content", comment_data["content"]
                yield "posted_at", comment_data["posted_at"]
                yield "task_id", comment_data["task_id"]
                yield "project_id", comment_data["project_id"]

        except Exception as e:
            yield "error", str(e)

class TodoistGetCommentsBlock(Block):
    """Get all comments for a Todoist task or project"""

    class Input(BlockSchema):
        credentials: TodoistCredentialsInput = TodoistCredentialsField([])
        task_id: Optional[str] = SchemaField(description="Task ID to get comments for", default=None)
        project_id: Optional[str] = SchemaField(description="Project ID to get comments for", default=None)

    class Output(BlockSchema):
        comments: list = SchemaField(description="List of comments")

    def __init__(self):
        super().__init__(
            id="b6a1c724-2e85-4f8a-c4d2-89e12a042def",
            description="Get all comments for a Todoist task or project",
            categories={BlockCategory.PRODUCTIVITY},
            input_schema=TodoistGetCommentsBlock.Input,
            output_schema=TodoistGetCommentsBlock.Output,
            test_input={
                "credentials": TEST_CREDENTIALS_INPUT,
                "task_id": "2995104339"
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                ("comments", [
                    {
                        "id": "2992679862",
                        "content": "Test comment",
                        "posted_at": "2016-09-22T07:00:00.000000Z",
                        "task_id": "2995104339",
                        "project_id": None,
                        "attachment": None
                    }
                ])
            ],
            test_mock={
                "get_comments": lambda *args, **kwargs: (
                    [
                        {
                            "id": "2992679862",
                            "content": "Test comment",
                            "posted_at": "2016-09-22T07:00:00.000000Z",
                            "task_id": "2995104339",
                            "project_id": None,
                            "attachment": None
                        }
                    ],
                    None,
                )
            },
        )

    @staticmethod
    def get_comments(credentials: TodoistCredentials, task_id: Optional[str] = None,
                    project_id: Optional[str] = None):
        try:
            api = TodoistAPI(credentials.access_token.get_secret_value())
            comments = api.get_comments(task_id=task_id, project_id=project_id)
            return [comment.__dict__ for comment in comments]

        except Exception as e:
            raise e

    def run(
        self,
        input_data: Input,
        *,
        credentials: TodoistCredentials,
        **kwargs,
    ) -> BlockOutput:
        try:
            if not input_data.task_id and not input_data.project_id:
                raise ValueError("Either task_id or project_id must be provided")

            comments = self.get_comments(
                credentials,
                task_id=input_data.task_id,
                project_id=input_data.project_id
            )

            yield "comments", comments

        except Exception as e:
            yield "error", str(e)

class TodoistGetCommentBlock(Block):
    """Get a single comment from Todoist"""

    class Input(BlockSchema):
        credentials: TodoistCredentialsInput = TodoistCredentialsField([])
        comment_id: str = SchemaField(description="Comment ID to retrieve")

    class Output(BlockSchema):
        content: str = SchemaField(description="Comment content")
        id: str = SchemaField(description="Comment ID")
        posted_at: str = SchemaField(description="Comment timestamp")
        project_id: Optional[str] = SchemaField(description="Associated project ID", default=None)
        task_id: Optional[str] = SchemaField(description="Associated task ID", default=None)
        attachment: Optional[dict] = SchemaField(description="Optional file attachment", default=None)

    def __init__(self):
        super().__init__(
            id="b6a1c724-2e85-4f8a-c4d2-89e12a042dff",
            description="Get a single comment from Todoist",
            categories={BlockCategory.PRODUCTIVITY},
            input_schema=TodoistGetCommentBlock.Input,
            output_schema=TodoistGetCommentBlock.Output,
            test_input={
                "credentials": TEST_CREDENTIALS_INPUT,
                "comment_id": "2992679862"
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                ("content", "Test comment"),
                ("id", "2992679862"),
                ("posted_at", "2016-09-22T07:00:00.000000Z"),
                ("project_id", None),
                ("task_id", "2995104339"),
                ("attachment", None)
            ],
            test_mock={
                "get_comment": lambda *args, **kwargs: (
                    {
                        "content": "Test comment",
                        "id": "2992679862",
                        "posted_at": "2016-09-22T07:00:00.000000Z",
                        "project_id": None,
                        "task_id": "2995104339",
                        "attachment": None
                    },
                    None,
                )
            },
        )

    @staticmethod
    def get_comment(credentials: TodoistCredentials, comment_id: str):
        try:
            api = TodoistAPI(credentials.access_token.get_secret_value())
            comment = api.get_comment(comment_id=comment_id)
            return comment.__dict__

        except Exception as e:
            raise e

    def run(
        self,
        input_data: Input,
        *,
        credentials: TodoistCredentials,
        **kwargs,
    ) -> BlockOutput:
        try:
            comment_data = self.get_comment(
                credentials,
                comment_id=input_data.comment_id
            )

            if comment_data:
                yield "content", comment_data["content"]
                yield "id", comment_data["id"]
                yield "posted_at", comment_data["posted_at"]
                yield "project_id", comment_data["project_id"]
                yield "task_id", comment_data["task_id"]
                yield "attachment", comment_data["attachment"]

        except Exception as e:
            yield "error", str(e)

class TodoistUpdateCommentBlock(Block):
    """Updates a Todoist comment"""

    class Input(BlockSchema):
        credentials: TodoistCredentialsInput = TodoistCredentialsField([])
        comment_id: str = SchemaField(description="Comment ID to update")
        content: str = SchemaField(description="New content for the comment")

    class Output(BlockSchema):
        content: str = SchemaField(description="Updated comment content")
        id: str = SchemaField(description="Comment ID")
        posted_at: str = SchemaField(description="Comment timestamp")
        project_id: Optional[str] = SchemaField(description="Associated project ID", default=None)
        task_id: Optional[str] = SchemaField(description="Associated task ID", default=None)
        attachment: Optional[dict] = SchemaField(description="Optional file attachment", default=None)

    def __init__(self):
        super().__init__(
            id="b6a1c724-2e85-4f8a-c4d2-89e12a042d00",
            description="Updates a Todoist comment",
            categories={BlockCategory.PRODUCTIVITY},
            input_schema=TodoistUpdateCommentBlock.Input,
            output_schema=TodoistUpdateCommentBlock.Output,
            test_input={
                "credentials": TEST_CREDENTIALS_INPUT,
                "comment_id": "2992679862",
                "content": "Need one bottle of milk"
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                ("content", "Need one bottle of milk"),
                ("id", "2992679862"),
                ("posted_at", "2016-09-22T07:00:00.000000Z"),
                ("project_id", None),
                ("task_id", "2995104339"),
                ("attachment", {
                    "file_name": "File.pdf",
                    "file_type": "application/pdf",
                    "file_url": "https://s3.amazonaws.com/domorebetter/Todoist+Setup+Guide.pdf",
                    "resource_type": "file"
                })
            ],
            test_mock={
                "update_comment": lambda *args, **kwargs: (
                    {
                        "content": "Need one bottle of milk",
                        "id": "2992679862",
                        "posted_at": "2016-09-22T07:00:00.000000Z",
                        "project_id": None,
                        "task_id": "2995104339",
                        "attachment": {
                            "file_name": "File.pdf",
                            "file_type": "application/pdf",
                            "file_url": "https://s3.amazonaws.com/domorebetter/Todoist+Setup+Guide.pdf",
                            "resource_type": "file"
                        }
                    },
                    None,
                )
            },
        )

    @staticmethod
    def update_comment(credentials: TodoistCredentials, comment_id: str, content: str):
        try:
            api = TodoistAPI(credentials.access_token.get_secret_value())
            comment = api.update_comment(
                comment_id=comment_id,
                content=content
            )
            return comment.__dict__

        except Exception as e:
            raise e

    def run(
        self,
        input_data: Input,
        *,
        credentials: TodoistCredentials,
        **kwargs,
    ) -> BlockOutput:
        try:
            comment_data = self.update_comment(
                credentials,
                comment_id=input_data.comment_id,
                content=input_data.content
            )

            if comment_data:
                yield "content", comment_data["content"]
                yield "id", comment_data["id"]
                yield "posted_at", comment_data["posted_at"]
                yield "project_id", comment_data["project_id"]
                yield "task_id", comment_data["task_id"]
                yield "attachment", comment_data["attachment"]

        except Exception as e:
            yield "error", str(e)

class TodoistDeleteCommentBlock(Block):
    """Deletes a Todoist comment"""

    class Input(BlockSchema):
        credentials: TodoistCredentialsInput = TodoistCredentialsField([])
        comment_id: str = SchemaField(description="Comment ID to delete")

    class Output(BlockSchema):
        success: bool = SchemaField(description="Whether the deletion was successful")

    def __init__(self):
        super().__init__(
            id="b6a1c724-2e85-4f8a-c4d2-89e12a042d01",
            description="Deletes a Todoist comment",
            categories={BlockCategory.PRODUCTIVITY},
            input_schema=TodoistDeleteCommentBlock.Input,
            output_schema=TodoistDeleteCommentBlock.Output,
            test_input={
                "credentials": TEST_CREDENTIALS_INPUT,
                "comment_id": "2992679862"
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                ("success", True)
            ],
            test_mock={
                "delete_comment": lambda *args, **kwargs: (
                    True,
                    None,
                )
            },
        )

    @staticmethod
    def delete_comment(credentials: TodoistCredentials, comment_id: str):
        try:
            api = TodoistAPI(credentials.access_token.get_secret_value())
            success = api.delete_comment(comment_id=comment_id)
            return success

        except Exception as e:
            raise e

    def run(
        self,
        input_data: Input,
        *,
        credentials: TodoistCredentials,
        **kwargs,
    ) -> BlockOutput:
        try:
            success = self.delete_comment(
                credentials,
                comment_id=input_data.comment_id
            )

            yield "success", success

        except Exception as e:
            yield "error", str(e)
