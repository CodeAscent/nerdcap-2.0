from app.stubs import revenue_stub, forest_stub, seiaa_stub, aptransco_stub, cadastral_stub, rtgs_stub


def get_all_stubs_status() -> dict:
    return {
        "revenue_department": {
            "name": "AP Revenue Department",
            "description": "Land ownership, title status, dispute records",
            "is_live": revenue_stub.IS_LIVE,
            "status": "live" if revenue_stub.IS_LIVE else "stub",
        },
        "forest_department": {
            "name": "AP Forest Department",
            "description": "Forest coverage, wildlife corridors, protected areas",
            "is_live": forest_stub.IS_LIVE,
            "status": "live" if forest_stub.IS_LIVE else "stub",
        },
        "seiaa_ap": {
            "name": "SEIAA-AP",
            "description": "EIA zones, CRZ boundaries, environmental clearance",
            "is_live": seiaa_stub.IS_LIVE,
            "status": "live" if seiaa_stub.IS_LIVE else "stub",
        },
        "aptransco": {
            "name": "APTRANSCO / DISCOMs",
            "description": "Grid infrastructure, substation proximity, transmission lines",
            "is_live": aptransco_stub.IS_LIVE,
            "status": "live" if aptransco_stub.IS_LIVE else "stub",
        },
        "cadastral_survey": {
            "name": "Cadastral Survey & Land Records",
            "description": "Boundary verification, area validation, survey numbers",
            "is_live": cadastral_stub.IS_LIVE,
            "status": "live" if cadastral_stub.IS_LIVE else "stub",
        },
        "rtgs": {
            "name": "RTGS Data Lake",
            "description": "Real-time governance sync endpoint",
            "is_live": rtgs_stub.IS_LIVE,
            "status": "live" if rtgs_stub.IS_LIVE else "stub",
        },
    }
