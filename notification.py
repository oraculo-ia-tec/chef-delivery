import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from config import (
    EMAIL_REMETENTE,
    GMAIL_REFRESH_TOKEN,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_OAUTH_SCOPES,
)


class Notificador:
    def __init__(self):
        self.email_remetente = EMAIL_REMETENTE
        self.client_id = GOOGLE_CLIENT_ID
        self.client_secret = GOOGLE_CLIENT_SECRET
        self.refresh_token = GMAIL_REFRESH_TOKEN
        self.scopes = self._normalizar_scopes(GOOGLE_OAUTH_SCOPES)
        self._validar_variaveis()

    @staticmethod
    def _normalizar_scopes(raw: Any) -> list[str]:
        if not raw:
            return ["https://www.googleapis.com/auth/gmail.send"]

        if isinstance(raw, (list, tuple, set)):
            values = [str(item).strip() for item in raw if str(item).strip()]
            return values or ["https://www.googleapis.com/auth/gmail.send"]

        texto = str(raw)
        texto = texto.replace("[", " ").replace("]", " ").replace("(", " ").replace(")", " ")
        partes = [p.strip().strip('"').strip("'") for p in texto.split()]
        scopes = [p for p in partes if p.startswith("https://www.googleapis.com/auth/")]
        return scopes or ["https://www.googleapis.com/auth/gmail.send"]

    def _validar_variaveis(self) -> None:
        faltantes = []
        if not self.email_remetente:
            faltantes.append("EMAIL_REMETENTE")
        if not self.client_id:
            faltantes.append("GOOGLE_CLIENT_ID")
        if not self.client_secret:
            faltantes.append("GOOGLE_CLIENT_SECRET")
        if not self.refresh_token:
            faltantes.append("GMAIL_REFRESH_TOKEN")
        if faltantes:
            raise ValueError(
                "Variáveis obrigatórias ausentes para Gmail API: " + ", ".join(faltantes)
            )

    def _credenciais(self) -> Credentials:
        creds = Credentials(
            token=None,
            refresh_token=self.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=self.scopes,
        )
        creds.refresh(Request())
        return creds

    def _service(self):
        return build("gmail", "v1", credentials=self._credenciais())

    def enviar_email(self, destino: str, assunto: str, mensagem: str) -> dict:
        if not destino:
            raise ValueError("Destino do e-mail é obrigatório.")

        email = MIMEMultipart("alternative")
        email["to"] = destino
        email["from"] = self.email_remetente
        email["subject"] = assunto
        email.attach(MIMEText(mensagem, "html", "utf-8"))

        raw = base64.urlsafe_b64encode(email.as_bytes()).decode()
        service = self._service()
        retorno = service.users().messages().send(userId="me", body={"raw": raw}).execute()
        return retorno

    def testar_envio(self, destino: str) -> dict:
        mensagem = """
        <div style='font-family:Arial,sans-serif;max-width:560px;margin:auto;padding:24px;border:1px solid #e5e7eb;border-radius:14px;'>
            <h2 style='margin:0 0 12px;color:#0f766e;'>Teste de e-mail</h2>
            <p style='margin:0 0 10px;'>Se você recebeu esta mensagem, a integração Gmail API do Chef Delivery está funcionando.</p>
            <p style='margin:0;color:#475569;'>Ambiente validado para testes locais e Streamlit Cloud.</p>
        </div>
        """
        return self.enviar_email(destino=destino, assunto="Chef Delivery - Teste de e-mail", mensagem=mensagem)
