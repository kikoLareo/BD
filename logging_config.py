import logging
import sys
from pythonjsonlogger import jsonlogger  # Para logs estructurados en JSON

# Configuración de colores para los niveles de logs
class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',  # Azul
        'INFO': '\033[92m',   # Verde
        'WARNING': '\033[93m',  # Amarillo
        'ERROR': '\033[91m',  # Rojo
        'CRITICAL': '\033[95m'  # Magenta
    }
    RESET = '\033[0m'  # Reset de color

    def format(self, record):
        color = self.COLORS.get(record.levelname, self.RESET)
        message = super().format(record)
        return f"{color}{message}{self.RESET}"

# Configuración del formateador JSON personalizado
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record['timestamp'] = record.created  # Marca de tiempo
        log_record['transaction_id'] = getattr(record, 'transaction_id', 'N/A')
        log_record['user_id'] = getattr(record, 'user_id', 'anonymous')
        log_record['level'] = record.levelname
        log_record['source'] = "backend"  # Identificador de procedencia

# Configuración del logger
def setup_logger():
    logger = logging.getLogger("wave_studio")
    logger.setLevel(logging.DEBUG)  # Nivel de logs: DEBUG, INFO, WARNING, ERROR, CRITICAL

    # Formateador JSON estructurado
    json_formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(transaction_id)s %(user_id)s %(source)s %(message)s')

    # Controlador de logs a la consola con colores
    console_handler = logging.StreamHandler(sys.stdout)
    colored_formatter = ColoredFormatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(colored_formatter)
    logger.addHandler(console_handler)

    # Controlador para guardar los logs en un archivo (usando el formateador JSON)
    file_handler = logging.FileHandler("wave_studio_backend_logs.json")
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()