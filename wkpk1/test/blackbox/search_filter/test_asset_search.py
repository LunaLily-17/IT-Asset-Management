"""US-02 black-box equivalence partitions, decisions, boundaries, pagination."""
import copy
import json
from pathlib import Path

import pytest

from database import db_json


def seeded(client, hardware, software):
    hw1 = client.post('/assets', json=hardware)
    assert hw1.status_code == 201, hw1.text
    second = copy.deepcopy(hardware)
    second.update(title='HP Server', asset_type='Server', manufacturer='HP', model='ProLiant', serial_number='SN-002', location='London Office')
    hw2 = client.post('/assets', json=second)
    assert hw2.status_code == 201, hw2.text
    sw1 = client.post('/assets', json=software)
    assert sw1.status_code == 201, sw1.text
    return hw1.json(), hw2.json(), sw1.json()


def test_bb01_empty_inventory_returns_200(client):
    response = client.get('/assets')
    assert response.status_code == 200
    assert response.json() == []
    assert response.headers['X-Total-Count'] == '0'


def test_bb02_list_all(client, hardware, software):
    seeded(client, hardware, software)
    response = client.get('/assets')
    assert len(response.json()) == 3
    assert response.headers['X-Total-Count'] == '3'


@pytest.mark.parametrize('category,expected', [('Hardware', 2), ('Software', 1)])
def test_bb03_category_filter(client, hardware, software, category, expected):
    seeded(client, hardware, software)
    response = client.get('/assets', params={'category': category})
    assert response.status_code == 200
    assert len(response.json()) == expected
    assert all(item['category'] == category for item in response.json())


def test_bb04_status_case_insensitive(client, hardware, software):
    seeded(client, hardware, software)
    assert len(client.get('/assets', params={'status': 'available'}).json()) == 3


def test_bb05_unknown_status_no_matches(client, hardware, software):
    seeded(client, hardware, software)
    assert client.get('/assets', params={'status': 'retired'}).json() == []


def test_bb06_location_case_insensitive_substring(client, hardware, software):
    seeded(client, hardware, software)
    result = client.get('/assets', params={'location': 'it off'}).json()
    assert len(result) == 1 and result[0]['category'] == 'Hardware'


def test_bb07_manufacturer_filter_hw_only(client, hardware, software):
    seeded(client, hardware, software)
    result = client.get('/assets', params={'manufacturer': 'dElL'}).json()
    assert len(result) == 1 and result[0]['manufacturer'] == 'Dell'


def test_bb08_model_filter_hw_only(client, hardware, software):
    seeded(client, hardware, software)
    result = client.get('/assets', params={'model': 'lati'}).json()
    assert len(result) == 1 and result[0]['model'] == 'Latitude 5450'


def test_bb09_combined_filters_and_logic(client, hardware, software):
    seeded(client, hardware, software)
    result = client.get('/assets', params={
        'category': 'Hardware', 'status': 'Available', 'location': 'IT',
        'manufacturer': 'dell', 'model': 'latitude', 'search': 'SN-001'
    }).json()
    assert len(result) == 1 and result[0]['serial_number'] == 'SN-001'


def test_bb10_nonmatching_combination(client, hardware, software):
    seeded(client, hardware, software)
    assert client.get('/assets', params={'manufacturer': 'Dell', 'location': 'London'}).json() == []


@pytest.mark.parametrize('term,category', [('SN-001', 'Hardware'), ('INSTALL-001', 'Software'), ('visual studio', 'Software'), ('proliant', 'Hardware'), ('latitude', 'Hardware')])
def test_bb11_search_fields(client, hardware, software, term, category):
    seeded(client, hardware, software)
    result = client.get('/assets', params={'search': term}).json()
    assert len(result) == 1 and result[0]['category'] == category


def test_bb12_unknown_id_404(client):
    assert client.get('/assets/HW-DOESNOTEXIST').status_code == 404


@pytest.mark.parametrize('category', ['Hardware', 'Software'])
def test_bb13_get_existing_by_id(client, hardware, software, category):
    records = seeded(client, hardware, software)
    match = next(item for item in records if item['category'] == category)
    response = client.get(f"/assets/{match['asset_id']}")
    assert response.status_code == 200
    assert response.json()['asset_id'] == match['asset_id']


def test_bb14_pagination_sorted_and_count(client, hardware, software):
    seeded(client, hardware, software)
    all_ids = [asset['asset_id'] for asset in client.get('/assets').json()]
    assert all_ids == sorted(all_ids)
    first = client.get('/assets', params={'limit': 1, 'offset': 0})
    second = client.get('/assets', params={'limit': 1, 'offset': 1})
    assert [first.json()[0]['asset_id'], second.json()[0]['asset_id']] == all_ids[:2]
    assert first.headers['X-Total-Count'] == '3'
    assert first.headers['X-Limit'] == '1'
    assert second.headers['X-Offset'] == '1'


def test_bb15_pagination_beyond_end(client, hardware, software):
    seeded(client, hardware, software)
    response = client.get('/assets', params={'offset': 100})
    assert response.status_code == 200 and response.json() == []
    assert response.headers['X-Total-Count'] == '3'


@pytest.mark.parametrize('parameters', [{'limit': 0}, {'limit': 101}, {'offset': -1}, {'limit': 'bad'}, {'category': 'Furniture'}, {'location': ''}, {'search': ''}])
def test_bb16_invalid_parameters_422(client, parameters):
    assert client.get('/assets', params=parameters).status_code == 422


def test_bb17_search_does_not_mutate_disk_or_memory(client, hardware, software):
    seeded(client, hardware, software)
    before = copy.deepcopy(db_json.DB)
    file_before = Path(db_json.DB_FILE_PATH).read_bytes()
    client.get('/assets', params={'category': 'Hardware', 'search': 'Dell'})
    for asset_id in [record['asset_id'] for record in before['hardware_assets'].values()]:
        assert client.get(f'/assets/{asset_id}').status_code == 200
    assert db_json.DB == before
    assert Path(db_json.DB_FILE_PATH).read_bytes() == file_before


def test_bb18_no_secret_or_assignment_fields(client, hardware, software):
    hw, _, sw = seeded(client, hardware, software)
    for record in db_json.DB['hardware_assets'].values():
        record['api_token'] = 'SECRET'
        record['internal_note'] = 'SECRET'
    for record in db_json.DB['software_assets'].values():
        record['licence_key'] = 'SECRET'
        record['password'] = 'SECRET'
    responses = [client.get('/assets').json(), [client.get(f"/assets/{hw['asset_id']}").json(), client.get(f"/assets/{sw['asset_id']}").json()]]
    for items in responses:
        for item in items:
            assert 'SECRET' not in json.dumps(item)
            assert 'assigned_employee_id' not in item
            assert 'installation_id' not in item


def test_bb19_filter_software_with_manufacturer_yields_empty(client, hardware, software):
    seeded(client, hardware, software)
    assert client.get('/assets', params={'category': 'Software', 'manufacturer': 'Microsoft'}).json() == []


def test_bb20_whitespace_query_and_no_match(client, hardware, software):
    seeded(client, hardware, software)
    assert client.get('/assets', params={'search': 'unlikely string'}).json() == []
