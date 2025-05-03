import time
import random
import questionary
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

ASCII_ART = """
Instagram Report Tool 
   _____
  /     \\
 /_______\\
 |  L    | 
 |    U | 
 |_______|
#Luannkzx
"""


def init_browser():
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
  
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def login(driver, username, password):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(random.uniform(2, 4))
    
    try:
        driver.find_element(By.NAME, "username").send_keys(username)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(random.uniform(3, 5))
        return True
    except Exception as e:
        print(f"Erro ao fazer login: {e}")
        return False

def report_profile(driver, profile_url, reason):
    driver.get(profile_url)
    time.sleep(random.uniform(2, 4))
    
    try:
       
        driver.find_element(By.XPATH, "//button[@aria-label='More options']").click()
        time.sleep(random.uniform(1, 2))
        
       
        driver.find_element(By.XPATH, "//button[contains(text(), 'Report')]").click()
        time.sleep(random.uniform(1, 2))
        
        
        reasons_map = {
            "Spam": "//button[contains(text(), 'It’s spam')]",
            "Inappropriate": "//button[contains(text(), 'It’s inappropriate')]",
            "Account": "//button[contains(text(), 'Report account')]"
        }
        
        if reason in reasons_map:
            driver.find_element(By.XPATH, reasons_map[reason]).click()
            time.sleep(random.uniform(1, 2))
            
            
            driver.find_element(By.XPATH, "//button[contains(text(), 'Submit Report')]").click()
            return True, f"Denúncia por '{reason}' enviada com sucesso!"
        else:
            return False, f"Motivo '{reason}' não suportado."
    except Exception as e:
        return False, f"Erro ao denunciar por '{reason}': {e}"

# Função para painel interativo
def interactive_panel():
    print(ASCII_ART)
    print("AVISO: Use apenas para testes éticos em contas de teste com permissão.")
    
   
    username = questionary.text("Digite seu usuário do Instagram:").ask()
    password = questionary.password("Digite sua senha do Instagram:").ask()
    
    
    profile_url = questionary.text("Digite a URL do perfil a ser denunciado (ex.: https://www.instagram.com/teste/):").ask()
    
    
    reasons = questionary.checkbox(
        "Selecione os motivos para denúncia:",
        choices=["Spam", "Inappropriate", "Fake Account"]
    ).ask()
    
    if not reasons:
        print("Nenhum motivo selecionado. Encerrando...")
        return
    
    # Inicializa o navegador
    driver = init_browser()
    try:
        # Faz login
        if not login(driver, username, password):
            print("Falha no login. Verifique suas credenciais.")
            return
        
        # Realiza denúncias
        print("\n📢 Iniciando denúncias...")
        for reason in reasons:
            success, message = report_profile(driver, profile_url, reason)
            print(f"[{reason}] {message}")
            time.sleep(random.uniform(5, 10))  # Pausa para evitar detecção
        
        print("\n✅ Teste concluído!")
    finally:
        driver.quit()

if __name__ == "__main__":
    try:
        interactive_panel()
    except KeyboardInterrupt:
        print("\n🚫 Script interrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
