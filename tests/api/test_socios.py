def test_create_socio_ok(client):
    body = {"nombre": "Lucía Méndez", "email": "lmendez@email.com", "activo": True}
    res = client.post("/socios", json=body)
    assert res.status_code == 201
    data = res.json()
    assert data["nombre"] == "Lucía Méndez"
    assert data["email"] == "lmendez@email.com"
    assert data["activo"] is True


def test_create_socio_email_duplicado_409(client, seed):
    body = {"nombre": "Otra Persona", "email": "mgomez@email.com", "activo": True}
    res = client.post("/socios", json=body)
    assert res.status_code == 409


def test_get_socios_ok(client, seed):
    res = client.get("/socios")
    assert res.status_code == 200
    assert len(res.json()) == 3


def test_get_socio_by_id_ok_and_not_found(client, seed):
    res = client.get("/socios/1")
    assert res.status_code == 200
    assert res.json()["email"] == "mgomez@email.com"

    assert client.get("/socios/999").status_code == 404


def test_update_socio_put_and_patch_ok(client, seed):
    res_put = client.put(
        "/socios/1",
        json={"nombre": "Martina G.", "email": "mgomez@email.com", "activo": True},
    )
    assert res_put.status_code == 200
    assert res_put.json()["nombre"] == "Martina G."

    res_patch = client.patch("/socios/1", json={"activo": False})
    assert res_patch.status_code == 200
    assert res_patch.json()["activo"] is False


def test_update_socio_email_duplicado_409(client, seed):
    res = client.patch("/socios/2", json={"email": "mgomez@email.com"})
    assert res.status_code == 409


def test_update_socio_not_found(client):
    body = {"nombre": "X", "email": "x@email.com", "activo": True}
    assert client.put("/socios/999", json=body).status_code == 404
    assert client.patch("/socios/999", json={"activo": False}).status_code == 404


def test_delete_socio_ok_and_not_found(client, seed):
    assert client.delete("/socios/3").status_code == 200
    assert client.get("/socios/3").status_code == 404
    assert client.delete("/socios/999").status_code == 404


def test_delete_socio_con_prestamo_activo_409(client, seed):
    res_prestamo = client.post("/prestamos", json={"socio_id": 1, "libro_id": 1})
    prestamo_id = res_prestamo.json()["id"]

    # Mientras el socio tenga préstamos activos no se puede borrar
    assert client.delete("/socios/1").status_code == 409

    # Una vez devuelto el préstamo, sí se permite borrar al socio
    client.post(f"/prestamos/{prestamo_id}/devolucion")
    assert client.delete("/socios/1").status_code == 200

