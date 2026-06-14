# Maps our display station names to official NTES station codes
STATION_TO_CODE = {
    "New Delhi": "NDLS",
    "Mumbai Central": "BCT",
    "Howrah": "HWH",
    "Chennai Central": "MAS",
    "Bengaluru City": "SBC",
    "Secunderabad": "SC",
    "Ahmedabad": "ADI",
    "Jaipur": "JP",
    "Lucknow": "LKO",
    "Patna": "PNBE",
    "Bhopal": "BPL",
    "Chandigarh": "CDG",
    "Pune": "PUNE",
    "Kolkata": "KOAA",
    "Thiruvananthapuram": "TVC",
    "Guwahati": "GHY",
    "Bhubaneswar": "BBS",
    "Jodhpur": "JU",
    "Varanasi": "BSB",
    "Nagpur": "NGP",
    "Agra": "AGC",
    "Surat": "ST",
    "Indore": "INDB",
    "Coimbatore": "CBE",
    "Madurai": "MDU",
    "Visakhapatnam": "VSKP",
    "Ranchi": "RNC",
    "Dehradun": "DDN",
    "Amritsar": "ASR",
    "Mysuru": "MYS",
}

CODE_TO_STATION = {v: k for k, v in STATION_TO_CODE.items()}

NTES_STATIONS = {
    "NDLS", "BCT", "HWH", "MAS", "SBC", "SC", "ADI", "JP", "LKO", "PNBE",
    "BPL", "CDG", "PUNE", "KOAA", "TVC", "GHY", "BBS", "JU", "BSB", "NGP",
    "AGC", "ST", "INDB", "CBE", "MDU", "VSKP", "RNC", "DDN", "ASR", "MYS",
}

def get_code(station_name):
    return STATION_TO_CODE.get(station_name)

def get_name(station_code):
    return CODE_TO_STATION.get(station_code, station_code)
