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


class TodoistListProjectsBlock(Block):
    """Gets all projects for a Todoist user"""

    class Input(BlockSchema):
        credentials: TodoistCredentialsInput = TodoistCredentialsField([])

    class Output(BlockSchema):
        names_list: list[str] = SchemaField(description="List of project names")
        ids_list: list[str] = SchemaField(description="List of project IDs")
        url_list: list[str] = SchemaField(description="List of project URLs")
        complete_data: list[dict] = SchemaField(description="Complete project data including all fields")

    def __init__(self):
        super().__init__(
            id="e141bce6-e0fa-4f3f-bbda-8a2bddc2c659",
            description="Gets all projects and their details from Todoist",
            categories={BlockCategory.PRODUCTIVITY},
            input_schema=TodoistListProjectsBlock.Input,
            output_schema=TodoistListProjectsBlock.Output,
            test_input={
                "credentials": TEST_CREDENTIALS_INPUT,
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                ("names_list", ["Inbox"]),
                ("ids_list", ["220474322"]),
                ("url_list", ["https://todoist.com/showProject?id=220474322"]),
                ("complete_data", [{
                    "id": "220474322",
                    "name": "Inbox",
                    "url": "https://todoist.com/showProject?id=220474322"
                }])
            ],
            test_mock={
                "get_project_lists": lambda *args, **kwargs: (
                    ["Inbox"],
                    ["220474322"],
                    ["https://todoist.com/showProject?id=220474322"],
                    [{"id": "220474322", "name": "Inbox", "url": "https://todoist.com/showProject?id=220474322"}],
                    None,
                )
            },
        )

    @staticmethod
    def get_project_lists(credentials: TodoistCredentials):
        try:
            api = TodoistAPI(credentials.access_token.get_secret_value())
            projects = api.get_projects()

            names = []
            ids = []
            urls = []
            complete_data = []

            for project in projects:
                names.append(project.name)
                ids.append(project.id)
                urls.append(project.url)
                complete_data.append(project.__dict__)

            return names, ids, urls, complete_data, None

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
            names, ids, urls, data, error = self.get_project_lists(credentials)

            if names:
                yield "names_list", names
            if ids:
                yield "ids_list", ids
            if urls:
                yield "url_list", urls
            if data:
                yield "complete_data", data

        except Exception as e:
            yield "error", str(e)

class TodoistCreateProjectBlock(Block):
    """Creates a new project in Todoist"""

    class Input(BlockSchema):
        credentials: TodoistCredentialsInput = TodoistCredentialsField([])
        name: str = SchemaField(description="Name of the project", advanced=False)
        parent_id: Optional[str] = SchemaField(description="Parent project ID", default=None, advanced=True)
        color: Optional[str] = SchemaField(description="Color of the project icon", default=None, advanced=True)
        is_favorite: bool = SchemaField(description="Whether the project is a favorite", default=False ,advanced=True)
        view_style: Optional[str] = SchemaField(description="Display style (list or board)", default=None, advanced=True)

    class Output(BlockSchema):
        project_id: str = SchemaField(description="ID of created project")
        project_name: str = SchemaField(description="Name of created project")
        project_url: str = SchemaField(description="URL of created project")
        complete_data: dict = SchemaField(description="Complete project data including all fields")
        error: str = SchemaField(description="Error message if the request failed")


    def __init__(self):
        super().__init__(
            id="f252bde7-e1fa-4f3f-ccda-9a2bddc2c770",
            description="Creates a new project in Todoist",
            categories={BlockCategory.PRODUCTIVITY},
            input_schema=TodoistCreateProjectBlock.Input,
            output_schema=TodoistCreateProjectBlock.Output,
            test_input={
                "credentials": TEST_CREDENTIALS_INPUT,
                "name": "Test Project"
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                ("project_id", "2203306141"),
                ("project_name", "Test Project"),
                ("project_url", "https://todoist.com/showProject?id=2203306141"),
                ("complete_data", {
                    "id": "2203306141",
                    "name": "Test Project",
                    "url": "https://todoist.com/showProject?id=2203306141"
                })
            ],
            test_mock={
                "create_project": lambda *args, **kwargs: (
                    "2203306141",
                    "Test Project",
                    "https://todoist.com/showProject?id=2203306141",
                    {"id": "2203306141", "name": "Test Project", "url": "https://todoist.com/showProject?id=2203306141"},
                    None
                )
            },
        )

    @staticmethod
    def create_project(credentials: TodoistCredentials, name: str, parent_id: Optional[str],
                      color: Optional[str], is_favorite: bool , view_style: Optional[str]):
        try:
            api = TodoistAPI(credentials.access_token.get_secret_value())
            params = {"name": name,"is_favorite":is_favorite}

            if parent_id is not None:
                params["parent_id"] = parent_id
            if color is not None:
                params["color"] = color
            if view_style is not None:
                params["view_style"] = view_style

            project = api.add_project(**params)
            return project.id, project.name, project.url, project.__dict__, None

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
            project_id, project_name, project_url, data, error = self.create_project(
                credentials=credentials,
                name=input_data.name,
                parent_id=input_data.parent_id,
                color=input_data.color,
                is_favorite=input_data.is_favorite,
                view_style=input_data.view_style
            )

            if project_id:
                yield "project_id", project_id
            if project_name:
                yield "project_name", project_name
            if project_url:
                yield "project_url", project_url
            if data:
                yield "complete_data", data

        except Exception as e:
            yield "error", str(e)

class TodoistGetProjectBlock(Block):
    """Gets details for a specific Todoist project"""

    class Input(BlockSchema):
        credentials: TodoistCredentialsInput = TodoistCredentialsField([])
        project_id: str = SchemaField(description="ID of the project to get details for", advanced=False)

    class Output(BlockSchema):
        project_id: str = SchemaField(description="ID of project")
        project_name: str = SchemaField(description="Name of project")
        project_url: str = SchemaField(description="URL of project")
        complete_data: dict = SchemaField(description="Complete project data including all fields")
        error: str = SchemaField(description="Error message if the request failed")

    def __init__(self):
        super().__init__(
            id="g363cef8-f1fb-4f3f-ddeb-0a2bddc2c881",
            description="Gets details for a specific Todoist project",
            categories={BlockCategory.PRODUCTIVITY},
            input_schema=TodoistGetProjectBlock.Input,
            output_schema=TodoistGetProjectBlock.Output,
            test_input={
                "credentials": TEST_CREDENTIALS_INPUT,
                "project_id": "2203306141"
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                ("project_id", "2203306141"),
                ("project_name", "Shopping List"),
                ("project_url", "https://todoist.com/showProject?id=2203306141"),
                ("complete_data", {
                    "id": "2203306141",
                    "name": "Shopping List",
                    "url": "https://todoist.com/showProject?id=2203306141"
                })
            ],
            test_mock={
                "get_project": lambda *args, **kwargs: (
                    "2203306141",
                    "Shopping List",
                    "https://todoist.com/showProject?id=2203306141",
                    {"id": "2203306141", "name": "Shopping List", "url": "https://todoist.com/showProject?id=2203306141"},
                    None
                )
            },
        )

    @staticmethod
    def get_project(credentials: TodoistCredentials, project_id: str):
        try:
            api = TodoistAPI(credentials.access_token.get_secret_value())
            project = api.get_project(project_id=project_id)

            return project.id, project.name, project.url, project.__dict__, None

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
            project_id, project_name, project_url, data, error = self.get_project(
                credentials=credentials,
                project_id=input_data.project_id
            )

            if project_id:
                yield "project_id", project_id
            if project_name:
                yield "project_name", project_name
            if project_url:
                yield "project_url", project_url
            if data:
                yield "complete_data", data

        except Exception as e:
            yield "error", str(e)

class TodoistUpdateProjectBlock(Block):
    """Updates an existing project in Todoist"""

    class Input(BlockSchema):
        credentials: TodoistCredentialsInput = TodoistCredentialsField([])
        project_id: str = SchemaField(description="ID of project to update", advanced=False)
        name: Optional[str] = SchemaField(description="New name for the project", default=None, advanced=False)
        color: Optional[str] = SchemaField(description="New color for the project icon", default=None, advanced=True)
        is_favorite: Optional[bool] = SchemaField(description="Whether the project should be a favorite", default=None, advanced=True)
        view_style: Optional[str] = SchemaField(description="Display style (list or board)", default=None, advanced=True)

    class Output(BlockSchema):
        success: bool = SchemaField(description="Whether the update was successful")
        error: str = SchemaField(description="Error message if the request failed")

    def __init__(self):
        super().__init__(
            id="h474dfg9-g2fc-4f3f-eefb-1b2bddc2c992",
            description="Updates an existing project in Todoist",
            categories={BlockCategory.PRODUCTIVITY},
            input_schema=TodoistUpdateProjectBlock.Input,
            output_schema=TodoistUpdateProjectBlock.Output,
            test_input={
                "credentials": TEST_CREDENTIALS_INPUT,
                "project_id": "2203306141",
                "name": "Things To Buy"
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                ("success", True)
            ],
            test_mock={
                "update_project": lambda *args, **kwargs: (True, None)
            },
        )

    @staticmethod
    def update_project(credentials: TodoistCredentials, project_id: str, name: Optional[str],
                      color: Optional[str], is_favorite: Optional[bool], view_style: Optional[str]):
        try:
            api = TodoistAPI(credentials.access_token.get_secret_value())
            params = {}

            if name is not None:
                params["name"] = name
            if color is not None:
                params["color"] = color
            if is_favorite is not None:
                params["is_favorite"] = is_favorite
            if view_style is not None:
                params["view_style"] = view_style

            success = api.update_project(project_id=project_id, **params)
            return success, None

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
            success, error = self.update_project(
                credentials=credentials,
                project_id=input_data.project_id,
                name=input_data.name,
                color=input_data.color,
                is_favorite=input_data.is_favorite,
                view_style=input_data.view_style
            )

            if success:
                yield "success", success

        except Exception as e:
            yield "error", str(e)

class TodoistDeleteProjectBlock(Block):
    """Deletes a project and all of its sections and tasks"""

    class Input(BlockSchema):
        credentials: TodoistCredentialsInput = TodoistCredentialsField([])
        project_id: str = SchemaField(description="ID of project to delete", advanced=False)

    class Output(BlockSchema):
        success: bool = SchemaField(description="Whether the deletion was successful")
        error: str = SchemaField(description="Error message if the request failed")


    def __init__(self):
        super().__init__(
            id="i585efg0-h3fd-4f3f-ffgc-2c2bddc2c003",
            description="Deletes a Todoist project and all its contents",
            categories={BlockCategory.PRODUCTIVITY},
            input_schema=TodoistDeleteProjectBlock.Input,
            output_schema=TodoistDeleteProjectBlock.Output,
            test_input={
                "credentials": TEST_CREDENTIALS_INPUT,
                "project_id": "2203306141"
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                ("success", True)
            ],
            test_mock={
                "delete_project": lambda *args, **kwargs: (True, None)
            },
        )

    @staticmethod
    def delete_project(credentials: TodoistCredentials, project_id: str):
        try:
            api = TodoistAPI(credentials.access_token.get_secret_value())
            success = api.delete_project(project_id=project_id)
            return success, None

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
            success, error = self.delete_project(
                credentials=credentials,
                project_id=input_data.project_id
            )

            if success:
                yield "success", success

        except Exception as e:
            yield "error", str(e)

class TodoistListCollaboratorsBlock(Block):
    """Gets all collaborators for a Todoist project"""

    class Input(BlockSchema):
        credentials: TodoistCredentialsInput = TodoistCredentialsField([])
        project_id: str = SchemaField(description="ID of the project to get collaborators for", advanced=False)

    class Output(BlockSchema):
        collaborator_ids: list[str] = SchemaField(description="List of collaborator IDs")
        collaborator_names: list[str] = SchemaField(description="List of collaborator names")
        collaborator_emails: list[str] = SchemaField(description="List of collaborator email addresses")
        complete_data: list[dict] = SchemaField(description="Complete collaborator data including all fields")
        error: str = SchemaField(description="Error message if the request failed")

    def __init__(self):
        super().__init__(
            id="j696fgh1-i4ge-4f3f-gghd-3d2bddc2d114",
            description="Gets all collaborators for a specific Todoist project",
            categories={BlockCategory.PRODUCTIVITY},
            input_schema=TodoistListCollaboratorsBlock.Input,
            output_schema=TodoistListCollaboratorsBlock.Output,
            test_input={
                "credentials": TEST_CREDENTIALS_INPUT,
                "project_id": "2203306141"
            },
            test_credentials=TEST_CREDENTIALS,
            test_output=[
                ("collaborator_ids", ["2671362", "2671366"]),
                ("collaborator_names", ["Alice", "Bob"]),
                ("collaborator_emails", ["alice@example.com", "bob@example.com"]),
                ("complete_data", [
                    {
                        "id": "2671362",
                        "name": "Alice",
                        "email": "alice@example.com"
                    },
                    {
                        "id": "2671366",
                        "name": "Bob",
                        "email": "bob@example.com"
                    }
                ])
            ],
            test_mock={
                "get_collaborators": lambda *args, **kwargs: (
                    ["2671362", "2671366"],
                    ["Alice", "Bob"],
                    ["alice@example.com", "bob@example.com"],
                    [
                        {"id": "2671362", "name": "Alice", "email": "alice@example.com"},
                        {"id": "2671366", "name": "Bob", "email": "bob@example.com"}
                    ],
                    None
                )
            },
        )

    @staticmethod
    def get_collaborators(credentials: TodoistCredentials, project_id: str):
        try:
            api = TodoistAPI(credentials.access_token.get_secret_value())
            collaborators = api.get_collaborators(project_id=project_id)

            ids = []
            names = []
            emails = []
            complete_data = []

            for collaborator in collaborators:
                ids.append(collaborator.id)
                names.append(collaborator.name)
                emails.append(collaborator.email)
                complete_data.append(collaborator.__dict__)

            return ids, names, emails, complete_data, None

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
            ids, names, emails, data, error = self.get_collaborators(
                credentials=credentials,
                project_id=input_data.project_id
            )

            if ids:
                yield "collaborator_ids", ids
            if names:
                yield "collaborator_names", names
            if emails:
                yield "collaborator_emails", emails
            if data:
                yield "complete_data", data

        except Exception as e:
            yield "error", str(e)
