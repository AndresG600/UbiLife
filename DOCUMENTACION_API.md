# 6. DOCUMENTACIÓN API – ENDPOINTS PRINCIPALES

---

## Autenticación

·POST /cuidadores/verificar
```json
{
  "email": "cuidador@ejemplo.com",
  "password": "Contraseña123!"
}
```

---

## Registro de usuario

·POST /cuidadores/registrar
```json
{
  "name": "Juan Pérez",
  "email": "cuidador@ejemplo.com",
  "password": "Contraseña123!",
  "phone": "+573001234567"
}
```

---

## Registrar paciente

·POST /pacientes/registrar
```json
{
  "nombre_paciente": "Carlos López",
  "edad_paciente": 75,
  "enfermedad": "Alzheimer",
  "cedula": "12345678",
  "eps": "Sura",
  "familiar_nombre": "Ana López",
  "familiar_telefono": "+573005551234"
}
```

---

## Vincular dispositivo

·POST /dispositivos/vincular
```json
{
  "id_dispositivo": "ESP32-C6-001",
  "paciente_id": "6650abc123def456789012ab"
}
```

---

## Crear zona segura

·POST /zonas-seguras/crear
```json
{
  "paciente_id": "6650abc123def456789012ab",
  "nombre": "Casa",
  "centro": {
    "latitud": 4.7110,
    "longitud": -74.0721
  },
  "radio_metros": 100
}
```

---

## Stream de ubicación en tiempo real

·GET /pacientes/{id}/ubicacion/stream
*(Requiere Bearer Token — responde text/event-stream)*

---

## Consultar alertas

·GET /alertas/
*(Requiere Bearer Token — sin cuerpo)*

---

## Activar modo viaje

·POST /modo-viaje/activar
```json
{
  "paciente_id": "6650abc123def456789012ab",
  "tipo": "caminata",
  "duracion_horas": 2.0
}
```
