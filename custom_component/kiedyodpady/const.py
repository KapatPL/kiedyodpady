DOMAIN = "kiedyodpady"

CONF_LOCALITY_ID = "locality_id"
CONF_STREET_ID = "street_id"
CONF_NUMBER = "number"
CONF_PROPERTY_TYPE = "property_type"
CONF_BUILDING_TYPE = "building_type"
CONF_ORIGIN = "origin"

DEFAULT_ORIGIN = "https://jozefow.kiedyodpady.pl"
DEFAULT_BUILDING_KIND = "zamieszkana_jednorodzinna"

WASTE_TYPES = {
    "01887640-c4e2-4ee4-a9eb-f15ac6ed1a82": "Bio",
    "01887642-b506-4f67-9db1-c14ff973d3a9": "Zielone",
    "01887640-9754-4439-b1f2-34cd3cbf2b6c": "Zmieszane",
    "01887643-ef73-43d7-81bd-fe8ac69e3721": "Metale i tworzywa sztuczne",
    "01887643-58ca-4988-a2d9-153ff5b76a2a": "Papier",
    "01887643-ae5a-4501-8ce7-207187937c58": "Szkło",
}

CONF_BUILDING_KIND = "building_kind"

BUILDING_KIND_OPTIONS = {
    "zamieszkana_jednorodzinna": {
        CONF_PROPERTY_TYPE: "Zamieszkana",
        CONF_BUILDING_TYPE: "Jednorodzinna",
        "label": "Zamieszkana - jednorodzinna",
    },
    "zamieszkana_wielorodzinna": {
        CONF_PROPERTY_TYPE: "Zamieszkana",
        CONF_BUILDING_TYPE: "Wielorodzinna",
        "label": "Zamieszkana - wielorodzinna",
    },
}
