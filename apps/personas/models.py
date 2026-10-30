"""Modelos de la app personas: personas (naturales y jurídicas) y usuarios de acceso.

Reglas que implementa este módulo:
- ACC-03: un usuario por persona; una persona jurídica (institución) nunca tiene usuario.
- ACC-05: el inicio de sesión es con correo (sin distinguir mayúsculas); el teléfono es solo contacto.
- ACC-06: una persona puede registrarse sin correo (la admisión queda pendiente).
- TEC-07: auditoría de cambios con django-simple-history.
- TEC-11: esta app no importa ninguna otra app del proyecto.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower
from django.utils import timezone
from simple_history.models import HistoricalRecords

from .normalizacion import normalizar_correo, normalizar_identificacion


class TipoPersona(models.TextChoices):
    NATURAL = 'natural', 'Natural'
    JURIDICA = 'juridica', 'Jurídica'


class TipoIdentificacion(models.TextChoices):
    CEDULA = 'cedula', 'Cédula'
    RUC = 'ruc', 'RUC'
    PASAPORTE = 'pasaporte', 'Pasaporte'
    OTRO = 'otro', 'Otro'


class Persona(models.Model):
    """Persona natural o jurídica. La institución es una persona jurídica sin usuario (ACC-03)."""

    Tipo = TipoPersona

    tipo = models.CharField('tipo de persona', max_length=10, choices=TipoPersona.choices)
    nombres = models.CharField('nombres o razón social', max_length=200)
    apellidos = models.CharField('apellidos', max_length=200, blank=True)
    tipo_identificacion = models.CharField(
        'tipo de identificación', max_length=10, choices=TipoIdentificacion.choices
    )
    numero_identificacion = models.CharField('número de identificación', max_length=30)
    fecha_nacimiento = models.DateField('fecha de nacimiento', null=True, blank=True)
    # ACC-06: el correo puede faltar; la admisión queda pendiente hasta tenerlo.
    correo = models.EmailField('correo', blank=True)
    # ACC-05: el teléfono es solo dato de contacto, nunca credencial.
    telefono = models.CharField('teléfono', max_length=30, blank=True)
    direccion = models.TextField('dirección', blank=True)

    # TEC-07: historial completo de cambios.
    historial = HistoricalRecords(
        verbose_name='historial de persona',
        verbose_name_plural='historial de personas',
    )

    class Meta:
        verbose_name = 'persona'
        verbose_name_plural = 'personas'
        constraints = [
            models.UniqueConstraint(
                fields=['tipo_identificacion', 'numero_identificacion'],
                name='persona_identificacion_unica',
                violation_error_message='Ya existe una persona con este tipo y número de identificación.',
            ),
            models.CheckConstraint(
                condition=Q(tipo__in=TipoPersona.values),
                name='persona_tipo_valido',
            ),
            models.CheckConstraint(
                condition=~Q(numero_identificacion=''),
                name='persona_identificacion_no_vacia',
            ),
            models.CheckConstraint(
                condition=Q(tipo=TipoPersona.JURIDICA) | ~Q(apellidos=''),
                name='persona_natural_con_apellidos',
            ),
            models.CheckConstraint(
                condition=Q(tipo=TipoPersona.NATURAL) | Q(apellidos='', fecha_nacimiento__isnull=True),
                name='persona_juridica_sin_datos_naturales',
            ),
        ]

    @property
    def nombre_completo(self) -> str:
        if self.tipo == TipoPersona.NATURAL:
            return f'{self.nombres} {self.apellidos}'.strip()
        return self.nombres

    def __str__(self) -> str:
        return self.nombre_completo

    def clean(self):
        super().clean()
        self.numero_identificacion = normalizar_identificacion(self.numero_identificacion)
        self.correo = normalizar_correo(self.correo)
        self.nombres = (self.nombres or '').strip()
        self.apellidos = (self.apellidos or '').strip()

        errores = {}
        if not self.nombres:
            errores['nombres'] = 'Los nombres o la razón social son obligatorios.'
        if not self.numero_identificacion:
            errores['numero_identificacion'] = 'El número de identificación es obligatorio.'
        if self.tipo == TipoPersona.NATURAL and not self.apellidos:
            errores['apellidos'] = 'Una persona natural debe tener apellidos.'
        if self.tipo == TipoPersona.JURIDICA and self.apellidos:
            errores['apellidos'] = 'Una persona jurídica no lleva apellidos: use la razón social.'
        if self.tipo == TipoPersona.JURIDICA and self.fecha_nacimiento:
            errores['fecha_nacimiento'] = 'Una persona jurídica no lleva fecha de nacimiento.'
        # ACC-03: no se puede convertir en jurídica a una persona que ya tiene usuario.
        if (
            self.tipo == TipoPersona.JURIDICA
            and self.pk
            and Usuario.objects.filter(persona_id=self.pk).exists()
        ):
            errores['tipo'] = 'No se puede cambiar a jurídica una persona que ya tiene usuario (ACC-03).'
        if (
            self.numero_identificacion
            and self.tipo_identificacion
            and 'numero_identificacion' not in errores
        ):
            otra = Persona.objects.filter(
                tipo_identificacion=self.tipo_identificacion,
                numero_identificacion=self.numero_identificacion,
            )
            if self.pk:
                otra = otra.exclude(pk=self.pk)
            otra = otra.first()
            if otra is not None:
                errores['numero_identificacion'] = (
                    f'Esta identificación ya pertenece a {otra.nombre_completo}.'
                )

        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        # Idempotente: deja la BD con valores normalizados aunque no se llame a full_clean().
        self.numero_identificacion = normalizar_identificacion(self.numero_identificacion)
        self.correo = normalizar_correo(self.correo)
        super().save(*args, **kwargs)


class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    @classmethod
    def normalize_email(cls, email):
        """ACC-05: el correo se normaliza completo (no solo el dominio, como hace Django)."""
        return normalizar_correo(email)

    def get_by_natural_key(self, email):
        """ACC-05: 'Ana@x.org' y 'ana@x.org' son el mismo inicio de sesión."""
        return self.get(email__iexact=normalizar_correo(email))

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('El correo es obligatorio.')
        usuario = self.model(email=self.normalize_email(email), **extra_fields)
        usuario.set_password(password)
        # full_clean() hace cumplir ACC-03 (jurídica sin usuario) y la unicidad del correo.
        usuario.full_clean()
        usuario.save(using=self._db)
        return usuario

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Usuario de acceso al sistema. Inicia sesión con correo (ACC-05).

    Los roles son grupos de Django (#22); aquí no hay "tipo de usuario" (regla de oro 2).
    No hereda de AbstractUser: nombres y apellidos viven en Persona.
    """

    email = models.EmailField(
        'correo',
        unique=True,
        error_messages={'unique': 'Ya existe un usuario con este correo.'},
    )
    # ACC-03: una persona tiene como máximo un usuario. Nulo solo para la cuenta técnica del instalador.
    persona = models.OneToOneField(
        Persona,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='usuario',
        verbose_name='persona',
    )
    is_active = models.BooleanField('activo', default=True)
    is_staff = models.BooleanField('acceso al panel', default=False)
    date_joined = models.DateTimeField('fecha de alta', default=timezone.now)

    objects = UsuarioManager()

    # TEC-07: la contraseña y el último inicio no se auditan (cambian con cada login).
    historial = HistoricalRecords(
        excluded_fields=['password', 'last_login'],
        m2m_fields=['groups'],
        verbose_name='historial de usuario',
        verbose_name_plural='historial de usuarios',
    )

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'
        constraints = [
            # Garantía en BD de unicidad sin distinguir mayúsculas, aunque algo salte save().
            models.UniqueConstraint(
                Lower('email'),
                name='usuario_email_unico_sin_mayusculas',
                violation_error_message='Ya existe un usuario con este correo.',
            ),
        ]

    def clean(self):
        super().clean()
        self.email = normalizar_correo(self.email)
        if self.persona_id and self.persona.tipo == Persona.Tipo.JURIDICA:
            raise ValidationError({'persona': 'Una persona jurídica no puede tener usuario (ACC-03).'})

    def save(self, *args, **kwargs):
        self.email = normalizar_correo(self.email)
        update_fields = kwargs.get('update_fields')
        # Al iniciar sesión Django guarda solo last_login; eso no debe generar historial.
        if update_fields is not None and set(update_fields) == {'last_login'}:
            self.skip_history_when_saving = True
            try:
                super().save(*args, **kwargs)
            finally:
                del self.skip_history_when_saving
            return
        super().save(*args, **kwargs)

    def get_full_name(self):
        return self.persona.nombre_completo if self.persona_id else self.email

    def get_short_name(self):
        return self.persona.nombres if self.persona_id else self.email

    def __str__(self) -> str:
        return self.email
