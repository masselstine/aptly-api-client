# -* encoding: utf-8 *-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import os
from typing import (
    NamedTuple,
    Sequence,
    Dict,
    List,
    Union,
    cast,
    Optional,
)
from urllib.parse import quote  # noqa: F401

from aptly_api.base import BaseAPIClient, AptlyAPIException
from aptly_api.parts.tasks import Task, TaskAPISection

Mirror = NamedTuple("Mirror", [
    ("name", str),
    ("archive_root", Optional[str]),
    ("distribution", Optional[str]),
    ("components", Sequence[str]),
])


class MirrorAPISection(BaseAPIClient):
    @staticmethod
    def mirror_from_response(api_response: Dict[str, Union[str, None]]) -> Mirror:
        return Mirror(
            name=api_response["Name"],
            archive_root=api_response["ArchiveRoot"],
            distribution=api_response["Distribution"],
            components=cast(Sequence[str], api_response["Components"]),
        )

    def list(self) -> Sequence[Mirror]:
        resp = self.do_get("api/mirrors")

        mirrors = []
        for mdesc in resp.json():
            mirrors.append(
                self.mirror_from_response(mdesc)
            )
        return mirrors

    def create(self, name: str, archive_url: str, distribution: Optional[str] = None,
               components: Sequence[str] = None, arhitectures: Sequence[str] = None,
               ignoresignatures: Optional[bool] = False) -> Mirror:
        data = {}

        data["Name"] = name
        data["ArchiveURL"] = archive_url

        if distribution:
            data["Distribution"] = distribution
        if components:
            data["Components"] = components
        if arhitectures:
            data["Architectures"] = arhitectures
        if ignoresignatures:
            data["IgnoreSignatures"] = ignoresignatures

        resp = self.do_post("api/mirrors", json=data)

        return self.mirror_from_response(resp.json())

    def update(self, name: str, ignoresignatures: Optional[bool] = False,
               force: Optional[bool] = False, skipexistingpackages: Optional[bool] = False,
               maxtries: Optional[int] = 1) -> Task:
        body = {}

        if ignoresignatures:
            body["IgnoreSignatures"] = ignoresignatures
        if skipexistingpackages:
            body["SkipExistingPackages"] = skipexistingpackages
        if maxtries:
            body["MaxTries"] = maxtries

        resp = self.do_put("api/mirrors/%s" % quote(name), json=body)

        return TaskAPISection.task_from_response(resp.json())

    def drop(self, name: str, force: Optional[str] = None) -> Task:
        body = {}
        if force:
            body["force"] = force

        resp = self.do_delete("api/mirrors/%s" % quote(name), json=body)

        return TaskAPISection.task_from_response(resp.json())

    def show(self, name: str) -> Mirror:
        resp = self.do_get("api/mirrors/%s" % quote(name))

        return self.mirror_from_response(resp.json())

    def packages(self, name: str) -> Sequence[str]:
        resp = self.do_get("api/mirrors/%s/packages" % quote(name))

        return cast(List[str], resp.json())