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
    ("architectures", Sequence[str],)
])


class MirrorAPISection(BaseAPIClient):
    @staticmethod
    def mirror_from_response(api_response: Dict[str, Union[str, None]]) -> Mirror:
        return Mirror(
            name=api_response["Name"],
            archive_root=api_response["ArchiveRoot"],
            distribution=api_response["Distribution"],
            components=cast(Sequence[str], api_response["Components"]),
            architectures=cast(Sequence[str], api_response["Architectures"]),
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
               filter: Optional[str] = None, components: Sequence[str] = None,
               architectures: Sequence[str] = None, keyrings: Sequence[str] = None,
               with_sources: Optional[bool] = False, with_udebs: Optional[bool] = False,
               with_installer: Optional[bool] = False, filter_with_deps: Optional[bool] = False,
               force_components: Optional[bool] = False, ignore_signatures: Optional[bool] = False) -> Mirror:
        data = {}

        data["Name"] = name
        data["ArchiveURL"] = archive_url

        if distribution:
            data["Distribution"] = distribution
        if filter:
            data["Filter"] = filter
        if components:
            data["Components"] = components
        if architectures:
            data["Architectures"] = architectures
        if keyrings:
            data["Keyrings"] = keyrings
        if with_sources:
            data["DownloadSources"] = with_sources
        if with_udebs:
            data["DownloadUdebs"] = with_udebs
        if with_installer:
            data["DownloadInstaller"] = with_installer
        if filter_with_deps:
            data["FilterWithDeps"] = filter_with_deps
        if force_components:
            data["SkipComponentCheck"] = force_components
        if ignore_signatures:
            data["IgnoreSignatures"] = ignore_signatures

        resp = self.do_post("api/mirrors", json=data)

        return self.mirror_from_response(resp.json())

    def update(self, name: str, archive_url: Optional[str] = None,
               filter: Optional[str] = None, architectures: Sequence[str] = None, 
               components: Sequence[str] = None, keyrings: Sequence[str] = None,
               filter_with_deps: Optional[bool] = None, with_sources: Optional[bool] = None,
               with_udebs: Optional[bool] = None, force_components: Optional[bool] = None,
               ignore_checksums: Optional[bool] = None, ignore_signatures: Optional[bool] = None,
               force: Optional[bool] = None, skip_existing_packages: Optional[bool] = None,
               max_tries: Optional[int] = 1) -> Task:
        body = {}

        if archive_url:
            body["ArchiveURL"] = archive_url
        if filter:
            body["Filter"] = filter
        if architectures:
            body["Architectures"] = architectures
        if components:
            body["Components"] = components
        if keyrings:
            body["Keyrings"] = keyrings
        if filter_with_deps:
            body["FilterWithDeps"] = filter_with_deps
        if with_sources:
            body["DownloadSources"] = with_sources
        if with_udebs:
            body["DownloadUdebs"] = with_udebs
        if force_components:
            body["SkipComponentCheck"] = force_components
        if ignore_checksums:
            body["IgnoreChecksums"] = ignore_checksums
        if ignore_signatures:
            body["IgnoreSignatures"] = ignore_signatures
        if force:
            body["ForceUpdate"] = force
        if skip_existing_packages:
            body["SkipExistingPackages"] = skip_existing_packages
        if max_tries:
            body["MaxTries"] = max_tries

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