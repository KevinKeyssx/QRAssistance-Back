# ============================================================
# Error Codes — QRAssistance API
# ============================================================
# Formato : ERR_XYZ
#   1xx   : Errores de Recursos (no encontrado, no disponible)
#   2xx   : Errores de Validación de Asistencia
#   3xx   : Errores de Encuesta (Survey)
#   4xx   : Errores de QR
#   5xx   : Errores Internos / Registro
# ============================================================


class ErrorCode:

    # ── 1xx · Recursos ──────────────────────────────────────
    ERR_101 = "ERR_101"    # Miembro no encontrado
    ERR_102 = "ERR_102"    # QR no encontrado
    ERR_103 = "ERR_103"    # Miembro o QR no encontrado
    ERR_104 = "ERR_104"    # Asistencia no encontrada
    ERR_105 = "ERR_105"    # Miembro duplicado

    # ── 2xx · Validación de Asistencia ──────────────────────
    ERR_201 = "ERR_201"    # El miembro no puede asistir a esta clase
    ERR_202 = "ERR_202"    # El QR ya expiró
    ERR_203 = "ERR_203"    # El QR es para una fecha futura
    ERR_204 = "ERR_204"    # Fuera del rango horario permitido
    ERR_205 = "ERR_205"    # Formato de hora en QR inválido
    ERR_206 = "ERR_206"    # El miembro se pudo registrar pero no su asistencia

    # ── 3xx · Encuesta (Survey) ──────────────────────────────
    ERR_301 = "ERR_301"    # El miembro no ha completado la encuesta del tercer domingo
    ERR_302 = "ERR_302"    # Encuesta no encontrada
    ERR_303 = "ERR_303"    # El miembro ya registró una encuesta para este QR (duplicado)

    # ── 4xx · QR ────────────────────────────────────────────
    ERR_401 = "ERR_401"    # QR no encontrado al eliminar

    # ── 5xx · Internos / Registro ───────────────────────────
    ERR_501 = "ERR_501"    # Error al registrar la asistencia
