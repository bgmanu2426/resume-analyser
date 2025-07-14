import os
import aiofiles


async def save_to_disk(file: bytes, file_path: str) -> bool:
    """
    Save the file to the specified disk path.

    :param file: The file content as bytes.
    :param file_path: The path where the file should be saved.
    :return: True if the file was saved successfully, False otherwise.
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file)
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False
