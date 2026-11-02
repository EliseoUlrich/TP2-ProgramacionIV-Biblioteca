# 📚 TP2: Sistema de Biblioteca (FastAPI + SQLModel)

Este repositorio contiene la resolución del **Trabajo Práctico N° 2: Sistema de Biblioteca** para la cátedra de **Programación IV (Backend con Python)**.

El objetivo del trabajo es construir una **API REST** para gestionar el catálogo de una biblioteca (`Autores`, `Libros`, `Socios`) y el flujo completo de `Préstamos` y devoluciones, aplicando relaciones entre entidades, arquitectura en capas, inyección de dependencias y reglas de negocio con los códigos de estado HTTP correspondientes.

---

## 🛠️ Qué se hizo en este TP

Partiendo de la plantilla didáctica de la cátedra (`clase-1-sqlmodel`), el proyecto fue adaptado y estructurado como `TP2-ProgramacionIV-Biblioteca`, realizando una refactorización integral:

1. **Limpieza del proyecto base:** Se eliminaron todos los módulos de ejemplo generales de la clase (`users`, `countries`, `roles`, `permissions`, `middlewares` de conteo y autenticación) para dejar únicamente el dominio de la **Biblioteca**.
2. **Modelado Relacional con SQLModel (`model/`):**
   - Relación **N-N** entre `Libro` y `Autor` mediante la tabla intermedia `LibroAutor` (`link_model`).
   - Relaciones **N-1** desde `Prestamo` hacia `Socio` y `Libro`, con borrado en cascada (`cascade_delete=True`).
   - Validaciones a nivel de esquema (`isbn` único, `stock >= 0`, `email` único con `EmailStr`).
3. **Capa de Persistencia (`repositories/`):**
   - Repositorios dedicados por entidad (`AutorRepository`, `LibroRepository`, `SocioRepository`, `PrestamoRepository`) e inicialización automática con datos de prueba (`seed_biblioteca`).
4. **Reglas de Negocio desacopladas (`services/`):**
   - Toda la lógica y validación de reglas de negocio vive exclusivamente en la capa `services` (implementando interfaces abstractas `ABC`), manteniendo los routers HTTP livianos.
5. **Controladores y DTOs (`api/` y `api/model/`):**
   - Separación entre modelos de persistencia y esquemas de entrada/salida (`Create*Request`, `Update*Request`, `*Response`), incluyendo la lista de `autores` en las respuestas de libros.

---

## 📂 Estructura del Proyecto

```text
TP2-ProgramacionIV-Biblioteca/
├── api/                        # Controladores HTTP (Routers) y DTOs
│   ├── model/                  # Esquemas Request / Response (autores, libros, socios, prestamos)
│   │   ├── autores.py
│   │   ├── libros.py
│   │   ├── prestamos.py
│   │   └── socios.py
│   ├── autores.py              # Endpoints CRUD de /autores
│   ├── libros.py               # Endpoints CRUD de /libros, filtro disponibles y relación N-N con autores
│   ├── socios.py               # Endpoints CRUD de /socios y consulta de préstamos por socio
│   └── prestamos.py            # Endpoints de /prestamos y devolución
├── model/                      # Entidades de dominio y tablas SQLModel
│   ├── autores.py              # Autor, AutorBase y LibroAutor (tabla intermedia N-N)
│   ├── libros.py               # Libro y LibroBase
│   ├── socios.py               # Socio y SocioBase
│   └── prestamos.py            # Prestamo y PrestamoBase
├── repositories/               # Capa de acceso a datos (SQLModel / SQLite)
│   ├── database.py             # Configuración del motor SQLite y generador de sesión
│   ├── seed.py                 # Precarga idempotente de autores, libros y socios
│   ├── autores.py              # AutorRepository
│   ├── libros.py               # LibroRepository
│   ├── socios.py               # SocioRepository
│   └── prestamos.py            # PrestamoRepository
├── services/                   # Capa de Lógica y Reglas de Negocio
│   ├── autores.py              # AutorServiceInterface / AutorService
│   ├── libros.py               # LibroServiceInterface / LibroService
│   ├── socios.py               # SocioServiceInterface / SocioService
│   └── prestamos.py            # PrestamoServiceInterface / PrestamoService
├── tests/                      # Suite de pruebas automatizadas (47 tests)
│   ├── api/                    # Tests de integración por cada router y regla de negocio
│   │   ├── test_autores.py
│   │   ├── test_libros.py
│   │   ├── test_prestamos.py
│   │   ├── test_seed.py
│   │   └── test_socios.py
│   ├── services/               # Tests unitarios directos sobre la capa services
│   │   └── test_prestamos_service.py
│   └── conftest.py             # Fixtures (SQLite en memoria con StaticPool y TestClient)
├── dependencies.py             # Inyección de dependencias centralizada (Annotated + Depends)
├── main.py                     # Inicialización de FastAPI, evento startup y registro de routers
├── pyproject.toml              # Configuración de linter (Ruff) y Pyright
├── requirements.txt            # Dependencias del proyecto
├── README.md                   # Documentación completa del proyecto
└── TP2-fastapi-biblioteca.md   # Consignas originales del Trabajo Práctico
```

---

## 🗃️ Modelo de Datos

| Entidad | Campos |
|---|---|
| `Autor` | `id`, `nombre`, `nacionalidad` |
| `Libro` | `id`, `titulo`, `isbn` (único), `stock` ($\ge 0$), `anio` |
| `LibroAutor` | `libro_id`, `autor_id` (tabla intermedia N-N) |
| `Socio` | `id`, `nombre`, `email` (único), `activo` |
| `Prestamo` | `id`, `socio_id`, `libro_id`, `fecha_prestamo`, `fecha_vencimiento`, `fecha_devolucion` (nullable), `multa` |

---

## 🌐 Endpoints y Códigos HTTP

| Método | Ruta | Descripción | Código Éxito |
|---|---|---|---|
| `POST` | `/autores` | Crea un nuevo autor | `201 Created` |
| `GET` | `/autores` | Lista todos los autores | `200 OK` |
| `GET` | `/autores/{id}` | Obtiene un autor por su ID | `200 OK` |
| `PUT` / `PATCH` | `/autores/{id}` | Modifica total o parcialmente un autor | `200 OK` |
| `DELETE` | `/autores/{id}` | Elimina un autor | `200 OK` |
| `POST` | `/libros` | Crea un nuevo libro | `201 Created` |
| `GET` | `/libros` | Lista libros (`?disponibles=true` filtra `stock > 0`) | `200 OK` |
| `GET` | `/libros/{id}` | Obtiene un libro por su ID (incluye sus `autores`) | `200 OK` |
| `PUT` / `PATCH` | `/libros/{id}` | Modifica total o parcialmente un libro | `200 OK` |
| `DELETE` | `/libros/{id}` | Elimina un libro | `200 OK` |
| `POST` | `/libros/{id}/autores/{autor_id}` | Asocia un autor a un libro | `200 OK` |
| `DELETE` | `/libros/{id}/autores/{autor_id}` | Desasocia un autor de un libro | `200 OK` |
| `POST` | `/socios` | Registra un nuevo socio | `201 Created` |
| `GET` | `/socios` | Lista todos los socios | `200 OK` |
| `GET` | `/socios/{id}` | Obtiene un socio por su ID | `200 OK` |
| `PUT` / `PATCH` | `/socios/{id}` | Modifica total o parcialmente un socio | `200 OK` |
| `DELETE` | `/socios/{id}` | Elimina un socio | `200 OK` |
| `GET` | `/socios/{id}/prestamos` | Lista préstamos del socio (`?activos=true` filtra no devueltos) | `200 OK` |
| `POST` | `/prestamos` | Registra un nuevo préstamo | `201 Created` |
| `GET` | `/prestamos` | Lista todos los préstamos | `200 OK` |
| `GET` | `/prestamos/{id}` | Obtiene un préstamo por su ID | `200 OK` |
| `POST` | `/prestamos/{id}/devolucion` | Registra la devolución, repone stock y calcula la multa | `200 OK` |

---

## ⚖️ Reglas de Negocio Implementadas

| # | Regla de Negocio | Código de Error / Comportamiento |
|---|---|---|
| **1** | Un socio no puede tener más de 3 préstamos activos simultáneos | `409 Conflict` |
| **2** | No se presta un libro sin stock (`stock <= 0`); al prestar se descuenta `1` unidad | `409 Conflict` |
| **3** | Un socio inactivo (`activo = False`) no puede pedir préstamos | `403 Forbidden` |
| **4** | El plazo del préstamo es de 14 días (`fecha_vencimiento = fecha_prestamo + 14 días`) | Automático al crear (`201`) |
| **5** | Al devolver se repone `1` al stock y se calcula la multa: $\$100 \times \text{días de atraso}$ ($0$ si llegó a tiempo) | Automático al devolver (`200`) |
| **6** | No se puede devolver un préstamo que ya fue devuelto | `409 Conflict` |
| **7** | Consulta, modificación, baja o relación sobre un recurso inexistente | `404 Not Found` |
| **8** | `ISBN` de libro o `email` de socio duplicado (en alta o modificación) | `409 Conflict` |

---

## 🚀 Instalación y Puesta en Marcha

Requisitos previos: tener instalado **Python 3.11 o superior** y **Git**.

---

### 🪟 En Windows (PowerShell o CMD)

#### 1. Clonar el repositorio y entrar a la carpeta
```powershell
git clone https://github.com/EliseoUlrich/TP2-ProgramacionIV-Biblioteca.git
cd TP2-ProgramacionIV-Biblioteca
```

#### 2. Crear y activar el entorno virtual
- **En PowerShell:**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  ```
  *(Nota: si PowerShell bloquea la ejecución de scripts, ejecuta antes: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

- **En CMD (Símbolo del sistema):**
  ```cmd
  python -m venv .venv
  .venv\Scripts\activate.bat
  ```

#### 3. Instalar las dependencias
```powershell
pip install -r requirements.txt
```

#### 4. Levantar el servidor de desarrollo
```powershell
uvicorn main:app --reload
```

---

### 🐧🍎 En Linux y macOS (Bash / Zsh)

#### 1. Clonar el repositorio y entrar a la carpeta
```bash
git clone https://github.com/EliseoUlrich/TP2-ProgramacionIV-Biblioteca.git
cd TP2-ProgramacionIV-Biblioteca
```

#### 2. Crear y activar el entorno virtual
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### 3. Instalar las dependencias
```bash
pip install -r requirements.txt
```

#### 4. Levantar el servidor de desarrollo
```bash
uvicorn main:app --reload
```

---

### 🌐 Acceso a la Documentación Interactiva
Una vez iniciado el servidor (en cualquier sistema operativo), abre tu navegador en:
- **Swagger UI (para probar los endpoints):** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

*(Al iniciar por primera vez, la aplicación crea automáticamente el archivo `database.db` y carga datos iniciales de autores, libros y socios).*

---

## 🧪 Testing y Cobertura

La suite de pruebas utiliza **pytest** junto con una base de datos **SQLite en memoria** (`StaticPool`), garantizando que cada test corra en un entorno limpio e independiente sin modificar `database.db`.

> **Nota sobre la autoría de los tests:**  
> Para este trabajo práctico **hice 10 tests a mano** cubriendo los casos principales de las reglas de negocio y el flujo de préstamos, y **le pedí a la IA que genere el resto de los tests** (37 pruebas adicionales) para cubrir de forma exhaustiva todas las ramas de error (`403`, `404`, `409`, `422`), operaciones CRUD, idempotencia del seed y pruebas unitarias de la capa `services`.  
> En total la suite cuenta con **47 tests** y alcanza un **99.9% de cobertura de código** (superando ampliamente el mínimo del 80% requerido en la consigna).

### Cómo correr los tests

- **En Windows:**
  Con el entorno virtual activado:
  ```powershell
  pytest -v
  pytest --cov=. --cov-report=term-missing
  ```
  O invocando directamente el ejecutable del entorno virtual:
  ```powershell
  .\.venv\Scripts\python -m pytest -v
  .\.venv\Scripts\python -m pytest --cov=. --cov-report=term-missing
  ```

- **En Linux / macOS:**
  Con el entorno virtual activado:
  ```bash
  pytest -v
  pytest --cov=. --cov-report=term-missing
  ```
  O invocando directamente el ejecutable del entorno virtual:
  ```bash
  .venv/bin/pytest -v
  .venv/bin/pytest --cov=. --cov-report=term-missing
  ```
