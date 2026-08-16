from math import radians, sin, cos, sqrt, atan2
import os
import httpx


GOOGLE_URL = "https://places.googleapis.com/v1/places:searchNearby"

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]


def distance_km(lat1, lon1, lat2, lon2):

    r = 6371.0

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2) ** 2
    )

    return round(
        r * 2 * atan2(
            sqrt(a),
            sqrt(1 - a)
        ),
        2
    )


def build_navigation_url(
    latitude,
    longitude
):
    return (
        "https://www.google.com/maps/dir/?api=1"
        f"&destination={latitude},{longitude}"
        "&travelmode=driving"
    )


def build_osm_navigation_url(
    latitude,
    longitude
):
    return (
        "https://www.openstreetmap.org/directions"
        f"?from=&to={latitude}%2C{longitude}"
    )


def classify_emergency_suitability(
    name="",
    tags=None,
    primary_type="hospital"
):

    tags = tags or {}

    text = " ".join([
        str(name),
        str(primary_type),
        str(tags.get("name", "")),
        str(tags.get("healthcare", "")),
        str(tags.get("amenity", "")),
        str(tags.get("emergency", "")),
        str(tags.get("healthcare:speciality", "")),
    ]).lower()

    score = 0
    reasons = []

    # Strong exclusions.
    excluded_terms = [
        "office of",
        "director of health",
        "health department",
        "administrative office",
        "clinic",
        "laboratory",
        "diagnostic centre",
        "diagnostic center",
        "dental clinic",
        "dental centre",
        "dental center",
        "dentistry",
        "pharmacy",
        "medical shop",
        "blood bank",
        "bloodbank",
        "dialysis centre",
        "dialysis center",
        "pathology lab",
        "pathology laboratory",
        "imaging centre",
        "imaging center"
    ]

    if any(term in text for term in excluded_terms):

        return {
            "emergency_suitable": False,
            "suitability_score": 0,
            "classification": "not_emergency_facility",
            "reasons": [
                "Facility appears to be a non-emergency medical facility."
            ]
        }

    # Explicit emergency information.
    emergency = str(
        tags.get("emergency", "")
    ).lower()

    if emergency in {
        "yes",
        "24_7",
        "24/7",
        "designated"
    }:

        score += 60

        reasons.append(
            "Emergency service is explicitly indicated by source data."
        )

    elif emergency in {
        "no",
        "none"
    }:

        score -= 60

        reasons.append(
            "Source data indicates no emergency service."
        )

    # General hospital.
    healthcare = str(
        tags.get("healthcare", "")
    ).lower()

    amenity = str(
        tags.get("amenity", "")
    ).lower()

    if healthcare == "hospital" or amenity == "hospital":

        score += 25

        reasons.append(
            "Facility is classified as a hospital."
        )

    # General hospital names.
    general_terms = [
        "general hospital",
        "multispeciality",
        "multi speciality",
        "multispecialty",
        "medical college",
        "teaching hospital",
        "government hospital",
        "district hospital",
        "community hospital"
    ]

    if any(term in text for term in general_terms):

        score += 15

        reasons.append(
            "Facility appears to provide broad hospital services."
        )

    # Specialist hospitals can still be useful,
    # but should not automatically outrank a general emergency hospital.
    specialist_terms = [
        "cardiac",
        "heart",
        "trauma",
        "orthopaedic",
        "orthopedic",
        "neurology",
        "neurosurgery",
        "children",
        "paediatric",
        "pediatric",
        "maternity",
        "women",
        "cancer",
        "oncology"
    ]

    if any(term in text for term in specialist_terms):

        score += 5

        reasons.append(
            "Facility appears to provide specialist medical care."
        )

    # Dental facilities are not general emergency hospitals.
    # Even if OSM happens to contain an emergency tag, do not
    # recommend a dental facility as a general emergency destination.
    if "dental" in text or "dentistry" in text:

        return {
            "emergency_suitable": False,
            "suitability_score": 0,
            "classification": "not_general_emergency_facility",
            "reasons": [
                "Dental facility is not a general emergency destination."
            ]
        }

    score = max(
        0,
        min(score, 100)
    )

    # Explicit emergency information is stronger than inferred
    # suitability from the facility name/type.
    explicit_emergency = emergency in {
        "yes",
        "24_7",
        "24/7",
        "designated"
    }

    is_hospital = (
        healthcare == "hospital"
        or amenity == "hospital"
        or primary_type == "hospital"
    )

    if explicit_emergency:
        classification = "emergency_ready"
        suitable = True
        emergency_status = "explicit"

    elif is_hospital and score >= 40:
        classification = "general_hospital"
        suitable = True
        emergency_status = "not_confirmed"

    elif score >= 20:
        classification = "specialist_facility"
        suitable = False
        emergency_status = "not_confirmed"

    else:
        classification = "not_preferred"
        suitable = False
        emergency_status = "not_confirmed"

    return {
        "emergency_suitable": suitable,
        "emergency_status": emergency_status,
        "suitability_score": score,
        "classification": classification,
        "reasons": reasons
    }


async def google_nearby_hospitals(
    latitude,
    longitude,
    radius=10000,
    max_results=20
):

    api_key = os.getenv(
        "GOOGLE_MAPS_API_KEY"
    )

    if not api_key:
        return None

    payload = {
        "includedTypes": ["hospital"],
        "maxResultCount": min(
            max_results,
            20
        ),
        "rankPreference": "DISTANCE",
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "radius": min(
                    radius,
                    50000
                )
            }
        },
        "regionCode": "IN"
    }

    headers = {
        "Content-Type":
            "application/json",

        "X-Goog-Api-Key":
            api_key,

        "X-Goog-FieldMask":
            "places.id,"
            "places.displayName,"
            "places.formattedAddress,"
            "places.location,"
            "places.googleMapsUri,"
            "places.primaryType"
    }

    try:

        async with httpx.AsyncClient(
            timeout=15
        ) as client:

            response = await client.post(
                GOOGLE_URL,
                json=payload,
                headers=headers
            )

        response.raise_for_status()

        data = response.json()

        hospitals = []

        for place in data.get(
            "places",
            []
        ):

            location = place.get(
                "location",
                {}
            )

            lat = location.get(
                "latitude"
            )

            lon = location.get(
                "longitude"
            )

            if lat is None or lon is None:
                continue

            name = (
                place.get(
                    "displayName",
                    {}
                ).get(
                    "text",
                    "Hospital"
                )
            )

            suitability = (
                classify_emergency_suitability(
                    name=name,
                    primary_type=place.get(
                        "primaryType",
                        "hospital"
                    )
                )
            )

            hospitals.append({

                "id":
                    place.get("id"),

                "name":
                    name,

                "address":
                    place.get(
                        "formattedAddress",
                        ""
                    ),

                "latitude":
                    lat,

                "longitude":
                    lon,

                "distance_km":
                    distance_km(
                        latitude,
                        longitude,
                        lat,
                        lon
                    ),

                "map_url":
                    place.get(
                        "googleMapsUri"
                    ),

                "navigation_url":
                    build_navigation_url(
                        lat,
                        lon
                    ),

                "type":
                    place.get(
                        "primaryType",
                        "hospital"
                    ),

                **suitability,

                "source":
                    "google_places"
            })

        hospitals = [
            x for x in hospitals
            if x["emergency_suitable"]
        ]

        hospitals.sort(
            key=lambda x: (
                -x["suitability_score"],
                x["distance_km"]
            )
        )

        return hospitals[:max_results]

    except Exception:

        return None


async def osm_nearby_hospitals(
    latitude,
    longitude,
    radius=10000,
    max_results=20
):

    radius = min(
        max(radius, 100),
        50000
    )

    query = f"""
    [out:json][timeout:20];

    (
      node["amenity"="hospital"]
        (around:{radius},{latitude},{longitude});

      way["amenity"="hospital"]
        (around:{radius},{latitude},{longitude});

      relation["amenity"="hospital"]
        (around:{radius},{latitude},{longitude});

      node["healthcare"="hospital"]
        (around:{radius},{latitude},{longitude});

      way["healthcare"="hospital"]
        (around:{radius},{latitude},{longitude});

      relation["healthcare"="hospital"]
        (around:{radius},{latitude},{longitude});
    );

    out center tags;
    """

    headers = {
        "User-Agent":
            "MedPulse/1.0 hospital-discovery",
        "Accept":
            "application/json"
    }

    for endpoint in OVERPASS_URLS:

        try:

            async with httpx.AsyncClient(
                timeout=25,
                headers=headers
            ) as client:

                response = await client.post(
                    endpoint,
                    data={
                        "data": query
                    }
                )

            response.raise_for_status()

            data = response.json()

            hospitals = []

            for element in data.get(
                "elements",
                []
            ):

                tags = element.get(
                    "tags",
                    {}
                )

                if element.get(
                    "type"
                ) == "node":

                    lat = element.get("lat")
                    lon = element.get("lon")

                else:

                    center = element.get(
                        "center",
                        {}
                    )

                    lat = center.get("lat")
                    lon = center.get("lon")

                if lat is None or lon is None:
                    continue

                name = tags.get(
                    "name",
                    "Hospital"
                )

                suitability = (
                    classify_emergency_suitability(
                        name=name,
                        tags=tags,
                        primary_type="hospital"
                    )
                )

                if not suitability[
                    "emergency_suitable"
                ]:

                    continue

                address_parts = [
                    tags.get(
                        "addr:housenumber",
                        ""
                    ),
                    tags.get(
                        "addr:street",
                        ""
                    ),
                    tags.get(
                        "addr:city",
                        ""
                    )
                ]

                address = ", ".join(
                    x for x in address_parts
                    if x
                )

                distance = distance_km(
                    latitude,
                    longitude,
                    lat,
                    lon
                )

                osm_type = element.get(
                    "type"
                )

                osm_id = element.get(
                    "id"
                )

                hospitals.append({

                    "id":
                        f"{osm_type}/{osm_id}",

                    "name":
                        name,

                    "address":
                        address,

                    "latitude":
                        lat,

                    "longitude":
                        lon,

                    "distance_km":
                        distance,

                    "map_url":
                        (
                            "https://www.openstreetmap.org/"
                            f"?mlat={lat}&mlon={lon}"
                            f"#map=18/{lat}/{lon}"
                        ),

                    "navigation_url":
                        build_navigation_url(
                            lat,
                            lon
                        ),

                    "osm_navigation_url":
                        build_osm_navigation_url(
                            lat,
                            lon
                        ),

                    "type":
                        "hospital",

                    **suitability,

                    "source":
                        "openstreetmap"
                })

            hospitals.sort(
                key=lambda x: (
                    0 if x["classification"] == "emergency_preferred" else 1,
                    x["distance_km"]
                )
            )

            return hospitals[:max_results]

        except Exception:
            continue

    return None



async def road_distance(
    origin_lat,
    origin_lon,
    destination_lat,
    destination_lon
):
    """
    Get actual driving distance using OSRM.

    Returns:
        {
            "distance_km": float,
            "duration_minutes": float,
            "source": "osrm"
        }

    Falls back to None if routing is unavailable.
    """

    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{origin_lon},{origin_lat};"
        f"{destination_lon},{destination_lat}"
    )

    try:

        async with httpx.AsyncClient(
            timeout=8
        ) as client:

            response = await client.get(
                url,
                params={
                    "overview": "false",
                    "steps": "false"
                }
            )

        response.raise_for_status()

        data = response.json()

        if data.get("code") != "Ok":
            return None

        routes = data.get("routes", [])

        if not routes:
            return None

        route = routes[0]

        return {
            "distance_km": round(
                route["distance"] / 1000,
                2
            ),
            "duration_minutes": round(
                route["duration"] / 60,
                1
            ),
            "source": "osrm"
        }

    except Exception:
        return None


async def add_road_distances(
    origin_lat,
    origin_lon,
    hospitals,
    max_routes=10
):
    """
    Replace straight-line distance with actual road distance
    for the nearest candidate hospitals.
    """

    candidates = sorted(
        hospitals,
        key=lambda h: h.get(
            "distance_km",
            999999
        )
    )[:max_routes]

    for hospital in candidates:

        lat = hospital.get("latitude")
        lon = hospital.get("longitude")

        if lat is None or lon is None:
            continue

        route = await road_distance(
            origin_lat,
            origin_lon,
            lat,
            lon
        )

        if route is None:
            hospital["distance_source"] = "geodesic"
            continue

        hospital["straight_line_distance_km"] = (
            hospital.get("distance_km")
        )

        hospital["distance_km"] = (
            route["distance_km"]
        )

        hospital["driving_distance_km"] = (
            route["distance_km"]
        )

        hospital["estimated_drive_minutes"] = (
            route["duration_minutes"]
        )

        hospital["distance_source"] = "osrm"

    hospitals.sort(
        key=lambda h: h.get(
            "distance_km",
            999999
        )
    )

    return hospitals


async def nearby_hospitals(
    latitude,
    longitude,
    radius=10000
):

    google_results = (
        await google_nearby_hospitals(
            latitude,
            longitude,
            radius
        )
    )

    if google_results is not None:

        return {
            "source":
                "google_places",

            "hospitals":
                google_results
        }

    osm_results = (
        await osm_nearby_hospitals(
            latitude,
            longitude,
            radius
        )
    )

    if osm_results is not None:

        osm_results = await add_road_distances(
            latitude,
            longitude,
            osm_results,
            max_routes=10
        )

        emergency_ready = [
            h for h in osm_results
            if h.get("classification")
            in (
                "emergency_preferred",
                "emergency_ready"
            )
        ]

        emergency_ready.sort(
            key=lambda h: (
                -h.get("suitability_score", 0),
                h.get("distance_km", 999999)
            )
        )

        return {
            "source":
                "openstreetmap",

            "hospitals":
                osm_results,

            "recommended_hospitals":
                emergency_ready[:5]
        }

    return {
        "source":
            "hospital_search_unavailable",

        "hospitals": []
    }


# ---------------------------------------------------------
# Emergency suitability layer
# ---------------------------------------------------------

EMERGENCY_KEYWORDS = (
    "emergency",
    "trauma",
    "trauma center",
    "trauma centre",
    "critical care",
    "multi speciality",
    "multi-speciality",
    "multispeciality",
    "medical college",
    "government hospital",
    "general hospital",
    "institute of medical sciences",
    "institute of medical science",
)

NON_EMERGENCY_KEYWORDS = (
    "clinic",
    "dental",
    "pharmacy",
    "diagnostic",
    "laboratory",
    "lab",
    "physiotherapy",
    "optical",
    "veterinary",
)


def hospital_suitability_score(hospital):
    """
    Heuristic emergency suitability ranking.

    IMPORTANT:
    This is a routing/ranking aid, not proof that a facility
    has an emergency department or trauma capability.
    """

    name = str(hospital.get("name", "")).lower()
    address = str(hospital.get("address", "")).lower()
    place_type = str(hospital.get("type", "")).lower()

    text = f"{name} {address} {place_type}"

    score = 0
    reasons = []

    if place_type in {
        "hospital",
        "medical_center",
        "medical_centre",
    }:
        score += 30
        reasons.append("hospital facility type")

    emergency_matches = [
        keyword
        for keyword in EMERGENCY_KEYWORDS
        if keyword in text
    ]

    if emergency_matches:
        score += min(50, len(emergency_matches) * 15)
        reasons.append(
            "emergency-capable terminology found"
        )

    non_emergency_matches = [
        keyword
        for keyword in NON_EMERGENCY_KEYWORDS
        if keyword in text
    ]

    if non_emergency_matches:
        score -= min(
            60,
            len(non_emergency_matches) * 30
        )
        reasons.append(
            "non-emergency facility terminology found"
        )

    distance = hospital.get("distance_km")

    if isinstance(distance, (int, float)):
        if distance <= 2:
            score += 20
        elif distance <= 5:
            score += 12
        elif distance <= 10:
            score += 5

    if score < 0:
        score = 0

    return score, reasons


def rank_emergency_hospitals(hospitals, limit=10):
    ranked = []

    for hospital in hospitals:
        score, reasons = hospital_suitability_score(
            hospital
        )

        item = dict(hospital)

        item["emergency_suitability_score"] = score
        item["suitability_reasons"] = reasons

        # Conservative classification.
        if score >= 60:
            suitability = "high"
        elif score >= 35:
            suitability = "moderate"
        else:
            suitability = "low"

        item["emergency_suitability"] = suitability

        ranked.append(item)

    ranked.sort(
        key=lambda x: (
            -x["emergency_suitability_score"],
            x.get("distance_km", 999999)
        )
    )

    return ranked[:limit]


def get_best_emergency_hospitals(
    hospitals,
    limit=5
):
    ranked = rank_emergency_hospitals(
        hospitals,
        limit=limit
    )

    suitable = [
        hospital
        for hospital in ranked
        if hospital["emergency_suitability"]
        in ("high", "moderate")
    ]

    return suitable[:limit]
