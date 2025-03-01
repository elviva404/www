import dataclasses
import re
import typing

from . import i18n

PRIVATE_RE = re.compile(r"prv-\d+$")


@dataclasses.dataclass(frozen=True)
class ContentItem:
    content: str
    location: str


@dataclasses.dataclass(frozen=True)
class Frontmatter:
    title: str
    description: typing.Optional[str] = None
    category: typing.Optional[str] = None
    date: typing.Optional[str] = None
    image: typing.Optional[str] = None
    image_thumbnail: typing.Optional[str] = None
    image_caption: typing.Optional[str] = None
    tags: typing.List[str] = dataclasses.field(default_factory=list)
    tag: typing.Optional[str] = None


@dataclasses.dataclass(frozen=True)
class Page:
    permalink: str
    frontmatter: Frontmatter
    meta: typing.List["MetaTag"]
    html: str = ""
    content: str = ""

    @property
    def language(self) -> str:
        # '/en/posts/...' -> 'en'
        parts = self.permalink.split("/")
        return parts[1]

    @property
    def is_post(self) -> bool:
        return "/posts/" in self.permalink

    @property
    def is_category(self) -> bool:
        return "/category/" in self.permalink

    @property
    def is_private(self) -> bool:
        return PRIVATE_RE.search(self.permalink) is not None


class Index:
    """
    An in-memory container of pages.
    """

    def __init__(self) -> None:
        self._pages: typing.Dict[str, typing.List[Page]] = {}

    def set_pages(self, pages: typing.Dict[str, typing.List[Page]]) -> None:
        self._pages = pages

    def get_i18n_aware_pages(self, language: str = None) -> typing.List[Page]:
        if language is None:
            language = i18n.get_locale().language
        return self._pages[language]

    def get_post_pages(
        self,
        *,
        tag: str = None,
        category: str = None,
        limit: int = None,
    ) -> typing.List[Page]:
        posts = []

        for page in self.get_i18n_aware_pages():
            if not page.is_post:
                continue
            if page.is_private:
                continue
            if tag is not None and tag not in page.frontmatter.tags:
                continue
            if category is not None and page.frontmatter.category != category:
                continue
            posts.append(page)

        posts = sorted(
            posts, key=lambda page: page.frontmatter.date or "", reverse=True
        )

        return posts[:limit]

    def get_category_pages(self) -> typing.List[Page]:
        return [page for page in self.get_i18n_aware_pages() if page.is_category]


class MetaTag:
    def __init__(self, **attributes: typing.Optional[str]) -> None:
        self.attributes = attributes

    def __str__(self) -> str:
        attrs = " ".join(
            f'{key}="{value}"' for key, value in self.attributes.items() if value
        )
        return f"<meta {attrs}>"
