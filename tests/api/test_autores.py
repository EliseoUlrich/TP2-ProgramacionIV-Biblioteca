def test_create_autor_ok(client):
    res = client.post("/autores", json={"nombre": "Ernesto Sabato", "nacionalidad": "Argentina"})
    assert res.status_code == 201
    data = res.json()
    assert data["id"] == 1
    assert data["nombre"] == "Ernesto Sabato"
    assert data["nacionalidad"] == "Argentina"


def test_get_autores_ok(client, seed):
    res = client.get("/autores")
    assert res.status_code == 200
    assert len(res.json()) == 3


def test_get_autor_by_id_ok(client, seed):
    res = client.get("/autores/1")
    assert res.status_code == 200
    assert res.json()["nombre"] == "Jorge Luis Borges"


def test_get_autor_by_id_not_found(client):
    res = client.get("/autores/999")
    assert res.status_code == 404


def test_update_autor_put_ok(client, seed):
    res = client.put("/autores/1", json={"nombre": "J. L. Borges", "nacionalidad": "Argentina"})
    assert res.status_code == 200
    assert res.json()["nombre"] == "J. L. Borges"


def test_update_autor_patch_ok(client, seed):
    res = client.patch("/autores/1", json={"nombre": "Borges"})
    assert res.status_code == 200
    assert res.json()["nombre"] == "Borges"
    assert res.json()["nacionalidad"] == "Argentina"


def test_update_autor_not_found(client):
    assert client.put("/autores/999", json={"nombre": "X", "nacionalidad": "Y"}).status_code == 404
    assert client.patch("/autores/999", json={"nombre": "X"}).status_code == 404


def test_delete_autor_ok(client, seed):
    res = client.delete("/autores/1")
    assert res.status_code == 200
    assert client.get("/autores/1").status_code == 404


def test_delete_autor_not_found(client):
    assert client.delete("/autores/999").status_code == 404

