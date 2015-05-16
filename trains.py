def find(func, dicts):
    for dikt in dicts:
        if func(dikt):
            return dikt

TRAIN_TYPES = {
    '0': 'Light engines',
    '1': 'Fast Passenger/Postal/Test',
    '2': 'Slow Passenger/Driver Training',
    '3': 'Test/Priority ECS/Autumn Rail head treatment',
    '4': 'Freight < 75mph',
    '5': 'Empty Coaching Stock (ECS)',
    '6': 'Freight < 60mph',
    '7': 'Freight < 45mph',
    '8': 'Freight < 35mph',
    '9': 'Express inter-regional and intl'
}

TOC_DATA = [
    {"company_name":"Abellio Greater Anglia","business_code":"EB","numeric_code":"21","atoc_code":"LE"},
    {"company_name":"Arriva Trains Wales","business_code":"HL","numeric_code":"71","atoc_code":"AW"},
    {"company_name":"c2c","business_code":"HT","numeric_code":"79","atoc_code":"CC"},
    {"company_name":"Caledonian Sleeper","business_code":"ES","numeric_code":"60","atoc_code":"CS"},
    {"company_name":"Chiltern Railway","business_code":"HO","numeric_code":"74","atoc_code":"CH"},
    {"company_name":"CrossCountry","business_code":"EH","numeric_code":"27","atoc_code":"XC"},
    {"company_name":"Crossrail","business_code":"EX","numeric_code":"33","atoc_code":"XR"},
    {"company_name":"Devon and Cornwall Railway","business_code":"EN","numeric_code":"34","atoc_code":"DC"},
    {"company_name":"East Midlands Trains","business_code":"EM","numeric_code":"28","atoc_code":"EM"},
    {"company_name":"East Coast","business_code":"HB","numeric_code":"61","atoc_code":"GR"},
    {"company_name":"Eurostar","business_code":"GA","numeric_code":"06","atoc_code":"ES"},
    {"company_name":"First Capital Connect (defunct)","business_code":"EG","numeric_code":"26","atoc_code":"FC"},
    {"company_name":"First Great Western","business_code":"EF","numeric_code":"25","atoc_code":"GW"},
    {"company_name":"First Hull Trains","business_code":"PF","numeric_code":"55","atoc_code":"HT"},
    {"company_name":"First Scotrail","business_code":"HA","numeric_code":"60","atoc_code":"SR"},
    {"company_name":"First Transpennine Express","business_code":"EA","numeric_code":"20","atoc_code":"TP"},
    {"company_name":"Gatwick Express","business_code":"HV","numeric_code":"81","atoc_code":"GX"},
    {"company_name":"GB Railfreight","business_code":"PE","numeric_code":"54","atoc_code":"ZZ"},
    {"company_name":"Grand Central","business_code":"EC","numeric_code":"22","atoc_code":"GC"},
    {"company_name":"Govia Thameslink Railway (Great Northern)","business_code":"ET","numeric_code":"88","atoc_code":"GN"},
    {"company_name":"Govia Thameslink Railway (Thameslink)","business_code":"ET","numeric_code":"88","atoc_code":"TL"},
    {"company_name":"Heathrow Connect","business_code":"EE","numeric_code":"24","atoc_code":"HC"},
    {"company_name":"Heathrow Express","business_code":"HM","numeric_code":"86","atoc_code":"HX"},
    {"company_name":"Island Lines","business_code":"HZ","numeric_code":"85","atoc_code":"IL"},
    {"company_name":"London Midland","business_code":"EJ","numeric_code":"29","atoc_code":"LM"},
    {"company_name":"London Overground","business_code":"EK","numeric_code":"30","atoc_code":"LO"},
    {"company_name":"LUL Bakerloo Line","business_code":"XC","numeric_code":"91","atoc_code":"LT"},
    {"company_name":"LUL District Line – Wimbledon","business_code":"XB","numeric_code":"90","atoc_code":"LT"},
    {"company_name":"LUL District Line – Richmond","business_code":"XE","numeric_code":"93","atoc_code":"LT"},
    {"company_name":"Merseyrail","business_code":"HE","numeric_code":"64","atoc_code":"ME"},
    {"company_name":"Nexus (Tyne & Wear Metro)","business_code":"PG","numeric_code":"56","atoc_code":"TW"},
    {"company_name":"North Yorkshire Moors Railway","business_code":"PR","numeric_code":"51","atoc_code":"NY"},
    {"company_name":"Northern Rail","business_code":"ED","numeric_code":"23","atoc_code":"NT"},
    {"company_name":"South West Trains","business_code":"HY","numeric_code":"84","atoc_code":"SW"},
    {"company_name":"Southeastern","business_code":"HU","numeric_code":"80","atoc_code":"SE"},
    {"company_name":"Southern","business_code":"HW","numeric_code":"82","atoc_code":"SN"},
    {"company_name":"Virgin Trains","business_code":"HF","numeric_code":"65","atoc_code":"VT"},
    {"company_name":"West Coast Railway Co.","business_code":"PA","numeric_code":"50","atoc_code":"WR"}
]


def get_train_info(message):
    info = {}
    headcode = message['train_id'][2:6]
    train_type = headcode[0]
    info['train_type'] = TRAIN_TYPES[train_type]

    info['operator'] = find(lambda o: o['numeric_code'] == message['toc_id'], TOC_DATA)['company_name']
    return info
