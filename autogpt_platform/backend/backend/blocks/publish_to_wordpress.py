from typing import Literal

import requests
from autogpt_libs.supabase_integration_credentials_store.types import APIKeyCredentials

from backend.data.block import Block, BlockCategory, BlockOutput, BlockSchema
from backend.data.model import CredentialsField, CredentialsMetaInput, SchemaField

WordPressCredentials = CredentialsMetaInput[Literal["wordpress"], Literal["api_key"]]


def WordPressCredentialsField() -> WordPressCredentials:
    return CredentialsField(
        description="API_TOKEN for WordPress.",
        provider="wordpress",
        supported_credential_types={"api_key"},
    )


class PublishToWordpressBlock(Block):
    class Input(BlockSchema):
        credentials: WordPressCredentials = WordPressCredentialsField()
        site: str = SchemaField(
            description="Site ID or domain.",
            placeholder="example.wordpress.com",
        )
        title: str = SchemaField(
            description="The post title.",
            placeholder="My New Post",
        )
        content: str = SchemaField(
            description="The content of the post.",
            placeholder="Hello, this is my new post...",
        )

    class Output(BlockSchema):
        post_id: int = SchemaField(description="The ID of the newly created post.")
        url: str = SchemaField(description="The URL of the newly created post.")
        error: str = SchemaField(
            description="Any errors encountered during the post creation."
        )

    def __init__(self):
        super().__init__(
            id="c5f2c7a0-cf16-4d9e-8724-7f98883cadd2",
            description="Publish an AI generated article to WordPress.",
            categories={BlockCategory.SOCIAL},
            input_schema=PublishToWordpressBlock.Input,
            output_schema=PublishToWordpressBlock.Output,
            test_input={
                "site": "example.wordpress.com",
                "title": "My AI Post",
                "content": "This is a test post generated by AI.",
                "credentials": {
                    "provider": "wordpress",
                    "id": "test-id",
                    "type": "api_key",
                    "title": "WordPress Test Credentials",
                },
            },
            test_output=[
                ("post_id", 12345),
                ("url", "https://example.wordpress.com/my-ai-post"),
            ],
            test_mock={
                "publish_post": lambda *args, **kwargs: (
                    12345,
                    "https://example.wordpress.com/my-ai-post",
                )
            },
        )

    def publish_post(
        self, credentials: APIKeyCredentials, site: str, title: str, content: str
    ) -> tuple[int, str]:
        """Publish a new post to WordPress."""
        url = f"https://public-api.wordpress.com/rest/v1.1/sites/{site}/posts/new"
        headers = {
            "Authorization": f"Bearer {credentials.api_key.get_secret_value()}",
            "Content-Type": "application/json",
        }
        data = {"title": title, "content": content}

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        json_response = response.json()
        return json_response["ID"], json_response["URL"]

    def run(
        self, input_data: Input, *, credentials: APIKeyCredentials, **kwargs
    ) -> BlockOutput:
        try:
            post_id, post_url = self.publish_post(
                credentials, input_data.site, input_data.title, input_data.content
            )
            yield "post_id", post_id
            yield "url", post_url
        except requests.exceptions.RequestException as e:
            yield "error", str(e)
