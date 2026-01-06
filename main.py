import requests
import os
import glob

# Configurações
ARQUIVO_SAIDA = 'lista_final_online.m3u8'
TIMEOUT = 5 
# User-Agent para evitar bloqueios de alguns servidores
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def validar_links_automatico():
    links_vistos = set()
    canais_validos = []
    
    # Busca por todos os arquivos .m3u e .m3u8 na pasta atual
    arquivos_m3u = glob.glob("*.m3u") + glob.glob("*.m3u8")
    
    # Remove o arquivo de saída da lista de leitura para evitar loop infinito
    if ARQUIVO_SAIDA in arquivos_m3u:
        arquivos_m3u.remove(ARQUIVO_SAIDA)

    if not arquivos_m3u:
        print("Nenhum arquivo .m3u ou .m3u8 encontrado na pasta.")
        return

    print(f"--- Encontrados {len(arquivos_m3u)} arquivos para processar ---")

    for arquivo in arquivos_m3u:
        print(f"\nProcessando arquivo: {arquivo}")
        try:
            with open(arquivo, 'r', encoding='utf-8', errors='ignore') as f:
                linhas = f.readlines()
        except Exception as e:
            print(f"Erro ao ler {arquivo}: {e}")
            continue

        nome_canal = "#EXTINF:-1, Canal Sem Nome"
        for linha in linhas:
            linha = linha.strip()
            
            if linha.startswith('#EXTINF'):
                nome_canal = linha
            
            elif linha.startswith('http'):
                url = linha
                
                # Validação de Duplicatas
                if url not in links_vistos:
                    try:
                        # Requisição HEAD para verificar status
                        response = requests.head(url, timeout=TIMEOUT, headers=HEADERS, allow_redirects=True)
                        
                        if response.status_code == 200:
                            print(f"  [ON]  {url}")
                            canais_validos.append(f"{nome_canal}\n{url}")
                            links_vistos.add(url)
                        else:
                            print(f"  [OFF] Status {response.status_code} - {url}")
                            
                    except Exception:
                        print(f"  [OFF] Timeout/Erro - {url}")
                else:
                    print(f"  [DUP] Link já processado: {url}")

    # Salva o resultado final
    with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for canal in canais_validos:
            f.write(f"{canal}\n")
    
    print(f"\n" + "="*30)
    print(f"CONCLUÍDO!")
    print(f"Canais únicos online encontrados: {len(canais_validos)}")
    print(f"Arquivo gerado: {ARQUIVO_SAIDA}")
    print("="*30)

if __name__ == "__main__":
    validar_links_automatico()