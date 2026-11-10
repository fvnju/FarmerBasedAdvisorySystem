"""Build the HTTP routes for one resource.

The routes only bind HTTP methods, paths, and status codes to the controller.
The router shows only the operations that the service supports.
Each route needs a login. The service checks the privileges and the data scope.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Response, status
from sqlalchemy.orm import Session

from app.controller.base import BaseController
from app.database import get_db
from app.route.dependencies import CurrentActor
from app.schema.common import DeleteAllResult, Operation, Page

ItemId = Annotated[int, Path(ge=1, description="Record ID")]


def build_crud_router(controller_class: type[BaseController], *, prefix: str, tag: str) -> APIRouter:
    router = APIRouter(prefix=prefix, tags=[tag])
    operations = controller_class.operations()
    read_schema = controller_class.read_schema
    item_schema = controller_class.item_schema()
    create_schema = controller_class.create_schema
    update_schema = controller_class.update_schema
    query_schema = controller_class.query_schema

    def get_controller(actor: CurrentActor, db: Session = Depends(get_db)) -> BaseController:
        return controller_class(db, actor)

    Controller = Annotated[BaseController, Depends(get_controller)]

    if Operation.LIST in operations:

        @router.get(
            "",
            response_model=Page[item_schema],
            summary=f"List and search {tag}",
            description="Use q for search as the user types. Use page and size for pagination.",
        )
        def list_items(params: Annotated[query_schema, Query()], controller: Controller):
            return controller.list(params)

    if Operation.READ in operations:

        @router.get("/{item_id}", response_model=read_schema, summary=f"Get one record from {tag}")
        def get_item(item_id: ItemId, controller: Controller):
            return controller.get(item_id)

    if Operation.CREATE in operations and create_schema is not None:

        @router.post(
            "",
            response_model=read_schema,
            status_code=status.HTTP_201_CREATED,
            summary=f"Insert a record in {tag}",
        )
        def create_item(payload: create_schema, controller: Controller):
            return controller.create(payload)

    if Operation.UPDATE in operations and update_schema is not None:

        @router.patch("/{item_id}", response_model=read_schema, summary=f"Update a record in {tag}")
        def update_item(item_id: ItemId, payload: update_schema, controller: Controller):
            return controller.update(item_id, payload)

    if Operation.DELETE in operations:

        @router.delete(
            "/{item_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            response_class=Response,
            summary=f"Delete a record from {tag}",
        )
        def delete_item(item_id: ItemId, controller: Controller):
            controller.delete(item_id)

    if Operation.DELETE_ALL in operations:

        @router.delete(
            "",
            response_model=DeleteAllResult,
            summary=f"Delete all records from {tag}",
            description="Set confirm=true. Records that other records still use are skipped.",
        )
        def delete_all_items(
            controller: Controller,
            confirm: Annotated[bool, Query(description="Must be true")] = False,
        ):
            return controller.delete_all(confirm)

    return router
