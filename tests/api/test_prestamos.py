from datetime import date, timedelta


def test_registrar_prestamo_ok_descuenta_stock_y_calcula_vencimiento(client, seed):
    # Libro 1 tiene stock inicial 3
    fecha_inicio = date(2026, 3, 1)
    res = client.post(
        "/prestamos",
        json={"socio_id": 1, "libro_id": 1, "fecha_prestamo": fecha_inicio.isoformat()},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["socio_id"] == 1
    assert data["libro_id"] == 1
    assert data["fecha_prestamo"] == "2026-03-01"
    # Regla 4: fecha_vencimiento = fecha_prestamo + 14 días
    assert data["fecha_vencimiento"] == (fecha_inicio + timedelta(days=14)).isoformat()
    assert data["fecha_devolucion"] is None
    assert data["multa"] == 0

    # Regla 2: al prestar se descuenta 1 del stock (3 -> 2)
    libro = client.get("/libros/1").json()
    assert libro["stock"] == 2


def test_regla_1_maximo_3_prestamos_activos_por_socio(client, seed):
    # Socio 1 pide 3 préstamos (Libro 1 tiene stock 3)
    for _ in range(3):
        r = client.post("/prestamos", json={"socio_id": 1, "libro_id": 1})
        assert r.status_code == 201

    # El 4to préstamo activo debe fallar con 409 (Libro 2 tiene stock 2)
    res_cuarto = client.post("/prestamos", json={"socio_id": 1, "libro_id": 2})
    assert res_cuarto.status_code == 409

    # Si devuelve uno de los préstamos activos, puede pedir uno nuevo
    client.post("/prestamos/1/devolucion")
    res_nuevo = client.post("/prestamos", json={"socio_id": 1, "libro_id": 2})
    assert res_nuevo.status_code == 201


def test_regla_2_no_se_presta_libro_sin_stock_409(client, seed):
    # En seed, Libro 3 ("Rayuela") tiene stock 0
    res = client.post("/prestamos", json={"socio_id": 1, "libro_id": 3})
    assert res.status_code == 409


def test_regla_3_socio_inactivo_no_puede_pedir_prestamos_403(client, seed):
    # En seed, Socio 3 tiene activo=False
    res = client.post("/prestamos", json={"socio_id": 3, "libro_id": 1})
    assert res.status_code == 403


def test_regla_5_devolucion_a_tiempo_repone_stock_y_multa_cero(client, seed):
    res_prestamo = client.post(
        "/prestamos",
        json={"socio_id": 1, "libro_id": 1, "fecha_prestamo": "2026-03-01"},
    )
    prestamo_id = res_prestamo.json()["id"]
    assert client.get("/libros/1").json()["stock"] == 2

    # Vence el 2026-03-15; se devuelve exactamente en la fecha de vencimiento
    res_dev = client.post(
        f"/prestamos/{prestamo_id}/devolucion",
        json={"fecha_devolucion": "2026-03-15"},
    )
    assert res_dev.status_code == 200
    data = res_dev.json()
    assert data["fecha_devolucion"] == "2026-03-15"
    assert data["multa"] == 0

    # El stock se repone a 3
    assert client.get("/libros/1").json()["stock"] == 3


def test_regla_5_devolucion_con_atraso_calcula_multa(client, seed):
    res_prestamo = client.post(
        "/prestamos",
        json={"socio_id": 1, "libro_id": 1, "fecha_prestamo": "2026-03-01"},
    )
    prestamo_id = res_prestamo.json()["id"]

    # Vence el 2026-03-15; se devuelve el 2026-03-20 (5 días de atraso -> $500)
    res_dev = client.post(
        f"/prestamos/{prestamo_id}/devolucion",
        json={"fecha_devolucion": "2026-03-20"},
    )
    assert res_dev.status_code == 200
    data = res_dev.json()
    assert data["fecha_devolucion"] == "2026-03-20"
    assert data["multa"] == 500
    assert client.get("/libros/1").json()["stock"] == 3


def test_regla_6_no_se_puede_devolver_prestamo_ya_devuelto_409(client, seed):
    res_prestamo = client.post("/prestamos", json={"socio_id": 1, "libro_id": 1})
    prestamo_id = res_prestamo.json()["id"]

    assert client.post(f"/prestamos/{prestamo_id}/devolucion").status_code == 200
    res_segunda = client.post(f"/prestamos/{prestamo_id}/devolucion")
    assert res_segunda.status_code == 409


def test_regla_7_recursos_inexistentes_en_prestamos_404(client, seed):
    # Socio inexistente al prestar
    assert client.post("/prestamos", json={"socio_id": 999, "libro_id": 1}).status_code == 404
    # Libro inexistente al prestar
    assert client.post("/prestamos", json={"socio_id": 1, "libro_id": 999}).status_code == 404
    # Préstamo inexistente al consultar o devolver
    assert client.get("/prestamos/999").status_code == 404
    assert client.post("/prestamos/999/devolucion").status_code == 404
    # Socio inexistente al listar sus préstamos
    assert client.get("/socios/999/prestamos").status_code == 404


def test_get_prestamos_y_filtro_activos_por_socio(client, seed):
    p1 = client.post("/prestamos", json={"socio_id": 1, "libro_id": 1}).json()
    p2 = client.post("/prestamos", json={"socio_id": 1, "libro_id": 2}).json()

    # Devolvemos el primer préstamo
    client.post(f"/prestamos/{p1['id']}/devolucion")

    # Todos los préstamos del socio 1
    todos = client.get("/socios/1/prestamos").json()
    assert len(todos) == 2

    # Solo préstamos activos del socio 1
    activos = client.get("/socios/1/prestamos?activos=true").json()
    assert len(activos) == 1
    assert activos[0]["id"] == p2["id"]
    assert activos[0]["fecha_devolucion"] is None

    # Solo préstamos devueltos del socio 1
    inactivos = client.get("/socios/1/prestamos?activos=false").json()
    assert len(inactivos) == 1
    assert inactivos[0]["id"] == p1["id"]
    assert inactivos[0]["fecha_devolucion"] is not None

    # Listado general y consulta individual de préstamos
    assert len(client.get("/prestamos").json()) == 2
    assert client.get(f"/prestamos/{p1['id']}").status_code == 200

