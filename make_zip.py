from zipfile import ZipFile
import glob


with ZipFile("io_export_agr.zip", 'w') as zip:
    for filename in glob.iglob("io_export_agr/**/*.py", recursive=True):
        zip.write(filename)
    #zip.write("LICENSE", "io_import_vmf/LICENSE")