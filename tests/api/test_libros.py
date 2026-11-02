def test_create_libro_ok(client):
    body = {"titulo": "El Aleph", "isbn": "978-950-07-0001-1", "stock": 5, "anio": 1949}
    res = client.post("/libros", json=body)
    assert res.status_code == 201
    data = res.json()
    assert data["titulo"] == "El Aleph"
    assert data["isbn"] == "978-950-07-0001-1"
    assert data["stock"] == 5
    assert data["anio"] == 1949
    assert data["autores"] == []


def test_create_libro_isbn_duplicado_409(client, seed):
    body = {"titulo": "Otro libro", "isbn": "978-84-206-6655-6", "stock": 1, "anio": 2020}
    res = client.post("/libros", json=body)
    assert res.status_code == 409


def test_create_libro_stock_negativo_422(client):
    body = {"titulo": "Stock Inválido", "isbn": "978-00-000-0000-1", "stock": -1, "anio": 2020}
    res = client.post("/libros", json=body)
    assert res.status_code == 422


def test_get_libros_all_and_disponibles(client, seed):
    # En seed: libro 1 (stock 3), libro 2 (stock 2), libro 3 (stock 0)
    res_all = client.get("/libros")
    assert res_all.status_code == 200
    assert len(res_all.json()) == 3

    res_disp = client.get("/libros?disponibles=true")
    assert res_disp.status_code == 200
    libros_disp = res_disp.json()
    assert len(libros_disp) == 2
    assert all(libro["stock"] > 0 for libro in libros_disp)

    res_no_disp = client.get("/libros?disponibles=false")
    assert res_no_disp.status_code == 200
    assert len(res_no_disp.json()) == 1
    assert res_no_disp.json()[0]["stock"] == 0


def test_get_libro_by_id_incluye_autores(client, seed):
    res = client.get("/libros/1")
    assert res.status_code == 200
    data = res.json()
    assert data["titulo"] == "Ficciones"
    assert len(data["autores"]) == 1
    assert data["autores"][0]["nombre"] == "Jorge Luis Borges"


def test_get_libro_not_found(client):
    assert client.get("/libros/999").status_code == 404


def test_update_libro_ok(client, seed):
    body = {"titulo": "Ficciones (Ed. Especial)", "isbn": "978-84-206-6655-6", "stock": 10, "anio": 1944}
    res = client.put("/libros/1", json=body)
    assert res.status_code == 200
    assert res.json()["titulo"] == "Ficciones (Ed. Especial)"
    assert res.json()["stock"] == 10


def test_update_libro_patch_ok(client, seed):
    res = client.patch("/libros/3", json={"stock": 4})
    assert res.status_code == 200
    assert res.json()["stock"] == 4
    assert res.json()["titulo"] == "Rayuela"


def test_update_libro_isbn_duplicado_409(client, seed):
    # Intentar poner al libro 2 el ISBN del libro 1
    res = client.patch("/libros/2", json={"isbn": "978-84-206-6655-6"})
    assert res.status_code == 409


def test_update_libro_not_found(client):
    body = {"titulo": "X", "isbn": "123", "stock": 1, "anio": 2000}
    assert client.put("/libros/999", json=body).status_code == 404
    assert client.patch("/libros/999", json={"stock": 2}).status_code == 404


def test_delete_libro_ok_and_not_found(client, seed):
    assert client.delete("/libros/3").status_code == 200
    assert client.get("/libros/3").status_code == 404
    assert client.delete("/libros/999").status_code == 404


def test_delete_libro_con_prestamo_activo_409(client, seed):
    res_prestamo = client.post("/prestamos", json={"socio_id": 1, "libro_id": 1})
    prestamo_id = res_prestamo.json()["id"]

    # Mientras el préstamo esté activo no se puede borrar el libro
    assert client.delete("/libros/1").status_code == 409

    # Una vez devuelto el libro, sí se permite borrarlo
    client.post(f"/prestamos/{prestamo_id}/devolucion")
    assert client.delete("/libros/1").status_code == 200


def test_asociar_y_desasociar_autor_a_libro(client, seed):
    # Libro 1 ya tiene al autor 1; asociamos también al autor 3
    res = client.post("/libros/1/autores/3")
    assert res.status_code == 200
    nombres = [a["nombre"] for a in res.json()["autores"]]
    assert "Jorge Luis Borges" in nombres
    assert "Julio Cortázar" in nombres

    # Asociar de nuevo el mismo autor es idempotente
    res_idem = client.post("/libros/1/autores/3")
    assert res_idem.status_code == 200
    assert len(res_idem.json()["autores"]) == 2

    # Desasociar autor 3
    res_del = client.delete("/libros/1/autores/3")
    assert res_del.status_code == 200
    assert [a["nombre"] for a in res_del.json()["autores"]] == ["Jorge Luis Borges"]


def test_asociar_autor_recurso_inexistente_404(client, seed):
    assert client.post("/libros/999/autores/1").status_code == 404
    assert client.post("/libros/1/autores/999").status_code == 404
    assert client.delete("/libros/999/autores/1").status_code == 404
    assert client.delete("/libros/1/autores/999").status_code == 404

