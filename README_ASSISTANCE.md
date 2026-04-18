# 📌 Servicio de Asistencia — Registro de Asistencia

Documentación detallada para el consumo del servicio de registro de asistencia mediante código QR.

## 🚀 Endpoint
**POST** `/api/v1/assistances/`

## 📥 Cuerpo de la Petición (Request Body)
Se debe enviar un objeto JSON con el ULID del miembro y el ID de sesión del código QR.

```json
{
    "member_ulid"   : "01ARZ3NDEKTSV4RRFFQ69G5FAV",
    "qr_session_id" : "session_uuid_here"
}
```

### Campos:
- **`member_ulid`**: `string` (Requerido) — El identificador único del miembro (ULID).
- **`qr_session_id`**: `string` (Requerido) — El identificador de la sesión activa del código QR.

---

## 📤 Respuestas (Responses)

### ✅ 201 Created — Asistencia Registrada
La asistencia se ha registrado exitosamente. Retorna el objeto de asistencia completo basado en la entidad `Assistance`.

#### Formato de Respuesta:
```json
{
    "_id"        : "01ARZ3NDEKTSV4RRFFQ69G5FAV",
    "member"     : {
        "_id"        : "65f2a1b2c3d4e5f6a7b8c9d0",
        "name"       : "Juan",
        "last_name"  : "Pérez",
        "classes"    : [ "Pintura", "Dibujo" ],
        "saveFinger" : false,
        "ulid_token" : "01ARZ3NDEKTSV4RRFFQ69G5FAV",
        "created_at" : "2024-03-14T12:00:00Z",
        "updated_at" : "2024-03-14T12:00:00Z"
    },
    "qr"         : {
        "_id"        : "65f2a1b2c3d4e5f6a7b8c9d1",
        "type"       : "Pintura",
        "date"       : "2024-03-14T00:00:00Z",
        "start_hour" : "09:00",
        "end_hour"   : "10:30",
        "created_at" : "2024-03-14T08:00:00Z",
        "updated_at" : "2024-03-14T08:00:00Z"
    },
    "created_at" : "2024-03-14T12:05:00Z",
    "updated_at" : "2024-03-14T12:05:00Z"
}
```

### ✅ 200 OK — Asistencia Ya Registrada
Si el miembro ya había registrado su asistencia para este QR anteriormente, el servicio retorna la información del miembro sin crear un nuevo registro.

---

### ❌ 400 Bad Request — Errores de Validación
Ocurre cuando la petición es válida pero no cumple con las reglas de negocio.

| Código de Error | Mensaje | Descripción |
| :--- | :--- | :--- |
| `ERR_201` | El miembro no puede asistir a esta clase. | La clase del QR no coincide con las permitidas para el miembro. |
| `ERR_301` | Debas completar la encuesta del tercer domingo... | El tercer domingo del mes requiere una encuesta previa. |
| `ERR_202` | Este QR ya expiró. | La fecha del QR es anterior a la fecha actual. |
| `ERR_203` | Este QR es para la fecha X, no para hoy. | La fecha del QR es futura. |
| `ERR_204` | Fuera de horario. | La hora actual no está dentro del rango `start_hour` y `end_hour`. |
| `ERR_205` | Formato de hora en QR inválido. | Error interno en el formato de hora almacenado en el QR. |

#### Ejemplo de Error 400:
```json
{
    "detail": {
        "code"    : "ERR_204",
        "message" : "Fuera de horario. Válido de 09:00 a 10:30. Hora actual: 11:15."
    }
}
```

---

### ❌ 404 Not Found — Recurso No Encontrado
| Código de Error | Mensaje | Descripción |
| :--- | :--- | :--- |
| `ERR_103` | Miembro o QR no encontrado. | El `member_ulid` o el `qr_session_id` no existen en la base de datos. |

---

### ❌ 500 Internal Server Error
| Código de Error | Mensaje | Descripción |
| :--- | :--- | :--- |
| `ERR_501` | Error al registrar la asistencia. | Fallo inesperado al insertar el registro en la base de datos. |
