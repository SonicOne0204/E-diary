import pytest


@pytest.mark.anyio(backends=["asyncio"])
async def test_create_school(client, db_session):
    response = await client.post(
        "/schools/",
        json={
            "name": "Test School",
            "short_name": "TS",
            "country": "France",
            "address": "123 Street",
            "grade_system": "letter",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test School"
    assert data["short_name"] == "TS"
    return data


@pytest.mark.anyio(backends=["asyncio"])
async def test_read_schools(client, db_session):
    response = await client.get("/schools/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(s["name"] == "Test School" for s in data)


@pytest.mark.anyio(backends=["asyncio"])
async def test_read_school_by_id(client, db_session):
    create = await client.post(
        "/schools/",
        json={
            "name": "Single School",
            "short_name": "SS",
            "country": "Germany",
            "address": "456 Avenue",
            "grade_system": "5numerical",
        },
    )
    school = create.json()
    print(str(school))
    school_id = school["id"]

    response = await client.get(f"/schools/{school_id}/")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == school_id
    assert data["name"] == "Single School"


@pytest.mark.anyio(backends=["asyncio"])
async def test_update_school(client, db_session):
    create = await client.post(
        "/schools/",
        json={
            "name": "Old Name",
            "short_name": "ON",
            "country": "Italy",
            "address": "789 Road",
            "grade_system": "letter",
        },
    )
    school = create.json()
    print(str(school))
    school_id = school["id"]

    response = await client.patch(
        f"/schools/{school_id}/",
        json={
            "name": "Updated Name",
            "short_name": "UN",
            "country": "Italy",
            "address": "789 Road",
            "grade_system": "letter",
        },
    )
    assert response.status_code == 200
    data = response.json()
    print(str(data))
    assert data["name"] == "Updated Name"
    assert data["short_name"] == "UN"


@pytest.mark.anyio(backends=["asyncio"])
async def test_delete_school(client, db_session):
    create = await client.post(
        "/schools/",
        json={
            "name": "To Delete",
            "short_name": "TD",
            "country": "Spain",
            "address": "1010 Plaza",
            "grade_system": "5numerical",
        },
    )
    school = create.json()
    print(str(school))
    school_id = school["id"]

    response = await client.delete(f"/schools/{school_id}/")
    assert response.status_code == 204

    get_response = await client.get(f"/schools/{school_id}/")
    assert get_response.status_code == 404
