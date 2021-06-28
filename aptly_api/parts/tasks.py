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
    ("id", int),
    ("name", Optional[str]),
    ("state", Optional[str]),
])

TaskState = {0: "IDLE", 1: "RUNNING", 2: "SUCCEEDED", 3: "FAILED"}

class TaskAPISection(BaseAPIClient):
    @staticmethod
    def task_from_response(api_response: Dict[str, Union[str, None]]) -> Task:
        return Task(
            id=api_response["ID"],
            name=api_response["Name"],
            state=TaskState[api_response["State"]],
        )

    def list(self) -> Sequence[Task]:
        resp = self.do_get("api/tasks")

        tasks = []
        if resp.json():
            for tdesc in resp.json():
                tasks.append(self.task_from_response(tdesc))
        return tasks

    def show(self, id: int) -> Task:
        resp = self.do_get("api/tasks/%d" % id)

        return self.task_from_response(resp.json())

    def output_show(self, id: int) -> str:
        resp = self.do_get("api/tasks/%d/output" % id)

        return "%s - %s" % (resp.status_code, resp.text)

    def clear(self) -> None:
        self.do_post("api/tasks-clear")

    def wait(self) -> None:
        self.do_get("api/tasks-wait")

    def wait_for_task_by_id(self, id: int) -> None:
        self.do_get("api/tasks/%d/wait" % id)

    def delete(self, id: int) -> Task:
        self.do_delete("api/tasks/%d" % id)
