# -* encoding: utf-8 *-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import os
from typing import (
    NamedTuple,
    Sequence,
    Dict,
    Union,
    cast,
    Optional,
)
from urllib.parse import quote  # noqa: F401

from aptly_api.base import BaseAPIClient, AptlyAPIException

Task = NamedTuple("Task", [
    ("id", str),
    ("name", Optional[str]),
    ("state", Optional[str]),
])


class TaskAPISection(BaseAPIClient):
    @staticmethod
    def task_from_response(api_response: Dict[str, Union[str, None]]) -> Task:
        return Task(
            id=api_response["ID"],
            name=api_response["Name"],
            state=api_response["State"],
        )

    def list(self) -> Sequence[Task]:
        resp = self.do_get("api/tasks")

        tasks = []
        for tdesc in resp.json():
            tasks.append(
                self.task_from_response(tdesc)
            )
        return tasks

    def show(self, id: str) -> Task:
        resp = self.do_get("api/tasks/%s" % quote(id))

        return self.task_from_response(resp.json())

    def outputshow(self, id: str) -> str:
        resp = self.do_get("api/tasks/%s/output" % quote(id))

        return "%s - %s" % (resp.status_code, resp.text)

    def clear(self) -> None:
        self.do_post("api/tasks/clear")
