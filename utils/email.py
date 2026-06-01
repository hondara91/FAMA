"""
utils/email.py - Envio de emails transaccionales via Resend.

Gestiona la generacion de tokens firmados (itsdangerous) y el envio
del email de verificacion de cuenta al registrarse.
"""
import resend
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from flask import current_app


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def generar_token_verificacion(email: str) -> str:
    """Genera un token firmado que codifica el email. Expira en 24 h."""
    return _serializer().dumps(email, salt="verificacion-email")


def confirmar_token_verificacion(token: str, max_age: int = 86400):
    """
    Decodifica y valida el token. Devuelve el email o None si es invalido/expirado.
    max_age en segundos (86400 = 24 horas).
    """
    try:
        email = _serializer().loads(token, salt="verificacion-email", max_age=max_age)
    except (BadSignature, SignatureExpired):
        return None
    return email


def enviar_aprobacion_cuenta(email: str, nombre: str, password_temporal: str) -> bool:
    """
    Notifica al usuario que su cuenta ha sido aprobada y le envia su contrasena temporal.
    Devuelve True si el envio fue exitoso.
    """
    app_url = current_app.config.get("APP_URL", "http://localhost:5000").rstrip("/")
    login_url = f"{app_url}/auth/login"

    resend.api_key = current_app.config["RESEND_API_KEY"]

    try:
        resend.Emails.send({
            "from": current_app.config["MAIL_FROM"],
            "to": [email],
            "subject": "FAMA - Tu cuenta ha sido aprobada",
            "html": f"""
            <div style="font-family:Arial,sans-serif;max-width:520px;margin:auto;padding:24px;border:1px solid #e0e0e0;border-radius:8px">
                <h2 style="color:#003366">Bienvenido a FAMA, {nombre}</h2>
                <p>Tu cuenta ha sido <strong>aprobada por el administrador</strong>. Ya puedes acceder a la plataforma.</p>
                <p>Tus credenciales de acceso son:</p>
                <table style="border-collapse:collapse;width:100%;margin:16px 0">
                    <tr>
                        <td style="padding:8px 12px;background:#f5f5f5;font-weight:bold;width:40%">Email</td>
                        <td style="padding:8px 12px;border:1px solid #ddd">{email}</td>
                    </tr>
                    <tr>
                        <td style="padding:8px 12px;background:#f5f5f5;font-weight:bold">Contrasenia temporal</td>
                        <td style="padding:8px 12px;border:1px solid #ddd;font-family:monospace;font-size:16px;letter-spacing:2px">{password_temporal}</td>
                    </tr>
                </table>
                <p style="color:#cc0000;font-size:13px"><strong>Debes cambiar esta contrasena en tu primer inicio de sesion.</strong></p>
                <p style="text-align:center;margin:24px 0">
                    <a href="{login_url}"
                       style="background:#003366;color:#fff;padding:12px 28px;border-radius:6px;text-decoration:none;font-weight:bold">
                        Iniciar sesion
                    </a>
                </p>
                <hr style="border:none;border-top:1px solid #eee;margin-top:24px">
                <p style="color:#999;font-size:11px">FAMA - Plataforma de la comunidad militar</p>
            </div>
            """,
        })
        return True
    except Exception as exc:
        current_app.logger.error("Error enviando email de aprobacion a %s: %s", email, exc)
        return False


def enviar_verificacion_email(email: str, nombre: str) -> bool:
    """
    Envia el email de verificacion de cuenta.
    Devuelve True si el envio fue exitoso, False si fallo.
    """
    token = generar_token_verificacion(email)
    app_url = current_app.config.get("APP_URL", "http://localhost:5000").rstrip("/")
    enlace = f"{app_url}/auth/verificar-email/{token}"

    resend.api_key = current_app.config["RESEND_API_KEY"]

    try:
        resend.Emails.send({
            "from": current_app.config["MAIL_FROM"],
            "to": [email],
            "subject": "FAMA - Verifica tu correo electronico",
            "html": f"""
            <div style="font-family:Arial,sans-serif;max-width:520px;margin:auto;padding:24px;border:1px solid #e0e0e0;border-radius:8px">
                <h2 style="color:#003366">Bienvenido a FAMA, {nombre}</h2>
                <p>Para completar tu registro, verifica tu direccion de correo haciendo clic en el boton:</p>
                <p style="text-align:center;margin:32px 0">
                    <a href="{enlace}"
                       style="background:#003366;color:#fff;padding:12px 28px;border-radius:6px;text-decoration:none;font-weight:bold">
                        Verificar mi correo
                    </a>
                </p>
                <p style="color:#666;font-size:13px">
                    El enlace expira en <strong>24 horas</strong>.<br>
                    Si no creaste esta cuenta, ignora este mensaje.
                </p>
                <hr style="border:none;border-top:1px solid #eee;margin-top:24px">
                <p style="color:#999;font-size:11px">FAMA - Plataforma de la comunidad militar</p>
            </div>
            """,
        })
        return True
    except Exception as exc:
        current_app.logger.error("Error enviando email de verificacion a %s: %s", email, exc)
        return False
