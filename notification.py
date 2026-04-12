import base64
import os
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


# ══════════════════════════════════════════════════════════════════════════════
# TEMPLATES DE E-MAIL - CHEF DELIVERY
# ══════════════════════════════════════════════════════════════════════════════

def _get_chef_image_base64() -> str:
    """Retorna a imagem do Chef em base64 para uso em emails."""
    # Tenta diferentes caminhos possíveis
    possible_paths = [
        "src/img/perfil-chat1.png",
        "./src/img/perfil-chat1.png",
        os.path.join(os.path.dirname(__file__), "src", "img", "perfil-chat1.png"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
            except Exception:
                continue
    
    # Se não encontrar, retorna uma imagem placeholder SVG em base64
    placeholder_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120">
        <circle cx="60" cy="60" r="58" fill="url(#grad)" stroke="#7af0b0" stroke-width="3"/>
        <defs><linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#1a1a2e;stop-opacity:1"/>
            <stop offset="100%" style="stop-color:#16213e;stop-opacity:1"/>
        </linearGradient></defs>
        <text x="60" y="70" font-size="40" text-anchor="middle" fill="#7af0b0">🍔</text>
    </svg>'''
    return base64.b64encode(placeholder_svg.encode()).decode()


def _get_profile_image_base64(imagem_perfil: str = None) -> str:
    """Retorna a imagem de perfil do usuário em base64."""
    if imagem_perfil:
        possible_paths = [
            f"src/img/profiles/{imagem_perfil}",
            f"./src/img/profiles/{imagem_perfil}",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, "rb") as f:
                        return base64.b64encode(f.read()).decode()
                except Exception:
                    continue
    
    # Avatar padrão em SVG
    default_avatar = '''<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 80 80">
        <circle cx="40" cy="40" r="38" fill="url(#avatar_grad)" stroke="#7af0b0" stroke-width="2"/>
        <defs><linearGradient id="avatar_grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:rgba(122,240,176,0.3)"/>
            <stop offset="100%" style="stop-color:rgba(94,200,255,0.3)"/>
        </linearGradient></defs>
        <text x="40" y="50" font-size="28" text-anchor="middle" fill="#7af0b0">👤</text>
    </svg>'''
    return base64.b64encode(default_avatar.encode()).decode()


def _email_base_template(content: str) -> str:
    """Template base para todos os emails do Chef Delivery."""
    chef_img = _get_chef_image_base64()
    
    return f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin:0;padding:0;background-color:#0d1117;font-family:'Segoe UI',Arial,sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0d1117;padding:20px 0;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">
                        <!-- Header com Logo -->
                        <tr>
                            <td align="center" style="padding:30px 20px;">
                                <img src="data:image/png;base64,{chef_img}" 
                                     alt="Chef Delivery" 
                                     style="width:100px;height:100px;border-radius:50%;border:3px solid #7af0b0;box-shadow:0 0 30px rgba(122,240,176,0.3);">
                            </td>
                        </tr>
                        
                        <!-- Conteúdo Principal -->
                        <tr>
                            <td style="background:linear-gradient(145deg,#1a1a2e,#16213e);border-radius:20px;padding:40px 30px;border:1px solid rgba(122,240,176,0.2);box-shadow:0 10px 40px rgba(0,0,0,0.3);">
                                {content}
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td align="center" style="padding:30px 20px;">
                                <p style="margin:0;color:#6b7280;font-size:12px;">
                                    © 2026 Chef Delivery — Carnes Premium na sua casa
                                </p>
                                <p style="margin:8px 0 0;color:#4b5563;font-size:11px;">
                                    Este é um e-mail automático. Por favor, não responda.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """


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

    def enviar_email_boas_vindas(
        self, 
        destino: str, 
        nome: str, 
        email_usuario: str, 
        whatsapp: str = None,
        imagem_perfil: str = None
    ) -> dict:
        """
        Envia e-mail de boas-vindas parabenizando o usuário pelo cadastro.
        
        Args:
            destino: E-mail do destinatário
            nome: Nome completo do usuário
            email_usuario: E-mail do usuário cadastrado
            whatsapp: Número de WhatsApp (opcional)
            imagem_perfil: Nome do arquivo de imagem de perfil (opcional)
        """
        primeiro_nome = nome.split(" ")[0] if nome else "Cliente"
        profile_img = _get_profile_image_base64(imagem_perfil)
        
        content = f"""
        <div style="text-align:center;margin-bottom:25px;">
            <h1 style="color:#7af0b0;margin:0;font-size:28px;font-weight:700;">
                🎉 Bem-vindo ao Chef Delivery!
            </h1>
            <p style="color:#c0d8e8;margin:10px 0 0;font-size:16px;">
                Estamos muito felizes em ter você conosco
            </p>
        </div>
        
        <div style="background:rgba(122,240,176,0.08);border-radius:16px;padding:25px;border:1px solid rgba(122,240,176,0.15);margin-bottom:25px;">
            <div style="text-align:center;margin-bottom:20px;">
                <img src="data:image/png;base64,{profile_img}" 
                     alt="Perfil" 
                     style="width:80px;height:80px;border-radius:50%;border:3px solid #7af0b0;box-shadow:0 0 20px rgba(122,240,176,0.2);">
            </div>
            
            <p style="color:#e8f4ee;font-size:16px;line-height:1.6;margin:0 0 15px;text-align:center;">
                Olá, <strong style="color:#7af0b0;">{primeiro_nome}</strong>! 👋
            </p>
            
            <p style="color:#c0d8e8;font-size:15px;line-height:1.7;margin:0 0 20px;text-align:center;">
                Parabéns por se cadastrar no <strong style="color:#7af0b0;">Chef Delivery</strong>! 
                Agora você tem acesso ao melhor açougue delivery da região, com carnes premium 
                selecionadas e entrega rápida na sua porta.
            </p>
        </div>
        
        <div style="background:rgba(30,40,60,0.5);border-radius:12px;padding:20px;margin-bottom:25px;">
            <h3 style="color:#7af0b0;margin:0 0 15px;font-size:16px;text-align:center;">
                📋 Seus Dados de Cadastro
            </h3>
            
            <table style="width:100%;border-collapse:collapse;">
                <tr>
                    <td style="padding:10px;color:#9ca3af;font-size:14px;border-bottom:1px solid rgba(122,240,176,0.1);">
                        👤 Nome
                    </td>
                    <td style="padding:10px;color:#e8f4ee;font-size:14px;text-align:right;border-bottom:1px solid rgba(122,240,176,0.1);">
                        <strong>{nome}</strong>
                    </td>
                </tr>
                <tr>
                    <td style="padding:10px;color:#9ca3af;font-size:14px;border-bottom:1px solid rgba(122,240,176,0.1);">
                        📧 E-mail
                    </td>
                    <td style="padding:10px;color:#7af0b0;font-size:14px;text-align:right;border-bottom:1px solid rgba(122,240,176,0.1);">
                        {email_usuario}
                    </td>
                </tr>
                {"<tr><td style='padding:10px;color:#9ca3af;font-size:14px;'>📱 WhatsApp</td><td style='padding:10px;color:#e8f4ee;font-size:14px;text-align:right;'>" + whatsapp + "</td></tr>" if whatsapp else ""}
            </table>
        </div>
        
        <div style="background:linear-gradient(135deg,rgba(122,240,176,0.15),rgba(94,200,255,0.1));border-radius:12px;padding:20px;margin-bottom:25px;">
            <h3 style="color:#7af0b0;margin:0 0 12px;font-size:15px;">
                🥩 O que você pode fazer agora:
            </h3>
            <ul style="color:#c0d8e8;margin:0;padding-left:20px;line-height:1.8;font-size:14px;">
                <li>Explorar nosso cardápio completo de carnes premium</li>
                <li>Fazer pedidos pelo chat com assistente inteligente</li>
                <li>Acompanhar suas entregas em tempo real</li>
                <li>Aproveitar ofertas exclusivas para clientes cadastrados</li>
            </ul>
        </div>
        
        <div style="text-align:center;">
            <p style="color:#6b7280;font-size:13px;margin:0;">
                Em breve você receberá um e-mail com o código de verificação 
                para ativar completamente sua conta.
            </p>
        </div>
        """
        
        mensagem = _email_base_template(content)
        
        return self.enviar_email(
            destino=destino,
            assunto="🎉 Bem-vindo ao Chef Delivery — Sua conta foi criada!",
            mensagem=mensagem
        )

    def enviar_codigo_verificacao(self, destino: str, nome: str, codigo: str) -> dict:
        """
        Envia e-mail com código de verificação para ativar a conta.
        
        Args:
            destino: E-mail do destinatário
            nome: Nome do usuário
            codigo: Código de verificação de 6 dígitos
        """
        primeiro_nome = nome.split(" ")[0] if nome else "Cliente"
        
        content = f"""
        <div style="text-align:center;margin-bottom:30px;">
            <h1 style="color:#7af0b0;margin:0;font-size:26px;font-weight:700;">
                Verificação de E-mail
            </h1>
            <p style="color:#c0d8e8;margin:12px 0 0;font-size:15px;">
                Estamos quase lá! Só mais um passo para ativar sua conta
            </p>
        </div>
        
        <div style="background:rgba(122,240,176,0.05);border-radius:16px;padding:30px 20px;margin-bottom:25px;text-align:center;">
            <p style="color:#e8f4ee;font-size:16px;margin:0 0 10px;">
                Olá, <strong style="color:#7af0b0;">{primeiro_nome}</strong>!
            </p>
            <p style="color:#9ca3af;font-size:14px;margin:0 0 25px;">
                Use o código abaixo para verificar seu e-mail e ativar sua conta no Chef Delivery
            </p>
            
            <div style="background:linear-gradient(145deg,#1e293b,#0f172a);border:2px solid rgba(122,240,176,0.4);border-radius:16px;padding:25px;display:inline-block;box-shadow:0 0 30px rgba(122,240,176,0.15);">
                <span style="font-size:36px;font-weight:800;letter-spacing:12px;color:#7af0b0;font-family:'Courier New',monospace;">
                    {codigo}
                </span>
            </div>
            
            <p style="color:#6b7280;font-size:12px;margin:20px 0 0;">
                ⏱️ Este código expira em 10 minutos
            </p>
        </div>
        
        <div style="background:rgba(30,40,60,0.4);border-radius:12px;padding:20px;margin-bottom:20px;">
            <h3 style="color:#7af0b0;margin:0 0 12px;font-size:14px;">
                📌 Como usar:
            </h3>
            <ol style="color:#c0d8e8;margin:0;padding-left:20px;line-height:1.8;font-size:13px;">
                <li>Volte para a tela de verificação no Chef Delivery</li>
                <li>Digite o código de 6 dígitos no campo indicado</li>
                <li>Clique em "Verificar" para ativar sua conta</li>
            </ol>
        </div>
        
        <div style="border-top:1px solid rgba(122,240,176,0.1);padding-top:20px;text-align:center;">
            <p style="color:#6b7280;font-size:12px;margin:0 0 8px;">
                🔒 Dica de segurança: Nunca compartilhe este código com ninguém.
            </p>
            <p style="color:#4b5563;font-size:11px;margin:0;">
                Se você não solicitou este cadastro, ignore este e-mail.
            </p>
        </div>
        """
        
        mensagem = _email_base_template(content)
        
        return self.enviar_email(
            destino=destino,
            assunto="🔐 Chef Delivery — Código de Verificação",
            mensagem=mensagem
        )

    def enviar_email_recuperacao(self, destino: str, nome: str, nova_senha: str) -> dict:
        """
        Envia e-mail com a nova senha gerada para recuperação de conta.
        
        Args:
            destino: E-mail do destinatário
            nome: Nome do usuário
            nova_senha: Nova senha gerada
        """
        primeiro_nome = nome.split(" ")[0] if nome else "Cliente"
        
        content = f"""
        <div style="text-align:center;margin-bottom:30px;">
            <h1 style="color:#7af0b0;margin:0;font-size:26px;font-weight:700;">
                Recuperação de Senha
            </h1>
            <p style="color:#c0d8e8;margin:12px 0 0;font-size:15px;">
                Sua nova senha foi gerada com sucesso
            </p>
        </div>
        
        <div style="background:rgba(122,240,176,0.05);border-radius:16px;padding:30px 20px;margin-bottom:25px;text-align:center;">
            <p style="color:#e8f4ee;font-size:16px;margin:0 0 10px;">
                Olá, <strong style="color:#7af0b0;">{primeiro_nome}</strong>!
            </p>
            <p style="color:#9ca3af;font-size:14px;margin:0 0 25px;">
                Recebemos sua solicitação de recuperação de senha. Use a senha abaixo para fazer login:
            </p>
            
            <div style="background:linear-gradient(145deg,#1e293b,#0f172a);border:2px solid rgba(122,240,176,0.4);border-radius:16px;padding:25px;display:inline-block;box-shadow:0 0 30px rgba(122,240,176,0.15);">
                <span style="font-size:24px;font-weight:700;letter-spacing:3px;color:#7af0b0;font-family:'Courier New',monospace;">
                    {nova_senha}
                </span>
            </div>
        </div>
        
        <div style="background:rgba(255,193,7,0.1);border:1px solid rgba(255,193,7,0.3);border-radius:12px;padding:15px;margin-bottom:20px;">
            <p style="color:#ffc107;font-size:13px;margin:0;text-align:center;">
                ⚠️ <strong>Importante:</strong> Por segurança, recomendamos que você altere 
                esta senha após o primeiro login acessando "Minha Conta".
            </p>
        </div>
        
        <div style="background:rgba(30,40,60,0.4);border-radius:12px;padding:20px;margin-bottom:20px;">
            <h3 style="color:#7af0b0;margin:0 0 12px;font-size:14px;">
                🔐 Dicas de segurança:
            </h3>
            <ul style="color:#c0d8e8;margin:0;padding-left:20px;line-height:1.8;font-size:13px;">
                <li>Use uma senha única que você não usa em outros sites</li>
                <li>Combine letras maiúsculas, minúsculas, números e símbolos</li>
                <li>Nunca compartilhe sua senha com terceiros</li>
            </ul>
        </div>
        
        <div style="border-top:1px solid rgba(122,240,176,0.1);padding-top:20px;text-align:center;">
            <p style="color:#4b5563;font-size:11px;margin:0;">
                Se você não solicitou esta recuperação, entre em contato conosco imediatamente.
            </p>
        </div>
        """
        
        mensagem = _email_base_template(content)
        
        return self.enviar_email(
            destino=destino,
            assunto="🔐 Chef Delivery — Nova Senha",
            mensagem=mensagem
        )

    def testar_envio(self, destino: str) -> dict:
        content = """
        <div style="text-align:center;margin-bottom:25px;">
            <h1 style="color:#7af0b0;margin:0;font-size:24px;">
                ✅ Teste de E-mail
            </h1>
        </div>
        
        <div style="background:rgba(122,240,176,0.08);border-radius:12px;padding:20px;text-align:center;">
            <p style="color:#e8f4ee;font-size:16px;margin:0 0 10px;">
                Parabéns! 🎉
            </p>
            <p style="color:#c0d8e8;font-size:14px;margin:0;">
                Se você recebeu esta mensagem, a integração com a Gmail API 
                do Chef Delivery está funcionando perfeitamente.
            </p>
        </div>
        
        <div style="margin-top:20px;text-align:center;">
            <p style="color:#6b7280;font-size:12px;margin:0;">
                Ambiente validado para testes locais e Streamlit Cloud.
            </p>
        </div>
        """
        
        mensagem = _email_base_template(content)
        
        return self.enviar_email(
            destino=destino, 
            assunto="✅ Chef Delivery — Teste de E-mail", 
            mensagem=mensagem
        )
