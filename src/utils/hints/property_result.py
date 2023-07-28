from typing import TypedDict, Literal


class PropertyResult(TypedDict):
    """Typings for results of this scrape process.

    Args:
        TypedDict: Type description lol.
    """

    building: Literal["oficina", "local", "bodega"]
    modality: Literal["ninguna", "arriendo", "venta"]
    neighborhood: str
    city: str
    price: str
    area: str
    rooms: str
    bathrooms: str
