import logging
import typing

import autogpt_libs.auth.depends
import autogpt_libs.auth.middleware
import autogpt_libs.utils.cache
import fastapi
import prisma

import backend.data.graph
import backend.executor
import backend.integrations.creds_manager
import backend.integrations.webhooks.graph_lifecycle_hooks
import backend.server.v2.library.db
import backend.server.v2.library.model
import backend.util.service

logger = logging.getLogger(__name__)

router = fastapi.APIRouter()
integration_creds_manager = (
    backend.integrations.creds_manager.IntegrationCredentialsManager()
)


@autogpt_libs.utils.cache.thread_cached
def execution_manager_client() -> backend.executor.ExecutionManager:
    return backend.util.service.get_service_client(backend.executor.ExecutionManager)


@router.get(
    "/agents",
    tags=["library", "private"],
    dependencies=[fastapi.Depends(autogpt_libs.auth.middleware.auth_middleware)],
)
async def get_library_agents(
    user_id: typing.Annotated[
        str, fastapi.Depends(autogpt_libs.auth.depends.get_user_id)
    ]
) -> typing.Sequence[backend.server.v2.library.model.LibraryAgent]:
    """
    Get all agents in the user's library, including both created and saved agents.
    """
    try:
        agents = await backend.server.v2.library.db.get_library_agents(user_id)
        return agents
    except Exception as e:
        logger.exception(f"Exception occurred whilst getting library agents: {e}")
        raise fastapi.HTTPException(
            status_code=500, detail="Failed to get library agents"
        )


@router.post(
    "/agents/{store_listing_version_id}",
    tags=["library", "private"],
    dependencies=[fastapi.Depends(autogpt_libs.auth.middleware.auth_middleware)],
    status_code=201,
)
async def add_agent_to_library(
    store_listing_version_id: str,
    user_id: typing.Annotated[
        str, fastapi.Depends(autogpt_libs.auth.depends.get_user_id)
    ],
) -> fastapi.Response:
    """
    Add an agent from the store to the user's library.

    Args:
        store_listing_version_id (str): ID of the store listing version to add
        user_id (str): ID of the authenticated user

    Returns:
        fastapi.Response: 201 status code on success

    Raises:
        HTTPException: If there is an error adding the agent to the library
    """
    try:
        # Get the graph from the store listing
        store_listing_version = (
            await prisma.models.StoreListingVersion.prisma().find_unique(
                where={"id": store_listing_version_id}, include={"Agent": True}
            )
        )

        if not store_listing_version or not store_listing_version.Agent:
            raise fastapi.HTTPException(
                status_code=404,
                detail=f"Store listing version {store_listing_version_id} not found",
            )

        agent = store_listing_version.Agent

        if agent.userId == user_id:
            raise fastapi.HTTPException(
                status_code=400, detail="Cannot add own agent to library"
            )

        # Create a new graph from the template
        graph = await backend.data.graph.get_graph(
            agent.id, agent.version, template=True, user_id=user_id
        )

        if not graph:
            raise fastapi.HTTPException(
                status_code=404, detail=f"Agent {agent.id} not found"
            )

        # Create a deep copy with new IDs
        graph.version = 1
        graph.is_template = False
        graph.is_active = True
        graph.reassign_ids(user_id=user_id, reassign_graph_id=True)

        # Save the new graph
        graph = await backend.data.graph.create_graph(graph, user_id=user_id)
        graph = (
            await backend.integrations.webhooks.graph_lifecycle_hooks.on_graph_activate(
                graph,
                get_credentials=lambda id: integration_creds_manager.get(user_id, id),
            )
        )

        return fastapi.Response(status_code=201)

    except Exception as e:
        logger.exception(f"Exception occurred whilst adding agent to library: {e}")
        raise fastapi.HTTPException(
            status_code=500, detail="Failed to add agent to library"
        )


@router.get("/presets")
async def get_presets(
    user_id: typing.Annotated[
        str, fastapi.Depends(autogpt_libs.auth.depends.get_user_id)
    ],
    page: int = 1,
    page_size: int = 10,
) -> backend.server.v2.library.model.LibraryAgentPresetResponse:
    try:
        presets = await backend.server.v2.library.db.get_presets(
            user_id, page, page_size
        )
        return presets
    except Exception as e:
        logger.exception(f"Exception occurred whilst getting presets: {e}")
        raise fastapi.HTTPException(status_code=500, detail="Failed to get presets")


@router.get("/presets/{preset_id}")
async def get_preset(
    preset_id: str,
    user_id: typing.Annotated[
        str, fastapi.Depends(autogpt_libs.auth.depends.get_user_id)
    ],
) -> backend.server.v2.library.model.LibraryAgentPreset:
    try:
        preset = await backend.server.v2.library.db.get_preset(user_id, preset_id)
        if not preset:
            raise fastapi.HTTPException(
                status_code=404,
                detail=f"Preset {preset_id} not found",
            )
        return preset
    except Exception as e:
        logger.exception(f"Exception occurred whilst getting preset: {e}")
        raise fastapi.HTTPException(status_code=500, detail="Failed to get preset")


@router.post("/presets")
async def create_preset(
    preset: backend.server.v2.library.model.CreateLibraryAgentPresetRequest,
    user_id: typing.Annotated[
        str, fastapi.Depends(autogpt_libs.auth.depends.get_user_id)
    ],
) -> backend.server.v2.library.model.LibraryAgentPreset:
    try:
        return await backend.server.v2.library.db.create_or_update_preset(
            user_id, preset
        )
    except Exception as e:
        logger.exception(f"Exception occurred whilst creating preset: {e}")
        raise fastapi.HTTPException(status_code=500, detail="Failed to create preset")


@router.put("/presets/{preset_id}")
async def update_preset(
    preset_id: str,
    preset: backend.server.v2.library.model.CreateLibraryAgentPresetRequest,
    user_id: typing.Annotated[
        str, fastapi.Depends(autogpt_libs.auth.depends.get_user_id)
    ],
) -> backend.server.v2.library.model.LibraryAgentPreset:
    try:
        return await backend.server.v2.library.db.create_or_update_preset(
            user_id, preset, preset_id
        )
    except Exception as e:
        logger.exception(f"Exception occurred whilst updating preset: {e}")
        raise fastapi.HTTPException(status_code=500, detail="Failed to update preset")


@router.delete("/presets/{preset_id}")
async def delete_preset(
    preset_id: str,
    user_id: typing.Annotated[
        str, fastapi.Depends(autogpt_libs.auth.depends.get_user_id)
    ],
):
    try:
        await backend.server.v2.library.db.delete_preset(user_id, preset_id)
        return fastapi.Response(status_code=204)
    except Exception as e:
        logger.exception(f"Exception occurred whilst deleting preset: {e}")
        raise fastapi.HTTPException(status_code=500, detail="Failed to delete preset")


@router.post(
    path="/presets/{preset_id}/execute",
    tags=["presets"],
    dependencies=[fastapi.Depends(autogpt_libs.auth.middleware.auth_middleware)],
)
async def execute_preset(
    graph_id: str,
    graph_version: int,
    preset_id: str,
    node_input: dict[typing.Any, typing.Any],
    user_id: typing.Annotated[
        str, fastapi.Depends(autogpt_libs.auth.depends.get_user_id)
    ],
) -> dict[str, typing.Any]:  # FIXME: add proper return type
    try:
        preset = await backend.server.v2.library.db.get_preset(user_id, preset_id)
        if not preset:
            raise fastapi.HTTPException(status_code=404, detail="Preset not found")

        merged_input = {**preset.inputs, **node_input}

        execution = execution_manager_client().add_execution(
            graph_id=graph_id,
            graph_version=graph_version,
            data=merged_input,
            user_id=user_id,
            preset_id=preset_id,
        )

        return {"id": execution.graph_exec_id}
    except Exception as e:
        msg = e.__str__().encode().decode("unicode_escape")
        raise fastapi.HTTPException(status_code=400, detail=msg)
