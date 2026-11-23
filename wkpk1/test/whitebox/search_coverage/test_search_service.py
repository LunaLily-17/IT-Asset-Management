"""US-02 white-box service branches and side-effect invariants."""
import copy

from database import db_json
from services import asset_service


def test_wb01_service_handles_empty_database(client):
    assert asset_service.search_assets() == ([], 0)


def test_wb02_service_matches_identifier_and_copies_record(client, hardware):
    record = client.post('/assets', json=hardware).json()
    items, total = asset_service.search_assets(search=record['asset_id'])
    assert total == 1
    items[0]['title'] = 'CHANGED IN RESULT ONLY'
    assert db_json.DB['hardware_assets'][record['asset_id']]['title'] != 'CHANGED IN RESULT ONLY'


def test_wb03_service_filters_missing_manufacturer(client, software):
    client.post('/assets', json=software)
    assert asset_service.search_assets(manufacturer='Microsoft') == ([], 0)


def test_wb04_service_filters_model_and_location(client, hardware):
    client.post('/assets', json=hardware)
    assert asset_service.search_assets(model='Latitude', location='London') == ([], 0)


def test_wb05_service_filters_before_pagination(client, hardware):
    client.post('/assets', json=hardware)
    items, total = asset_service.search_assets(category='Hardware', limit=2, offset=5)
    assert items == [] and total == 1


def test_wb06_service_never_saves(client, hardware, monkeypatch):
    client.post('/assets', json=hardware)
    before = copy.deepcopy(db_json.DB)
    def disallow_save():
        raise AssertionError('Search must never persist records')
    monkeypatch.setattr(db_json, 'save_db', disallow_save)
    asset_service.search_assets(search='Dell')
    asset_service.get_asset(next(iter(db_json.DB['hardware_assets'])))
    assert db_json.DB == before
