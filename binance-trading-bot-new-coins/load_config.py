import yaml

def load_config(file):
    """
    Lädt die Konfigurationsdaten aus einer YAML-Datei.

    :param file: Pfad zur YAML-Konfigurationsdatei.
    :return: Dictionary mit den geladenen Konfigurationsdaten.
    """
    with open(file, 'r') as yaml_file:
        config = yaml.load(yaml_file, Loader=yaml.FullLoader)
        return config

if __name__ == "__main__":
    # Beispiel: Konfiguration laden und ausgeben
    config_file = "config.yaml"
    config = load_config(config_file)
    
    # Zugriff auf die TRADE_OPTIONS
    trade_options = config.get("TRADE_OPTIONS", {})
    print("Trade Options:", trade_options)
