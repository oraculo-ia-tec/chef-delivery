"""
Script para gerar novos tokens OAuth do Gmail.

Execute este script quando receber o erro:
  'invalid_grant: Bad Request'

Isso acontece quando o refresh_token expirou (comum em apps em modo "teste").
"""

import json
import os
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

import requests
from dotenv import load_dotenv

load_dotenv()

# Configurações do OAuth
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8502")
PORT = int(os.getenv("GOOGLE_AUTH_PORT", "8502"))
TOKEN_FILE = os.getenv("GOOGLE_TOKEN_FILE", "./tokens.json")

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.insert",
]

authorization_code = None


class OAuthHandler(BaseHTTPRequestHandler):
    """Handler para capturar o código de autorização."""
    
    def do_GET(self):
        global authorization_code
        query = urlparse(self.path).query
        params = parse_qs(query)
        
        if "code" in params:
            authorization_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <head><title>Sucesso!</title></head>
                <body style="font-family:Arial;text-align:center;padding:50px;">
                    <h1 style="color:green;">Autorizado com sucesso!</h1>
                    <p>Pode fechar esta janela e voltar ao terminal.</p>
                </body>
                </html>
            """)
        else:
            error = params.get("error", ["Erro desconhecido"])[0]
            self.send_response(400)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"""
                <html>
                <head><title>Erro</title></head>
                <body style="font-family:Arial;text-align:center;padding:50px;">
                    <h1 style="color:red;">Erro na autorização</h1>
                    <p>{error}</p>
                </body>
                </html>
            """.encode())
    
    def log_message(self, format, *args):
        pass  # Suprime logs do servidor


def gerar_url_autorizacao():
    """Gera a URL de autorização do Google OAuth."""
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",  # Força a geração de novo refresh_token
    }
    query = "&".join(f"{k}={requests.utils.quote(str(v))}" for k, v in params.items())
    return f"{base_url}?{query}"


def trocar_codigo_por_tokens(code: str) -> dict:
    """Troca o código de autorização por tokens."""
    response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
        },
    )
    response.raise_for_status()
    return response.json()


def main():
    global authorization_code
    
    print("=" * 60)
    print("  GERADOR DE TOKEN GMAIL OAUTH")
    print("=" * 60)
    
    # Validar variáveis
    if not CLIENT_ID or not CLIENT_SECRET:
        print("\n❌ ERRO: GOOGLE_CLIENT_ID e GOOGLE_CLIENT_SECRET não configurados no .env")
        return
    
    print(f"\n📧 Client ID: {CLIENT_ID[:30]}...")
    print(f"🔗 Redirect URI: {REDIRECT_URI}")
    print(f"📁 Token File: {TOKEN_FILE}")
    
    # Gerar URL e abrir navegador
    auth_url = gerar_url_autorizacao()
    print(f"\n🌐 Abrindo navegador para autorização...")
    print(f"\nSe não abrir automaticamente, acesse:")
    print(auth_url)
    
    webbrowser.open(auth_url)
    
    # Iniciar servidor para capturar callback
    print(f"\n⏳ Aguardando autorização na porta {PORT}...")
    server = HTTPServer(("127.0.0.1", PORT), OAuthHandler)
    server.handle_request()
    
    if not authorization_code:
        print("\n❌ Não foi possível obter o código de autorização.")
        return
    
    print("\n✅ Código de autorização recebido!")
    print("🔄 Trocando por tokens...")
    
    try:
        tokens = trocar_codigo_por_tokens(authorization_code)
        
        # Salvar tokens no arquivo
        with open(TOKEN_FILE, "w") as f:
            json.dump(tokens, f, indent=2)
        
        print(f"\n✅ Tokens salvos em: {TOKEN_FILE}")
        
        # Mostrar refresh_token para adicionar ao .env
        refresh_token = tokens.get("refresh_token")
        if refresh_token:
            print("\n" + "=" * 60)
            print("  IMPORTANTE: Atualize seu arquivo .env")
            print("=" * 60)
            print(f"\nGMAIL_REFRESH_TOKEN={refresh_token}")
            print("\n" + "=" * 60)
        else:
            print("\n⚠️  Aviso: refresh_token não retornado (pode já existir no tokens.json)")
            
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ Erro ao trocar código por tokens: {e}")
        print(e.response.text)


if __name__ == "__main__":
    main()
