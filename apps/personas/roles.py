"""Roles confirmados (ACC-03/04, sección 3, C24 y C39)."""

ADMISION_COBRANZA = 'Admisión y cobranza'
REGISTRO_ACADEMICO = 'Registro académico'
MAESTRO = 'Maestro'
ALUMNO = 'Alumno'

PERMISOS_PERSONA = ('view_persona', 'add_persona', 'change_persona')
PERMISOS_INICIALES = {
    ADMISION_COBRANZA: PERMISOS_PERSONA,
    REGISTRO_ACADEMICO: PERMISOS_PERSONA,
    MAESTRO: (),
    ALUMNO: (),
}
ROLES = tuple(PERMISOS_INICIALES)
