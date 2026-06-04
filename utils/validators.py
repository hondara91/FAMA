"""utils/validators.py - Validaciones de negocio reutilizables en FAMA."""
import re


def validar_password_fuerte(password):
    """
    Verifica que la contraseña cumpla los requisitos mínimos de seguridad.
    Devuelve un mensaje de error (str) o None si es válida.
    Requisitos: 8+ caracteres, 1 mayúscula, 1 minúscula, 1 número, 1 especial.
    """
    if len(password) < 8:
        return "La contraseña debe tener al menos 8 caracteres."
    if not re.search(r'[A-Z]', password):
        return "La contraseña debe incluir al menos una mayúscula."
    if not re.search(r'[a-z]', password):
        return "La contraseña debe incluir al menos una minúscula."
    if not re.search(r'[0-9]', password):
        return "La contraseña debe incluir al menos un número."
    if not re.search(r'[^A-Za-z0-9]', password):
        return "La contraseña debe incluir al menos un carácter especial (!@#$%...)."
    return None
