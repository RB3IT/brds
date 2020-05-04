

class QuickbooksInventory():
    def __init__(self,worksheet):
        self.worksheet = worksheet
        rows = list(worksheet.rows)
        self.headers = [cell.value for cell in rows[0]]
        items = [dict(list(zip(self.headers,[cell.value for cell in item]))) for item in rows[1:]]
        self.items = {item['Item'].rsplit(':',maxsplit=1)[-1]:item for item in items}