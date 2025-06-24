"""
Modelos de datos para el Sistema de Gestión Clínica
Define todas las tablas y relaciones de la base de datos
"""

from flask_login import UserMixin
from datetime import datetime
from ..extensions import db  # ✅ import desde extensions.py

# Tabla intermedia para la relación muchos a muchos entre doctores y especialidades
doctor_especialidad = db.Table('doctor_especialidad',
    db.Column('doctor_id', db.Integer, db.ForeignKey('usuarios.id'), primary_key=True),
    db.Column('especialidad_id', db.Integer, db.ForeignKey('especialidades.id'), primary_key=True)
)

class Rol(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)

    usuarios = db.relationship('Usuario', backref='rol', lazy=True)

    def __repr__(self):
        return f'<Rol {self.nombre}>'

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_usuario = db.Column(db.String(80), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    superadmin = db.Column(db.Boolean, default=False)
    nombre_completo = db.Column(db.String(150), nullable=False)

    expedientes = db.relationship('Expediente', backref='doctor', lazy=True)
    especialidades = db.relationship('Especialidad', secondary=doctor_especialidad, backref='doctores')

    def is_admin(self):
        return self.rol.nombre == 'administrador'

    def is_doctor(self):
        return self.rol.nombre == 'doctor'

    def is_superadmin(self):
        return self.superadmin

    def get_nombre_completo(self):
        return self.nombre_completo

    def __repr__(self):
        return f'<Usuario {self.nombre_usuario}>'

class Paciente(db.Model):
    __tablename__ = 'pacientes'

    carnet = db.Column(db.String(20), primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    genero = db.Column(db.String(20))
    direccion = db.Column(db.String(255))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100), unique=True)
    estado = db.Column(db.Boolean, default=True)

    expedientes = db.relationship('Expediente', backref='paciente', lazy=True)

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"

    @property
    def edad(self):
        today = datetime.now().date()
        return today.year - self.fecha_nacimiento.year - \
               ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))

    def __repr__(self):
        return f'<Paciente {self.carnet}: {self.nombre_completo}>'

class Especialidad(db.Model):
    __tablename__ = 'especialidades'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)

    expedientes = db.relationship('Expediente', backref='especialidad', lazy=True)

    def __repr__(self):
        return f'<Especialidad {self.nombre}>'

class Expediente(db.Model):
    __tablename__ = 'expedientes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    paciente_carnet = db.Column(db.String(20), db.ForeignKey('pacientes.carnet'), nullable=False)
    especialidad_id = db.Column(db.Integer, db.ForeignKey('especialidades.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    tipo_consulta = db.Column(db.String(100), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_consulta = db.Column(db.Date, nullable=False)
    resumen_clinico = db.Column(db.Text)
    datos_consulta = db.Column(db.JSON)

    def __repr__(self):
        return f'<Expediente {self.id}: {self.paciente.nombre_completo} - {self.especialidad.nombre}>'
