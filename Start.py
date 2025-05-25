# main.py
import discord
from discord import app_commands
import requests
import re
from urllib.parse import urlparse
import asyncio
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Token do bot (INSIRA SEU TOKEN AQUI)
DISCORD_TOKEN = 'INSIRA_SEU_TOKEN_AQUI'  # Substitua por seu token do Discord Developer Portal

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# Funções de Varredura de Vulnerabilidades
def test_sql_injection(url):
    payloads = ["' OR '1'='1", "' OR '1'='1' --"]
    for payload in payloads:
        try:
            test_url = f"{url}?id={payload}"
            response = requests.get(test_url, timeout=5)
            if "mysql" in response.text.lower() or "sql syntax" in response.text.lower():
                return True
        except:
            pass
    return False

def test_xss(url):
    payloads = ["<script>alert('xss')</script>", "<img src=x onerror=alert('xss')>"]
    for payload in payloads:
        try:
            test_url = f"{url}?q={payload}"
            response = requests.get(test_url, timeout=5)
            if payload in response.text:
                return True
        except:
            pass
    return False

def test_csrf(url):
    try:
        response = requests.get(url, timeout=5)
        if "csrf" not in response.text.lower() and "<form" in response.text.lower():
            return True
        return False
    except:
        return False

def test_directory_traversal(url):
    payloads = ["../../etc/passwd", "../windows/win.ini"]
    for payload in payloads:
        try:
            test_url = f"{url}/{payload}"
            response = requests.get(test_url, timeout=5)
            if "root:x" in response.text or "[extensions]" in response.text:
                return True
        except:
            pass
    return False

def test_security_headers(url):
    try:
        response = requests.get(url, timeout=5)
        headers = response.headers
        missing_headers = []
        if "X-Content-Type-Options" not in headers or headers["X-Content-Type-Options"] != "nosniff":
            missing_headers.append("X-Content-Type-Options")
        if "X-Frame-Options" not in headers or headers["X-Frame-Options"] not in ["DENY", "SAMEORIGIN"]:
            missing_headers.append("X-Frame-Options")
        if missing_headers:
            return True
        return False
    except:
        return False

def scan_vulnerabilities(url):
    print(f"[*] Iniciando varredura em {url}")
    results = {
        "SQL Injection": test_sql_injection(url),
        "XSS": test_xss(url),
        "CSRF": test_csrf(url),
        "Directory Traversal": test_directory_traversal(url),
        "Security Headers": test_security_headers(url)
    }
    return results

# Evento de Inicialização
@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    await bot.change_presence(activity=discord.Game(name='🔐 Scanner Ético | /scan'))
    try:
        synced = await tree.sync()
        print(f'Sincronizados {len(synced)} comandos de barra.')
    except Exception as e:
        print(f'Erro ao sincronizar comandos: {e}')

# Comando /scan
@tree.command(name='scan', description='Inicia uma varredura de vulnerabilidades em uma URL')
async def scan(interaction: discord.Interaction):
    # Criar modal para entrada de URL
    modal = discord.ui.Modal(title='🔐 Scanner de Vulnerabilidades')
    modal.add_item(discord.ui.TextInput(
        label='Digite a URL (ex: http://exemplo.com)',
        custom_id='target_url',
        placeholder='http://exemplo.com',
        required=True
    ))
    
    async def on_submit(interaction: discord.Interaction):
        url = interaction.data['components'][0]['components'][0]['value']
        # Validar URL
        if not url.startswith(('http://', 'https://')):
            await interaction.response.send_message('⚠️ URL inválida! Use http:// ou https://', ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        # Executar varredura
        results = scan_vulnerabilities(url)
        
        # Criar embed com resultados
        embed = discord.Embed(title='📡 Relatório de Vulnerabilidades', color=0x00FF00)
        embed.description = f'**URL**: {url}\n⚠️ **AVISO**: Use apenas com permissão explícita!\n\n'
        for test, result in results.items():
            status = '🛡️ Seguro' if not result else '⚠️ Vulnerável'
            embed.add_field(name=test, value=status, inline=False)
        embed.set_footer(text='SauronNET - Scanner Ético | Use com responsabilidade')

        await interaction.followup.send(embed=embed, ephemeral=True)

    modal.on_submit = on_submit
    await interaction.response.send_modal(modal)

# Comando /help
@tree.command(name='help', description='Mostra como usar o bot')
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title='📚 Ajuda do Scanner Bot', color=0x00FF00)
    embed.description = (
        'Use `/scan` para iniciar uma varredura de vulnerabilidades em uma URL.\n\n'
        '**Funcionalidades**:\n'
        '- **SQL Injection**: Testa payloads comuns.\n'
        '- **XSS**: Verifica scripts injetados.\n'
        '- **CSRF**: Checa tokens de proteção.\n'
        '- **Directory Traversal**: Busca acesso a arquivos sensíveis.\n'
        '- **Cabeçalhos de Segurança**: Verifica configurações HTTP.\n\n'
        '⚠️ **AVISO**: Use apenas com permissão explícita do proprietário do site!'
    )
    embed.set_footer(text='SauronNET - Scanner Ético')
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Iniciar bot
async def main():
    await bot.start(DISCORD_TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
