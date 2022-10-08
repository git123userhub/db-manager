import sqlite3 as slt3
from typing import Literal

null = 'null'
integer = 'integer'
text = 'text'
real = 'real'
blob = 'blob'
table = 'table'

class DatabaseObj:
    def __init__(self, db):

        """A mask for the sqlite3 library, used to simplify database managing."""

        self.conn = slt3.connect(db)
        self.cursor = self.conn.cursor()

        self.cursor.execute("""
                            select name from sqlite_master where
                            type = 'table';
                            """)

        self.tables = [x[0] for x in self.cursor.fetchall()]

        self._db_dict = {}
        self._update()

    def execute(self, *args):
        self.cursor.execute(*args)
        self.conn.commit()
        self._update()

    def add_table(self, table_name:str, column_data:list[str]):
        """Formatting should be ['name dtype', 'name dtype', ...]"""
        print(column_data)
        condition = f"create table {table_name} ("+"{},"*len(column_data)
        condition = condition[:-1]+')'

        self.execute(condition.format(*column_data))

    def rename_table(self, table_name:str, new_name:str):
        self.execute(f"alter table {table_name} rename to {new_name}")

    def delete_table(self, table_name:str):
        self.execute(f"drop table {table_name}")

    def delete_column(self, table_name:str, column_name:str):
        self.execute(f"alter table {table_name} drop column {column_name}")

    def rename_column(self, table_name:str, column_name:str, new_name:str):
        self.execute(f"alter table {table_name}" + '\n' +
                     f"rename column {column_name} to {new_name}")

    def add_column(self, table_name:str, column_name:str, dtype:Literal['integer', 'text', 'real', 'blob']):
        self.execute(f"alter table {table_name} add column {column_name} {dtype}")

    def get_row(self, table_name:str, rowid:int): return self[table_name]['values'][rowid]

    def table_exists(self, table_name:str):
        return table_name in self.tables

    def row_exists(self, table_name:str, row_id: int | list):
        if isinstance(row_id, int):
            return self.get_row(table_name, row_id) in self[table_name]

        return row_id in self[table_name]

    def replace_record(self, row:list | int, update_row:list, table_name:str):
        self._validate_params(update_row, table_name)
        if isinstance(row, int): row = self.get_row(table_name, row)

        condition = ""
        update_code = ""
        row_array = self[table_name]
        print(row, update_row, row_array['values'])

        for val, newval, col in zip(row, update_row, row_array['columns']):
            if val == 'None': val = null

            if isinstance(val, str) and val != null:
                condition += f"{col} = '{val}' and "
            elif val == null:
                condition += f"{col} is null and "
            else:
                condition += f"{col} = {val} and "

            if isinstance(newval, str):
                update_code += f"{col} = '{newval}', "
            else:
                update_code += f"{col} = {newval}, "

        condition = condition[0:-4]
        update_code = update_code[0:-2]

        self.execute(f"update {table_name} set {update_code} where {condition}")

    def delete_record(self, row:list | int, table_name:str):
        self._validate_params(None, table_name)
        if isinstance(row, int): row = self.get_row(table_name, row)

        condition = ""
        row_array = self[table_name]

        for val, col in zip(row, row_array['columns']):
            if val is None: val = null

            if isinstance(val, str) and val != null:
                condition += f"{col} = '{val}' and "
            else:
                condition += f"{col} = {val} and "

        condition = condition[0:-4]

        self.execute(f"delete from {table_name} where "+condition)

    def db(self): return self._db_dict

    def add_record(self, row:list | int, table_name:str):
        self._validate_params(row, table_name)
        if isinstance(row, int): row = self.get_row(table_name, row)

        self.execute(f"insert into {table_name} values {tuple(row)}")

    def schema(self, table):
        self._validate_params(None, table)
        table_dict = self[table]
        schema_dict = {}

        for i, v in enumerate(table_dict['columns']):
            schema_dict[v] = [x[i] for x in table_dict['values']]

        return schema_dict

    def __getitem__(self, item):
        return self._db_dict[item]
    def __setitem__(self, key, value):
        self._db_dict[key] = value

    def _update(self):
        for table in self.tables:
            self.cursor.execute(f"""select * from {table}""")
            vals = self.cursor.fetchall()

            self[table] = {'columns': [x[0] for x in self.cursor.description], 'values':vals, 'name':table}

    def _validate_params(self, val, table):
        try: self._db_dict[table]
        except: raise AttributeError(f"Table {table} does not exist.")

        if val:
            if len(val) != len(self._db_dict[table]['columns']):
                raise ValueError("Length of values do not match length of table columns.")
            if '' in val:
                raise ValueError("Empty string in row list. Should be replaced with null.")

    def close(self):
        self.conn.commit()
        self.conn.close()