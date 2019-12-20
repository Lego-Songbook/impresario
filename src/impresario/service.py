"""
Check the consistency among files.
"""
from datetime import date
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Mapping, Sequence

import attr
import yaml

SERVICE_POST_TEMPLATE = """---
layout: past-service
title: {0} 赞美安排
---
"""


@attr.s(auto_attribs=True)
class Service:
    """Wrapper for service data."""

    date: date
    lead_singer: str = None
    instrumentation: Sequence[Mapping[str, str]] = None
    songs: Sequence[str] = None
    vocals: Sequence[str] = None

    @property
    def file_name(self):
        return f"{self.date.isoformat()}.md"

    @property
    def file_content(self):
        return SERVICE_POST_TEMPLATE.format(self.date.isoformat())

    @classmethod
    def from_dict(cls, source: Mapping[str, Any]) -> "Service":
        return cls(
            date=source["date"],
            lead_singer=source.get("lead_singer", None),
            vocals=source.get("vocals", None),
            instrumentation=source.get("instrumentation", None),
            songs=source.get("songs", None),
        )

    @classmethod
    def from_list(cls, source: Sequence[Mapping[str, Any]]) -> List["Service"]:
        return [cls.from_dict(data) for data in source]

    @classmethod
    def from_yaml(cls, source_document: str) -> List["Service"]:
        """Get all services from ``services.yaml``."""
        with open(source_document, "r", encoding="utf-8") as stream:
            return Service.from_list(yaml.load(stream, Loader=yaml.Loader))

    def post_exists(self, post_dir: str) -> bool:
        service_post = Path(post_dir) / self.file_name
        return service_post.exists()

    def create_post(self, post_dir: str) -> bool:
        """Create a post, and write the content."""
        if self.post_exists(post_dir):
            print(f"{self.file_name} already exists in {post_dir}.")
            return True
        service_post = Path(post_dir) / self.file_name
        service_post.touch(exist_ok=False)
        service_post.write_text(self.file_content)
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date,
            "lead_singer": self.lead_singer,
            "vocals": self.vocals,
            "instrumentation": self.instrumentation,
            "songs": self.songs,
        }

    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict(), allow_unicode=True, line_break="\n")

    def write_yaml(self, target_document: str) -> bool:
        """Append the service info to the end of a yaml document."""
        with open(target_document, "r", encoding="utf-8") as stream:
            services_dict = yaml.load(stream, Loader=yaml.Loader)

        services_dict.append(self.to_dict())

        with open(target_document, "w", encoding="utf-8") as stream:
            stream.write(yaml.dump(services_dict, allow_unicode=True, line_break="\n"))

        return True

    def check_post_content(self, post_dir: str) -> bool:
        """Check if the post's content is correct."""
        if not self.post_exists(post_dir):
            return False
        else:
            post = Path(post_dir) / self.file_name
            with post.open("w", encoding="utf-8") as file:
                return file.read() == self.file_content

    def sync_post_content(self, post_dir: str) -> bool:
        """If the post content is incorrect, then write the correct content."""
        if self.post_exists(post_dir):
            if self.check_post_content(post_dir):
                return True
            else:
                service_post = Path(post_dir) / self.file_name
                service_post.write_text(self.file_content)
        else:
            self.create_post(post_dir)
            return True


def check_services(service_yaml, posts) -> bool:
    """Make sure that each service has a post."""
    services = Service.from_yaml(service_yaml)
    for service in services:
        if not service.post_exists(posts):
            service.create_post(posts)

    return True


def check_songs():
    """Make sure that all songs mentioned in the services are listed in
    ``songs.csv``.
    """
    pass


if __name__ == "__main__":
    SERVICES_YAML = "D:\Documents\Python Code Library\lego-songbook-new\lego-songbook\_data\past_services.yaml"
    SERVICE_POSTS = (
        "D:\Documents\Python Code Library\lego-songbook-new\lego-songbook\past-services"
    )
    service = Service(date=date(2019, 12, 29), lead_singer="Kip")
    service.create_post(SERVICE_POSTS)
    service.write_yaml(SERVICES_YAML)
