# DBS SMS Gateway for Home Assistant

[PL] **DBS SMS** to zgodna z HACS integracja dla Home Assistant, która umożliwia wysyłanie wiadomości SMS za pomocą różnych polskich i międzynarodowych bramek API. Aktualnie wtyczka w pełni wspiera serwis **HostedSMS.pl**, a jej modułowa architektura pozwala na łatwe dodawanie kolejnych dostawców w przyszłości.

[EN] **DBS SMS** is a HACS-compatible integration for Home Assistant that allows sending SMS notifications via various Polish and international API gateways. Currently, it fully supports the **HostedSMS.pl** gateway, with a modular design that makes it easy to add more providers in the future.

---

## Główne Funkcje / Features

* 📱 **Wielu odbiorców w jednej akcji (Multi-recipient)**: Możliwość wysyłania jednej wiadomości do wielu numerów jednocześnie (wspierane natywnie przez API).
* ⚙️ **Brak konfiguracji YAML (Config Flow)**: Łatwe dodawanie i konfiguracja integracji bezpośrednio z poziomu interfejsu graficznego Home Assistant (UI).
* 🔄 **Automatyczny Failover (Kopia zapasowa)**: Integracja automatycznie przełącza się na zapasowy serwer API dostawcy (np. `api2.hostedsms.pl`), jeśli główny serwer jest nieosiągalny.
* 📊 **Sensory Diagnostyczne**:
  * `sensor.dbs_sms_balance` – Ilość pozostałych SMS-ów na koncie.
  * `sensor.dbs_sms_account_expiry` – Data ważności doładowania konta (z pełną obsługą stref czasowych).
* ⚡ **Natychmiastowe odświeżenie**: Stan pozostałych SMS-ów na koncie jest aktualizowany w tle natychmiast po wysłaniu nowej wiadomości.
* 🛠️ **Akcja `dbs_sms.send_sms`**: Dedykowana akcja z pełnym wsparciem szablonów Jinja2 (np. pobieranie temperatur z innych sensorów bezpośrednio w treści wiadomości).

---

## Instalacja / Installation

### Krok 1: Dodanie repozytorium do HACS / Step 1: Add Custom Repository to HACS
1. W Home Assistant przejdź do sekcji **HACS** -> **Integracje** (Integrations).
2. Kliknij ikonę trzech kropek w prawym górnym rogu i wybierz **Niestandardowe repozytoria** (Custom repositories).
3. Wklej URL do tego repozytorium i jako kategorię wybierz **Integracja** (Integration).
4. Kliknij **Dodaj** (Add) i zainstaluj integrację **DBS SMS**.
5. Zrestartuj Home Assistant.

### Krok 2: Konfiguracja w UI / Step 2: Configuration via UI
1. Przejdź do **Ustawienia** (Settings) -> **Urządzenia oraz usługi** (Devices & services).
2. Kliknij **Dodaj integrację** (Add integration) w prawym dolnym rogu.
3. Wyszukaj **DBS SMS**.
4. Wybierz dostawcę (np. **HostedSMS.pl**).
5. Podaj swoje dane logowania do serwisu i kliknij **Zatwierdź**.

---

## Użycie w automatyzacjach (Przykłady) / Automation Examples

### Wysłanie powiadomienia o temperaturze do wielu osób
Poniższy przykład pokazuje, jak wywołać akcję w automatyzacji z użyciem szablonów:

```yaml
action: dbs_sms.send_sms
data:
  message: >-
    Alert! Temperatura w szklarni wynosi {{ states('sensor.szklarnia_temperature') }}°C.
    Sprawdź ogrzewanie!
  targets:
    - "48501502503"
    - "48502503504"
  sender: "INFO" # Opcjonalny nadpis nadawcy
```

### Użycie z poziomu skryptu (pojedynczy odbiorca jako tekst)
```yaml
action: dbs_sms.send_sms
data:
  message: "Testowa wiadomość z Home Assistant"
  targets: "48501502503"
```

---

## Przyszłe Wsparcie / Future Providers
Integracja została zaprojektowana w sposób modułowy. Jeśli planujesz dodać innego dostawcę (np. SMSAPI, Twilio), wystarczy zaimplementować nową klasę w katalogu `custom_components/dbs_sms/providers/` dziedziczącą po `BaseSMSProvider`.
