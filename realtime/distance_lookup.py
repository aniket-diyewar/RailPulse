import re

ROUTES = [
    ("New Delhi", "Mumbai Central", 1384), ("New Delhi", "Howrah", 1450),
    ("Mumbai Central", "Chennai Central", 1200), ("Howrah", "Chennai Central", 1660),
    ("New Delhi", "Bengaluru City", 2100), ("Mumbai Central", "Bengaluru City", 980),
    ("New Delhi", "Lucknow", 550), ("New Delhi", "Jaipur", 300),
    ("Mumbai Central", "Ahmedabad", 520), ("Howrah", "Patna", 530),
    ("Chennai Central", "Bengaluru City", 350), ("New Delhi", "Chandigarh", 260),
    ("Mumbai Central", "Pune", 180), ("Howrah", "Guwahati", 1010),
    ("New Delhi", "Varanasi", 820), ("Bengaluru City", "Thiruvananthapuram", 720),
    ("Mumbai Central", "Bhopal", 780), ("New Delhi", "Nagpur", 1090),
    ("Howrah", "Bhubaneswar", 440), ("Jaipur", "Jodhpur", 330),
    ("Nagpur", "Mumbai Central", 800), ("Nagpur", "Secunderabad", 500),
    ("Nagpur", "Bhopal", 300), ("Nagpur", "Chennai Central", 1100),
    ("New Delhi", "Agra", 220), ("Mumbai Central", "Surat", 260),
    ("Indore", "Bhopal", 190), ("Chennai Central", "Coimbatore", 500),
    ("Chennai Central", "Madurai", 460), ("Howrah", "Ranchi", 420),
    ("Visakhapatnam", "Howrah", 880), ("New Delhi", "Dehradun", 310),
    ("New Delhi", "Amritsar", 450), ("Bengaluru City", "Mysuru", 140),
    ("Pune", "Secunderabad", 560), ("Ahmedabad", "Surat", 230),
    ("Jaipur", "Agra", 240), ("Lucknow", "Varanasi", 280),
    ("Secunderabad", "Chennai Central", 650), ("New Delhi", "Indore", 800),
    ("Mumbai Central", "Indore", 590), ("Howrah", "Visakhapatnam", 880),
    ("Chennai Central", "Mysuru", 500), ("Secunderabad", "Bengaluru City", 610),
    ("Pune", "Mumbai Central", 180), ("Kolkata", "Howrah", 10),
]

_route_map = {}
for a, b, d in ROUTES:
    key = frozenset((a, b))
    _route_map[key] = d

STATION_NAMES = {
    "New Delhi", "Mumbai Central", "Howrah", "Chennai Central", "Bengaluru City",
    "Secunderabad", "Ahmedabad", "Jaipur", "Lucknow", "Patna",
    "Bhopal", "Chandigarh", "Pune", "Kolkata", "Thiruvananthapuram",
    "Guwahati", "Bhubaneswar", "Jodhpur", "Varanasi", "Nagpur",
    "Agra", "Surat", "Indore", "Coimbatore", "Madurai",
    "Visakhapatnam", "Ranchi", "Dehradun", "Amritsar", "Mysuru",
}

_SUFFIXES = re.compile(
    r"\s+(jn|junc|junction|hlt|halt|cant|cantt|central|terminus|station|court|road|gate|town|city|rs|railway\s+station|stn)\.?$",
    re.IGNORECASE,
)

_SPECIAL = {
    "puratchi thalaivar dr. mgr ctl chennai": "Chennai Central",
    "puratchi thalaivar dr. mgr central": "Chennai Central",
    "mgrs chennai central": "Chennai Central",
    "smvt bengaluru": "Bengaluru City",
    "smvb bengaluru": "Bengaluru City",
    "smvt bengaluru": "Bengaluru City",
    "krantivira sangolli rayanna railway station": "Bengaluru City",
    "ksr bengaluru": "Bengaluru City",
    "chhatrapati shivaji maharaj terminus": "Mumbai Central",
    "csmt": "Mumbai Central",
    "cst": "Mumbai Central",
    "hazrat nizamuddin": "New Delhi",
    "h nizamuddin": "New Delhi",
    "nizamuddin": "New Delhi",
    "new delhi": "New Delhi",
}

_normalized = {}
for name in STATION_NAMES:
    key = name.lower().strip()
    _normalized[key] = name
    _normalized[key.replace("central", "").strip()] = name
    _normalized[key.replace("city", "").strip()] = name

def _clean(name):
    name = name.lower().strip()
    name = name.replace("  ", " ")
    name = _SUFFIXES.sub("", name)
    name = re.sub(r"[^a-z0-9\s]", "", name)
    name = name.strip()
    return name

def resolve(name):
    if not name:
        return name
    key = name.lower().strip()
    if key in _SPECIAL:
        return _SPECIAL[key]
    cleaned = _clean(name)
    if cleaned in _SPECIAL:
        return _SPECIAL[cleaned]
    if cleaned in _normalized:
        return _normalized[cleaned]
    for short, full in sorted(_normalized.items(), key=lambda x: -len(x[0])):
        if cleaned in short or short in cleaned:
            return full
    return name

def lookup_distance(from_name, to_name):
    a = resolve(from_name)
    b = resolve(to_name)
    key = frozenset((a, b))
    return _route_map.get(key)
