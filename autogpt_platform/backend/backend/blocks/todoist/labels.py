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


class TodoistCreateLabelBlock(Block):
    """Creates a new label in Todoist"""

    class Input(BlockSchema):
        credentials: TodoistCredentialsInput = TodoistCredentialsField([])
        name: str = SchemaField(description="Name of the label")
        order: Optional[int] = SchemaField(description="Label order", default=None)
        color: Optional[str] = SchemaField(description="The color of the label icon", default=None)
        is_favorite: Optional[bool] = SchemaField(description="Whether the label is a favorite", default=None)

    class Output(BlockSchema):
        id: str = SchemaField(description="ID of created label")
        name: str = SchemaField(description="Name of the label")
        color: str = SchemaField(description="Color of the label")
        order: int = SchemaField(description="Label order")
        is_favorite: bool = SchemaField(description="Favorite status")

    def __init__(self):
        super().__init__(
            id="a7b2c835-3f96-5g9b-d5e3-90f23b153def",
            description="Creates a new label in Todoist",
            categories={BlockCategory.PRODUCTIVITY},
            input_schema=TodoistCreateLabelBlock.Input,
            output_schema=TodoistCreateLabelBlock.Output,
            test_input={
                "credentials": TEST_CREDENTIALS_INPUT,
                "name": "Test Label",
                "color": "charcoal",
                "order": 1,
                "is_favorite": False
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                ("id", "2156154810"),
                ("name", "Test Label"),
                ("color", "charcoal"),
                ("order", 1),
                ("is_favorite", False)
            ],
            test_mock={
                "create_label": lambda *args, **kwargs: (
                    {
                        "id": "2156154810",
                        "name": "Test Label",
                        "color": "charcoal",
                        "order": 1,
                        "is_favorite": False
                    },
                    None,
                )
            },
        )

    @staticmethod
    def create_label(credentials: TodoistCredentials, name: str, **kwargs):
        try:
            api = TodoistAPI(credentials.access_token.get_secret_value())
            label = api.add_label(name=name, **kwargs)
            return label.__dict__

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
            label_args = {
                "order": input_data.order,
                "color": input_data.color,
                "is_favorite": input_data.is_favorite
            }

            label_data = self.create_label(
                credentials,
                input_data.name,
                **{k:v for k,v in label_args.items() if v is not None}
            )

            if label_data:
                yield "id", label_data["id"]
                yield "name", label_data["name"]
                yield "color", label_data["color"]
                yield "order", label_data["order"]
                yield "is_favorite", label_data["is_favorite"]

        except Exception as e:
            yield "error", str(e)

class TodoistListLabelsBlock(Block):
    """Gets all personal labels from Todoist"""

    class Input(BlockSchema):
        credentials: TodoistCredentialsInput = TodoistCredentialsField([])

    class Output(BlockSchema):
        labels: list = SchemaField(description="List of labels")

    def __init__(self):
        super().__init__(
            id="d9e4a167-2b8c-4f1d-9c3a-5e7b8d0f4a12",
            description="Gets all personal labels from Todoist",
            categories={BlockCategory.PRODUCTIVITY},
            input_schema=TodoistListLabelsBlock.Input,
            output_schema=TodoistListLabelsBlock.Output,
            test_input={
                "credentials": TEST_CREDENTIALS_INPUT
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                ("labels", [
                    {
                        "id": "2156154810",
                        "name": "Test Label",
                        "color": "charcoal",
                        "order": 1,
                        "is_favorite": False
                    }
                ])
            ],
            test_mock={
                "get_labels": lambda *args, **kwargs: (
                    [{
                        "id": "2156154810",
                        "name": "Test Label",
                        "color": "charcoal",
                        "order": 1,
                        "is_favorite": False
                    }],
                    None,
                )
            },
        )

    @staticmethod
    def get_labels(credentials: TodoistCredentials):
        try:
            api = TodoistAPI(credentials.access_token.get_secret_value())
            labels = api.get_labels()
            return [label.__dict__ for label in labels]

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
            labels = self.get_labels(credentials)
            yield "labels", labels

        except Exception as e:
            yield "error", str(e)

class TodoistGetLabelBlock(Block):
    """Gets a personal label from Todoist by ID"""

    class Input(BlockSchema):
        credentials: TodoistCredentialsInput = TodoistCredentialsField([])
        label_id: str = SchemaField(description="ID of the label to retrieve")

    class Output(BlockSchema):
        id: str = SchemaField(description="ID of the label")
        name: str = SchemaField(description="Name of the label")
        color: str = SchemaField(description="Color of the label")
        order: int = SchemaField(description="Label order")
        is_favorite: bool = SchemaField(description="Favorite status")

    def __init__(self):
        super().__init__(
            id="f8c1b234-5d6e-7a8b-9c0d-1e2f3a4b5c6d",
            description="Gets a personal label from Todoist by ID",
            categories={BlockCategory.PRODUCTIVITY},
            input_schema=TodoistGetLabelBlock.Input,
            output_schema=TodoistGetLabelBlock.Output,
            test_input={
                "credentials": TEST_CREDENTIALS_INPUT,
                "label_id": "2156154810"
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                ("id", "2156154810"),
                ("name", "Test Label"),
                ("color", "charcoal"),
                ("order", 1),
                ("is_favorite", False)
            ],
            test_mock={
                "get_label": lambda *args, **kwargs: (
                    {
                        "id": "2156154810",
                        "name": "Test Label",
                        "color": "charcoal",
                        "order": 1,
                        "is_favorite": False
                    },
                    None,
                )
            },
        )

    @staticmethod
    def get_label(credentials: TodoistCredentials, label_id: str):
        try:
            api = TodoistAPI(credentials.access_token.get_secret_value())
            label = api.get_label(label_id=label_id)
            return label.__dict__

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
            label_data = self.get_label(credentials, input_data.label_id)

            if label_data:
                yield "id", label_data["id"]
                yield "name", label_data["name"]
                yield "color", label_data["color"]
                yield "order", label_data["order"]
                yield "is_favorite", label_data["is_favorite"]

        except Exception as e:
            yield "error", str(e)

class TodoistUpdateLabelBlock(Block):
    """Updates a personal label in Todoist"""

    class Input(BlockSchema):
        credentials: TodoistCredentialsInput = TodoistCredentialsField([])
        label_id: str = SchemaField(description="ID of the label to update")
        name: Optional[str] = SchemaField(description="New name of the label", default=None)
        order: Optional[int] = SchemaField(description="Label order", default=None)
        color: Optional[str] = SchemaField(description="The color of the label icon", default=None)
        is_favorite: Optional[bool] = SchemaField(description="Whether the label is a favorite", default=None)

    class Output(BlockSchema):
        id: str = SchemaField(description="ID of the label")
        name: str = SchemaField(description="Name of the label")
        color: str = SchemaField(description="Color of the label")
        order: int = SchemaField(description="Label order")
        is_favorite: bool = SchemaField(description="Favorite status")

    def __init__(self):
        super().__init__(
            id="b3c4d567-8e9f-0a1b-2c3d-4e5f6g7h8i9j",
            description="Updates a personal label in Todoist",
            categories={BlockCategory.PRODUCTIVITY},
            input_schema=TodoistUpdateLabelBlock.Input,
            output_schema=TodoistUpdateLabelBlock.Output,
            test_input={
                "credentials": TEST_CREDENTIALS_INPUT,
                "label_id": "2156154810",
                "name": "Updated Label",
                "color": "charcoal",
                "order": 2,
                "is_favorite": True
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                ("id", "2156154810"),
                ("name", "Updated Label"),
                ("color", "charcoal"),
                ("order", 2),
                ("is_favorite", True)
            ],
            test_mock={
                "update_label": lambda *args, **kwargs: (
                    {
                        "id": "2156154810",
                        "name": "Updated Label",
                        "color": "charcoal",
                        "order": 2,
                        "is_favorite": True
                    },
                    None,
                )
            },
        )

    @staticmethod
    def update_label(credentials: TodoistCredentials, label_id: str, **kwargs):
        try:
            api = TodoistAPI(credentials.access_token.get_secret_value())
            label = api.update_label(label_id=label_id, **kwargs)
            return label.__dict__

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
            label_args = {
                "name": input_data.name,
                "order": input_data.order,
                "color": input_data.color,
                "is_favorite": input_data.is_favorite
            }

            label_data = self.update_label(
                credentials,
                input_data.label_id,
                **{k:v for k,v in label_args.items() if v is not None}
            )

            if label_data:
                yield "id", label_data["id"]
                yield "name", label_data["name"]
                yield "color", label_data["color"]
                yield "order", label_data["order"]
                yield "is_favorite", label_data["is_favorite"]

        except Exception as e:
            yield "error", str(e)

class TodoistDeleteLabelBlock(Block):
    """Deletes a personal label in Todoist"""

    class Input(BlockSchema):
        credentials: TodoistCredentialsInput = TodoistCredentialsField([])
        label_id: str = SchemaField(description="ID of the label to delete")

    class Output(BlockSchema):
        success: bool = SchemaField(description="Whether the deletion was successful")

    def __init__(self):
        super().__init__(
            id="k4l5m678-9n0p-1q2r-3s4t-5u6v7w8x9y10",
            description="Deletes a personal label in Todoist",
            categories={BlockCategory.PRODUCTIVITY},
            input_schema=TodoistDeleteLabelBlock.Input,
            output_schema=TodoistDeleteLabelBlock.Output,
            test_input={
                "credentials": TEST_CREDENTIALS_INPUT,
                "label_id": "2156154810"
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                ("success", True)
            ],
            test_mock={
                "delete_label": lambda *args, **kwargs: (
                    True,
                    None,
                )
            },
        )

    @staticmethod
    def delete_label(credentials: TodoistCredentials, label_id: str):
        try:
            api = TodoistAPI(credentials.access_token.get_secret_value())
            success = api.delete_label(label_id=label_id)
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
            success = self.delete_label(credentials, input_data.label_id)
            yield "success", success

        except Exception as e:
            yield "error", str(e)

#  check for omit personal
class TodoistGetSharedLabelsBlock(Block):
    """Gets all shared labels from Todoist"""

    class Input(BlockSchema):
        credentials: TodoistCredentialsInput = TodoistCredentialsField([])
        omit_personal: Optional[bool] = SchemaField(
            description="Whether to exclude personal labels",
            default=False
        )

    class Output(BlockSchema):
        labels: list = SchemaField(description="List of shared label names")

    def __init__(self):
        super().__init__(
            id="m7n8p901-2q3r-4s5t-6u7v-8w9x0y1z2a3b",
            description="Gets all shared labels from Todoist",
            categories={BlockCategory.PRODUCTIVITY},
            input_schema=TodoistGetSharedLabelsBlock.Input,
            output_schema=TodoistGetSharedLabelsBlock.Output,
            test_input={
                "credentials": TEST_CREDENTIALS_INPUT,
                "omit_personal": False
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                ("labels", ["Label1", "Label2", "Label3"])
            ],
            test_mock={
                "get_shared_labels": lambda *args, **kwargs: (
                    ["Label1", "Label2", "Label3"],
                    None,
                )
            },
        )

    @staticmethod
    def get_shared_labels(credentials: TodoistCredentials, omit_personal: bool = False):
        try:
            api = TodoistAPI(credentials.access_token.get_secret_value())
            labels = api.get_shared_labels()
            return labels

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
            labels = self.get_shared_labels(credentials)
            yield "labels", labels

        except Exception as e:
            yield "error", str(e)

# Error in todoist doumentation
class TodoistRenameSharedLabelsBlock(Block):
    """Renames all instances of a shared label"""

    class Input(BlockSchema):
        credentials: TodoistCredentialsInput = TodoistCredentialsField([])
        name: str = SchemaField(description="The name of the existing label to rename")
        new_name: str = SchemaField(description="The new name for the label")

    class Output(BlockSchema):
        success: bool = SchemaField(description="Whether the rename was successful")

    def __init__(self):
        super().__init__(
            id="c5d6e789-0f1g-2h3i-4j5k-6l7m8n9o0p1q",
            description="Renames all instances of a shared label",
            categories={BlockCategory.PRODUCTIVITY},
            input_schema=TodoistRenameSharedLabelsBlock.Input,
            output_schema=TodoistRenameSharedLabelsBlock.Output,
            test_input={
                "credentials": TEST_CREDENTIALS_INPUT,
                "name": "OldLabel",
                "new_name": "NewLabel"
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                ("success", True)
            ],
            test_mock={
                "rename_shared_labels": lambda *args, **kwargs: (
                    True,
                    None,
                )
            },
        )

    @staticmethod
    def rename_shared_labels(credentials: TodoistCredentials, name: str, new_name: str):
        try:
            api = TodoistAPI(credentials.access_token.get_secret_value())
            success = api.rename_shared_label(name=name, new_name=new_name)
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
            success = self.rename_shared_labels(credentials, input_data.name, input_data.new_name)
            yield "success", success

        except Exception as e:
            yield "error", str(e)

# Error in todoist doumentation
class TodoistRemoveSharedLabelsBlock(Block):
    """Removes all instances of a shared label"""

    class Input(BlockSchema):
        credentials: TodoistCredentialsInput = TodoistCredentialsField([])
        name: str = SchemaField(description="The name of the label to remove")

    class Output(BlockSchema):
        success: bool = SchemaField(description="Whether the removal was successful")

    def __init__(self):
        super().__init__(
            id="r8s9t012-3u4v-5w6x-7y8z-9a0b1c2d3e4f",
            description="Removes all instances of a shared label",
            categories={BlockCategory.PRODUCTIVITY},
            input_schema=TodoistRemoveSharedLabelsBlock.Input,
            output_schema=TodoistRemoveSharedLabelsBlock.Output,
            test_input={
                "credentials": TEST_CREDENTIALS_INPUT,
                "name": "LabelToRemove"
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                ("success", True)
            ],
            test_mock={
                "remove_shared_labels": lambda *args, **kwargs: (
                    True,
                    None,
                )
            },
        )

    @staticmethod
    def remove_shared_label(credentials: TodoistCredentials, name: str):
        try:
            api = TodoistAPI(credentials.access_token.get_secret_value())
            success = api.remove_shared_label(name=name)
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
            success = self.remove_shared_label(credentials, input_data.name)
            yield "success", success

        except Exception as e:
            yield "error", str(e)
