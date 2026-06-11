# DBS SMS Gateway

Integracja dla Home Assistant pozwalająca na wysyłanie powiadomień SMS za pomocą bramek API. 

## Główne zalety:
- **Konfiguracja przez UI** - nie musisz edytować plików `configuration.yaml`.
- **Wielu odbiorców** - wyślij wiadomość do kilku osób w jednym wywołaniu usługi.
- **Sensory diagnostyczne** - monitoruj ilość pozostałych środków (SMS) i datę ważności konta bezpośrednio w Home Assistant.
- **Wsparcie dla szablonów** - używaj sensorów i zmiennych Jinja2 w treści wiadomości.
- **Modułowa architektura** - gotowość do rozbudowy o kolejnych dostawców SMS (na start wspiera HostedSMS.pl).

Po instalacji przejdź do **Ustawienia -> Urządzenia oraz usługi -> Dodaj integrację** i wyszukaj **DBS SMS**.
