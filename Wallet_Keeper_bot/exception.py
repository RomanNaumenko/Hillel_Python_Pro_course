class NotCorrectMessage(Exception):
    """Вами було введено некоректне повідомлення, яке не вдалося розпізнати."""
    pass


class InvalidExecuteDB(Exception):
    """Не вдалося досягти даних у БД."""
    pass
