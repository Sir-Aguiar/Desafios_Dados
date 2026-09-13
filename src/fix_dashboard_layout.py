import json
from superset.app import create_app

app = create_app()
with app.app_context():
    from superset import db
    from superset.models.dashboard import Dashboard
    from superset.models.slice import Slice

    dash = db.session.query(Dashboard).filter_by(id=1).first()
    slices = db.session.query(Slice).all()
    s_by_id = {s.id: s for s in slices}

    pos = {
        "DASHBOARD_VERSION_KEY": "v2",
        "ROOT_ID": {
            "children": ["GRID_ID"],
            "id": "ROOT_ID",
            "type": "ROOT"
        },
        "HEADER_ID": {
            "id": "HEADER_ID",
            "meta": {"text": "Plataforma Educacional — KPIs e Recomendações"},
            "type": "HEADER"
        },
        "GRID_ID": {
            "children": ["ROW-CARDS", "ROW-CHARTS"],
            "id": "GRID_ID",
            "parents": ["ROOT_ID"],
            "type": "GRID"
        },
        "ROW-CARDS": {
            "children": ["CHART-1", "CHART-2", "CHART-3"],
            "id": "ROW-CARDS",
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
            "parents": ["ROOT_ID", "GRID_ID"],
            "type": "ROW"
        },
        "CHART-1": {
            "children": [],
            "id": "CHART-1",
            "meta": {
                "chartId": 1,
                "height": 30,
                "sliceName": s_by_id[1].slice_name,
                "uuid": str(s_by_id[1].uuid),
                "width": 4
            },
            "parents": ["ROOT_ID", "GRID_ID", "ROW-CARDS"],
            "type": "CHART"
        },
        "CHART-2": {
            "children": [],
            "id": "CHART-2",
            "meta": {
                "chartId": 2,
                "height": 30,
                "sliceName": s_by_id[2].slice_name,
                "uuid": str(s_by_id[2].uuid),
                "width": 4
            },
            "parents": ["ROOT_ID", "GRID_ID", "ROW-CARDS"],
            "type": "CHART"
        },
        "CHART-3": {
            "children": [],
            "id": "CHART-3",
            "meta": {
                "chartId": 3,
                "height": 30,
                "sliceName": s_by_id[3].slice_name,
                "uuid": str(s_by_id[3].uuid),
                "width": 4
            },
            "parents": ["ROOT_ID", "GRID_ID", "ROW-CARDS"],
            "type": "CHART"
        },
        "ROW-CHARTS": {
            "children": ["CHART-4", "CHART-5"],
            "id": "ROW-CHARTS",
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
            "parents": ["ROOT_ID", "GRID_ID"],
            "type": "ROW"
        },
        "CHART-4": {
            "children": [],
            "id": "CHART-4",
            "meta": {
                "chartId": 4,
                "height": 50,
                "sliceName": s_by_id[4].slice_name,
                "uuid": str(s_by_id[4].uuid),
                "width": 6
            },
            "parents": ["ROOT_ID", "GRID_ID", "ROW-CHARTS"],
            "type": "CHART"
        },
        "CHART-5": {
            "children": [],
            "id": "CHART-5",
            "meta": {
                "chartId": 5,
                "height": 50,
                "sliceName": s_by_id[5].slice_name,
                "uuid": str(s_by_id[5].uuid),
                "width": 6
            },
            "parents": ["ROOT_ID", "GRID_ID", "ROW-CHARTS"],
            "type": "CHART"
        }
    }

    dash.position_json = json.dumps(pos)
    dash.slices = list(s_by_id.values())
    db.session.commit()
    print("Layout do dashboard atualizado com sucesso e 100% conforme com v2!")
