# DBS SMS (Home Assistant Integration)

Integracja dla Home Assistant umożliwiająca wysyłanie wiadomości SMS za pośrednictwem bramek API. Projekt został zaprojektowany z myślą o modułowości, dzięki czemu w przyszłości będzie wspierać wielu dostawców. Na ten moment wtyczka w pełni obsługuje serwis HostedSMS.pl.

## Funkcje

* **Konfiguracja przez interfejs (Config Flow)**: Pełna konfiguracja bez konieczności edycji plików YAML.
* **Wielu odbiorców jednocześnie**: Możliwość podania listy numerów telefonów w jednym wywołaniu usługi.
* **Sensory diagnostyczne**:
  * `sensor.dbs_sms_balance` – liczba pozostałych SMS-ów na koncie.
  * `sensor.dbs_sms_account_expiry` – data ważności doładowania konta (z obsługą strefy czasowej).
* **Automatyczny failover (HostedSMS)**: W przypadku niedostępności głównego serwera API (`api.hostedsms.pl`), integracja automatycznie przełącza się na serwer zapasowy (`api2.hostedsms.pl`).
* **Szybkie odświeżanie licznika**: Stan pozostałych SMS-ów na koncie jest aktualizowany w tle natychmiast po wysłaniu nowej wiadomości.

## Instalacja

### Krok 1: Dodanie repozytorium do HACS
1. W Home Assistant przejdź do sekcji **HACS** -> **Integracje** (Integrations).
2. Kliknij ikonę trzech kropek w prawym górnym rogu i wybierz **Niestandardowe repozytoria** (Custom repositories).
3. Wklej link do tego repozytorium i jako kategorię wybierz **Integracja** (Integration).
4. Kliknij **Dodaj** (Add), a następnie zainstaluj integrację **DBS SMS**.
5. Zrestartuj Home Assistant.

### Krok 2: Konfiguracja integracji
1. Przejdź do **Ustawienia** -> **Urządzenia oraz usługi**.
2. Kliknij **Dodaj integrację** w prawym dolnym rogu.
3. Wyszukaj i wybierz **DBS SMS**.
4. Wybierz dostawcę (np. **HostedSMS.pl**).
5. Podaj login (e-mail) oraz hasło do konta, a następnie zatwierdź.

## Użycie (Przykłady automatyzacji)

Integracja udostępnia usługę `dbs_sms.send_sms`.

### Przykład 1: Wysyłka alertu do wielu odbiorców
```yaml
action: dbs_sms.send_sms
data:
  message: "Alert! Temperatura w szklarni spadła do {{ states('sensor.szklarnia_temperature') }}°C."
  targets:
    - "48501502503"
    - "48502503504"
```

### Przykład 2: Prosta wysyłka do jednego odbiorcy (jako pojedynczy ciąg znaków)
```yaml
action: dbs_sms.send_sms
data:
  message: "Testowa wiadomość z Home Assistant."
  targets: "48501502503"
```

## Autor i Licencja

Projekt jest rozwijany i licencjonowany przez firmę **Digital Best Solutions** ([dbsservice.pl](https://dbsservice.pl/)).

Oprogramowanie jest udostępniane na warunkach określonych w pliku [LICENSE](LICENSE). Korzystanie z niego jest całkowicie bezpłatne do celów prywatnych i niekomercyjnych. Jakiekolwiek komercyjne wdrożenie lub użycie w ramach prowadzonej działalności gospodarczej wymaga uzyskania pisemnej zgody oraz zakupienia licencji komercyjnej.
