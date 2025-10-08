import requests
from bs4 import BeautifulSoup
import datetime

# --- Konfiguracja ---
WIBOR_URL = 'https://www.bankier.pl/mieszkaniowe/stopy-procentowe/wibor'
ODSETKI_URL = 'https://wskazniki.gofin.pl/wskaznik/70/odsetki-ustawowe'
HTML_FILE = 'index.html'

def get_wibor_rates():
    """Pobiera i parsuje stawki WIBOR ze strony bankier.pl."""
    try:
        response = requests.get(WIBOR_URL)
        response.raise_for_status() # Sprawdza czy zapytanie się udało
        soup = BeautifulSoup(response.text, 'html.parser')
        
        rates = {}
        # Znajdź tabelę z danymi
        table = soup.find('table', class_='profilLast')
        rows = table.find_all('tr')

        for row in rows:
            cells = row.find_all('td')
            if len(cells) > 1:
                name = cells[0].text.strip()
                value = cells[1].text.strip() + '%'
                
                if 'WIBOR 1M' in name:
                    rates['WIBOR_1M'] = value
                elif 'WIBOR 3M' in name:
                    rates['WIBOR_3M'] = value
                elif 'WIBOR 6M' in name:
                    rates['WIBOR_6M'] = value
        
        if len(rates) < 3:
            print("Błąd: Nie znaleziono wszystkich stawek WIBOR.")
            return None
            
        print(f"Pobrano WIBOR: {rates}")
        return rates
    except Exception as e:
        print(f"Wystąpił błąd podczas pobierania stawek WIBOR: {e}")
        return None

def get_interest_rate():
    """Pobiera i parsuje stawkę odsetek za opóźnienie z gofin.pl."""
    try:
        response = requests.get(ODSETKI_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Znajdź tabelę o ID 'p_wsk_70_0'
        table = soup.find('table', id='p_wsk_70_0')
        rows = table.find_all('tr')
        
        # Szukamy wiersza, który zawiera tekst 'Odsetki ustawowe za opóźnienie'
        for row in rows:
            if 'Odsetki ustawowe za opóźnienie' in row.text:
                # Wartość jest w drugiej komórce 'td'
                value_cell = row.find_all('td')[1]
                value = value_cell.text.strip() + '%'
                print(f"Pobrano odsetki za opóźnienie: {value}")
                return value
        
        print("Błąd: Nie znaleziono stawki odsetek za opóźnienie.")
        return None
    except Exception as e:
        print(f"Wystąpił błąd podczas pobierania odsetek: {e}")
        return None


def update_html_file(wibor_data, interest_data):
    """Aktualizuje plik HTML podmieniając znaczniki na nowe dane."""
    if not wibor_data or not interest_data:
        print("Brak danych do aktualizacji. Przerywam.")
        return

    try:
        with open(HTML_FILE, 'r', encoding='utf-8') as f:
            content = f.read()

        content = content.replace('%%WIBOR_1M%%', wibor_data['WIBOR_1M'])
        content = content.replace('%%WIBOR_3M%%', wibor_data['WIBOR_3M'])
        content = content.replace('%%WIBOR_6M%%', wibor_data['WIBOR_6M'])
        content = content.replace('%%ODSETKI_OPOZNIENIE%%', interest_data)

        with open(HTML_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Plik {HTML_FILE} został pomyślnie zaktualizowany.")
    except Exception as e:
        print(f"Wystąpił błąd podczas aktualizacji pliku HTML: {e}")


if __name__ == '__main__':
    wibor_rates = get_wibor_rates()
    interest_rate = get_interest_rate()
    update_html_file(wibor_rates, interest_rate)
