from typing import TypedDict, NotRequired

class ArtDict(TypedDict, total=False):
    poster: str
    thumb: str
    square: str
    fanart: str
    banner: str

class FileDict(TypedDict):
    fileId: str
    releaseTitle: str
    torrentHash: NotRequired[str]

class NFODict(TypedDict):
    title: str
    cleantitle: str
    shorttitle: str
    genre: str
    studio: str
    thesportsdbid: str
    year: str
    releasedate: str
    art: ArtDict
    mpaa: NotRequired[str]
    showtitle: NotRequired[str]
    episode: NotRequired[str]
    releasename: NotRequired[str]
    torrenthash: NotRequired[str]

