"""
GitLab API:
https://docs.gitlab.com/ee/api/lint.html
"""

from typing import Any

from gitlab.base import RESTObject
from gitlab.cli import register_custom_action
from gitlab.exceptions import GitlabCiLintError
from gitlab.mixins import CreateMixin, GetWithoutIdMixin
from gitlab.types import RequiredOptional

__all__ = ["CiLint", "CiLintManager", "ProjectCiLint", "ProjectCiLintManager"]


class CiLint(RESTObject):
    _id_attr = None


class CiLintManager(CreateMixin[CiLint]):
    _path = "/ci/lint"
    _obj_cls = CiLint
    _create_attrs = RequiredOptional(
        required=("content",), optional=("include_merged_yaml", "include_jobs")
    )

    @register_custom_action(
        cls_names="CiLintManager",
        required=("content",),
        optional=("include_merged_yaml", "include_jobs"),
    )
    def validate(self, *args: Any, **kwargs: Any) -> None:
        """Raise an error if the CI Lint results are not valid.

        This is a custom python-gitlab method to wrap lint endpoints."""
        result = self.create(*args, **kwargs)

        if result.status != "valid":
            message = ",\n".join(result.errors)
            raise GitlabCiLintError(message)


class ProjectCiLint(RESTObject):
    _id_attr = None


class ProjectCiLintManager(
    GetWithoutIdMixin[ProjectCiLint], CreateMixin[ProjectCiLint]
):
    _path = "/projects/{project_id}/ci/lint"
    _obj_cls = ProjectCiLint
    _from_parent_attrs = {"project_id": "id"}
    _optional_get_attrs = ("dry_run", "include_jobs", "ref")
    _create_attrs = RequiredOptional(
        required=("content",), optional=("dry_run", "include_jobs", "ref")
    )

    @register_custom_action(
        cls_names="ProjectCiLintManager",
        required=("content",),
        optional=("dry_run", "include_jobs", "ref"),
    )
    def validate(self, *args: Any, **kwargs: Any) -> None:
        """Raise an error if the Project CI Lint results are not valid.

        This is a custom python-gitlab method to wrap lint endpoints."""
        result = self.create(*args, **kwargs)

        if not result.valid:
            message = ",\n".join(result.errors)
            raise GitlabCiLintError(message)
