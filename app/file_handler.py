from io import StringIO, BytesIO
import zipfile
import csv


def generate_csv(playlist_contents):
    """:returns BytesIO csv with given playlist contents."""
    memory_file = BytesIO()
    with StringIO() as proxy:
        writer = csv.writer(proxy)
        for row in playlist_contents:
            writer.writerow(row)

        memory_file.write(proxy.getvalue().encode())
        memory_file.seek(0)
    return memory_file


def generate_zip(csv_files):
    """:returns BytesIO zip with given 'csv_name: csv_BytesIO'."""
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for name, csv_file in csv_files.items():
            zf.writestr(f"{name}.csv", csv_file.getvalue())
    memory_file.seek(0)
    return memory_file
