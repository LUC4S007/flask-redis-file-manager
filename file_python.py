
import base64
from io import BytesIO
import json
import os
import zipfile


class File():
    def __init__(self, zip_file_directory='temp', zip_file_name='packed.zip') -> None:
        self.zip_file_directory = zip_file_directory
        self.zip_file = zip_file_name
        self.checks()
    def checks(self):
        if self.zip_file is None:
            self.zip_file='packed.zip'
        if self.zip_file_directory is None:
            self.zip_file_directory='temp'
    def zip_physically(self, file_paths):
        if not file_paths:
            return None
        if len(file_paths) < 1:
            return None

        # Create a temporary directory to store the packed files
        temp_dir = self.zip_file_directory
        os.makedirs(temp_dir, exist_ok=True)

        # Pack the selected files into a ZIP archive
        zip_file_path = os.path.join(temp_dir, self.zip_file)
        with zipfile.ZipFile(zip_file_path, "w") as zip_file:
            for file_path in file_paths:
                zip_file.write(file_path, os.path.basename(file_path))
         # Remove the temporary directory and files
        encoded_data = self.read_file(zip_file_path)

        self.removing()
        return encoded_data
    def zip_in_memory_fileStorage(self, file_storages):
        if not file_storages or len(file_storages) < 1:
            return None

        # Create an in-memory file-like object to write the ZIP data
        zip_data = BytesIO()

        # Pack the selected files into a ZIP archive
        with zipfile.ZipFile(zip_data, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for file_storage in file_storages:
                # Read the file content from the FileStorage object
                file_content = file_storage.read()
                # Get the filename
                file_name = file_storage.filename
                # Write the file content to the ZIP archive
                zip_file.writestr(file_name, file_content)

        # Get the ZIP data as bytes
        zip_data.seek(0)
        zip_bytes = zip_data.getvalue()

        # You can now do whatever you want with the ZIP data, such as sending it over a network or writing it to a file

        # Remember to close the in-memory file-like object
        zip_data.close()
        encoded_data = self.encoding(zip_bytes)
        return encoded_data

    def zip_in_memory(self, file_paths):
        if not file_paths:
            return None
        if len(file_paths) < 1:
            return None

        # Create an in-memory file-like object to write the ZIP data
        zip_data = BytesIO()

        # Pack the selected files into a ZIP archive
        with zipfile.ZipFile(zip_data, "w") as zip_file:
            for file_path in file_paths:
                zip_file.write(file_path, os.path.basename(file_path))

        # Get the ZIP data as bytes
        zip_data.seek(0)
        zip_bytes = zip_data.getvalue()

        # You can now do whatever you want with the ZIP data, such as sending it over a network or writing it to a file

        # Remember to close the in-memory file-like object
        zip_data.close()
        encoded_data = self.encoding(zip_bytes)
        return encoded_data

        # Remove the temporary directory and files

    def removing(self):
        os.remove(self.zip_file_path)
        os.rmdir(self.temp_dir)

    def encoding(self, file_data):
        file_data_encoded = base64.b64encode(file_data).decode()
        return file_data_encoded

    def decoding(self, file_data_encoded):
        file_data = base64.b64decode(file_data_encoded.encode())
        return file_data

    def extract_zip(self, zip_file_path, directory_to_save):
        # Extract the files from the received ZIP archive
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(directory_to_save)

    def save_file_in_folder(self, file_name, folder_path, data):
        # For example, to write the ZIP data to a file on disk
        file_path = os.path.join(folder_path, file_name)
        self.save_file(file_path, data)

    def save_file(self, file_path, data_encoded):
        # For example, to write the ZIP data to a file on disk
        decoded_data = self.decoding(data_encoded)
        with open(file_path, "wb") as output_file:
            output_file.write(decoded_data)

    def read_file(self, file_path):
        with open(file_path, 'rb') as file:
            file_data = file.read()
        encoded_data = self.encoding(file_data)
        return encoded_data

    @staticmethod
    def save_text_file(file_path, decoded_data):
        # For example, to write the ZIP data to a file on disk
        with open(file_path, "w") as output_file:
            output_file.write(decoded_data)

    @staticmethod
    def read_text_file(file_path):
        with open(file_path, 'r') as file:
            file_data = file.read()
        return file_data

    @staticmethod
    def read_json(filepath):
        params = None
        if filepath:
            with open(filepath, 'r') as c:
                params = json.load(c)
        return params

    @staticmethod
    def save_json_file(file_path, data):
        if file_path and data:
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)

    @staticmethod
    def split_path(file_path):
        folderpath, filename = os.path.split(file_path)
        return folderpath, filename
