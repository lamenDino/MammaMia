import json
import requests
from urllib.parse import urlparse

def get_domains(pastebin_url):
    try:
        response = requests.get(pastebin_url)
        response.raise_for_status()
        domains = response.text.strip().split('\n')
        domains = [domain.strip().replace('\r', '') for domain in domains]
        return domains
    except requests.RequestException as e:
        print(f"❌ Errore durante il recupero dei domini: {e}")
        return []

def extract_full_domain(domain, site_key):
    parsed_url = urlparse(domain)
    scheme = parsed_url.scheme if parsed_url.scheme else 'https'
    netloc = parsed_url.netloc or parsed_url.path

    if site_key in ['Tantifilm', 'StreamingWatch']:
        if not netloc.startswith('www.'):
            netloc = 'www.' + netloc
        return f"{scheme}://{netloc}"
    else:
        return f"{scheme}://{netloc}"

def extract_tld(domain_url):
    parsed = urlparse(domain_url)
    netloc = parsed.netloc or parsed.path
    if '.' in netloc:
        return netloc.split('.')[-1]
    return ''

def check_redirect(domain, site_key):
    if not domain.startswith(('http://', 'https://')):
        domain = 'http://' + domain

    try:
        response = requests.get(domain, allow_redirects=True)
        final_url = response.url
        final_domain = extract_full_domain(final_url, site_key)
        return domain, final_domain
    except requests.RequestException as e:
        return domain, f"Error: {str(e)}"

def update_json_file():
    try:
        with open('config.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        print("❌ Errore: Il file config.json non è stato trovato.")
        return
    except json.JSONDecodeError:
        print("❌ Errore: Il file config.json non è un JSON valido.")
        return

    pastebin_url = 'https://pastebin.com/raw/HFx8qvKF'
    domain_list = get_domains(pastebin_url)

    if len(domain_list) < 13:
        print("❌ Lista dei domini troppo corta. Controlla il Pastebin, fratm.")
        return

    site_mapping = {
        'StreamingCommunity': domain_list[0],
        'Filmpertutti': domain_list[1],
        'Tantifilm': domain_list[2],
        'LordChannel': domain_list[3],
        'StreamingWatch': domain_list[4],
        'CB01': domain_list[5],
        'DDLStream': domain_list[6],
        'Guardaserie': domain_list[7],
        'GuardaHD': domain_list[8],
        'Onlineserietv': domain_list[9],
        'AnimeWorld': domain_list[10],
        'SkyStreaming': domain_list[11],
        'DaddyLiveHD': domain_list[12],
    }

    for site_key, domain_url in site_mapping.items():
        if site_key in data['Siti']:
            original, final_domain = check_redirect(domain_url, site_key)
            if "Error" in final_domain:
                print(f"❌ Errore nel redirect di {original}: {final_domain}")
                continue

            # Aggiorna l'URL del sito
            data['Siti'][site_key]['url'] = final_domain
            print(f"✅ Aggiornato {site_key}: {final_domain}")

            # Per onlineserietv estrai il TLD
            if site_key == 'Onlineserietv':
                tld = extract_tld(final_domain)
                data['Siti'][site_key]['domain'] = tld
                print(f"🧠 Dominio TLD per Onlineserietv: {tld}")

            # Aggiorna i cookies se servono
            if 'cookies' in data['Siti'][site_key]:
                cookies = data['Siti'][site_key]['cookies']
                updated = False
                for key in ['ips4_device_key', 'ips4_IPSSessionFront', 'ips4_member_id', 'ips4_login_key']:
                    if cookies.get(key) is None:
                        updated = True
                        if key == 'ips4_device_key':
                            cookies[key] = "1496c03312d318b557ff53512202e757"
                        elif key == 'ips4_IPSSessionFront':
                            cookies[key] = "d9ace0029696972877e2a5e3614a333b"
                        elif key == 'ips4_member_id':
                            cookies[key] = "d9ace0029696972877e2a5e3614a333b"
                        elif key == 'ips4_login_key':
                            cookies[key] = "71a501781ba479dfb91b40147e637daf"
                if updated:
                    print(f"🍪 Cookies aggiornati per {site_key} – benedetti siano, porco mondo.")

    try:
        with open('config.json', 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print("💾 File config.json aggiornato con successo! Alleluja!")
    except Exception as e:
        print(f"❌ Errore durante il salvataggio del file JSON: {e}")

if __name__ == '__main__':
    update_json_file()
