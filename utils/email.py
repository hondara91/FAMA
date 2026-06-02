"""
utils/email.py - Envio de emails transaccionales via Resend.
"""
import resend
from flask import current_app


def enviar_pendiente_validacion(email: str, nombre: str) -> bool:
    """
    Notifica al usuario que su solicitud de registro ha sido recibida
    y esta pendiente de aprobacion por el administrador.
    """
    resend.api_key = current_app.config["RESEND_API_KEY"]

    try:
        resend.Emails.send({
            "from": current_app.config["MAIL_FROM"],
            "to": [email],
            "subject": "FAMA - Solicitud de registro recibida",
            "html": f"""
            <div style="font-family:Arial,sans-serif;max-width:520px;margin:auto;padding:24px;border:1px solid #e0e0e0;border-radius:8px">
                <h2 style="color:#003366">Hola, {nombre}</h2>
                <p>Hemos recibido tu solicitud de acceso a la plataforma <strong>FAMA</strong>.</p>
                <p>Tu cuenta esta <strong>pendiente de validacion</strong> por parte del administrador.
                Este proceso puede durar unas horas.</p>
                <p>Cuando tu cuenta sea aprobada recibiras otro correo con tus credenciales de acceso.</p>
                <hr style="border:none;border-top:1px solid #eee;margin-top:24px">
                <p style="color:#999;font-size:11px">FAMA - Plataforma de la comunidad militar</p>
            </div>
            """,
        })
        return True
    except Exception as exc:
        current_app.logger.error("Error enviando email de pendiente a %s: %s", email, exc)
        return False


def enviar_aprobacion_cuenta(email: str, nombre: str) -> bool:
    """
    Notifica al usuario que su cuenta ha sido aprobada e indica
    la contrasena por defecto con la que debe hacer login por primera vez.
    """
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
                <p>Inicia sesion con tu email y la siguiente contrasena temporal:</p>
                <p style="text-align:center;margin:24px 0">
                    <span style="font-family:monospace;font-size:22px;letter-spacing:3px;background:#f5f5f5;padding:10px 24px;border-radius:6px;border:1px solid #ddd">fama1234</span>
                </p>
                <p style="color:#cc0000;font-size:13px"><strong>Debes cambiar esta contrasena en tu primer inicio de sesion.</strong></p>
                <hr style="border:none;border-top:1px solid #eee;margin-top:24px">
                <p style="color:#999;font-size:11px">FAMA - Plataforma de la comunidad militar</p>
            </div>
            """,
        })
        return True
    except Exception as exc:
        current_app.logger.error("Error enviando email de aprobacion a %s: %s", email, exc)
        return False
