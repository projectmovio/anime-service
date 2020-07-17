import time
import uuid

import requests

from apitest.conftest import API_URL, BASE_HEADERS


def test_search():
    res = requests.get(f"{API_URL}/anime?search=Naruto", headers=BASE_HEADERS)

    assert res.status_code == 200
    item = res.json()[0]
    assert item["id"] == 20
    assert item["title"] == "Naruto"
    time.sleep(1)


def test_search_by_mal_id():
    res = requests.get(f"{API_URL}/anime?mal_id=20", headers=BASE_HEADERS)

    assert res.status_code == 200
    item = res.json()
    assert item["mal_id"] == 20
    assert item["title"] == "Naruto"
    time.sleep(1)


def test_get_anime_by_id():
    anime_id = str(uuid.uuid5(uuid.NAMESPACE_OID, "20"))
    res = requests.get(f"{API_URL}/anime/{anime_id}", headers=BASE_HEADERS)

    assert res.status_code == 200
    item = res.json()
    assert item["mal_id"] == 20
    assert item["title"] == "Naruto"
    time.sleep(1)


def test_get_anime_episodes():
    anime_id = str(uuid.uuid5(uuid.NAMESPACE_OID, "20"))
    res = requests.get(f"{API_URL}/anime/{anime_id}/episodes", headers=BASE_HEADERS)

    assert res.status_code == 200
    item = res.json()
    assert len(item["items"]) == 100
    assert item["items"][0]["episode_number"] == "220"
    assert item["items"][-1]["episode_number"] == "121"
    assert item["total"] == 220
    time.sleep(1)


def test_get_anime_episodes_with_changed_limit():
    anime_id = str(uuid.uuid5(uuid.NAMESPACE_OID, "20"))
    res = requests.get(f"{API_URL}/anime/{anime_id}/episodes?limit=10", headers=BASE_HEADERS)

    assert res.status_code == 200
    item = res.json()
    assert len(item["items"]) == 10
    assert item["items"][0]["episode_number"] == "220"
    assert item["items"][-1]["episode_number"] == "211"
    assert item["total"] == 220
    time.sleep(1)


def test_get_anime_episodes_with_changed_start_and_limit():
    anime_id = str(uuid.uuid5(uuid.NAMESPACE_OID, "20"))
    res = requests.get(f"{API_URL}/anime/{anime_id}/episodes?limit=10&start=2", headers=BASE_HEADERS)

    assert res.status_code == 200
    item = res.json()
    assert len(item["items"]) == 10
    assert item["items"][0]["episode_number"] == "210"
    assert item["items"][-1]["episode_number"] == "201"
    assert item["total"] == 220
    time.sleep(1)


def test_post_anime():
    res = requests.post(f"{API_URL}/anime?mal_id=20", headers=BASE_HEADERS)
    assert res.status_code == 202
    time.sleep(1)
