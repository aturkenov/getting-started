def ll2geom(
    latitude: float = ...,
    longitude: float = ...,
) -> str:
    geom = ...
    if latitude is ...:
        latitude = 0
    if longitude is ...:
        longitude = 0
    if any((latitude, longitude)):
        geom = f'POINT({latitude} {longitude})'
    return geom
