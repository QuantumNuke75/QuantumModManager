import time, os, io, re
from struct import unpack as st_unpack


def read_path(stream: io.BufferedReader, encoding: str = 'utf-16') -> str:
    try:
        path_len, = st_unpack('<i',stream.read(4))
        if path_len < 0:
            # in at least some format versions, this indicates a UTF-16 path
            path_len = -2 * path_len
            encoding = 'iso-8859-1'
        return stream.read(path_len).decode(encoding).rstrip('\0').replace('/',os.path.sep)
    except:
        return


def read_file(stream):
    stream.seek(-225, 2)
    footer_offset = stream.tell()
    footer = stream.read(225)

    key, index, magic, version, offset, size, hash, comp = st_unpack('< 20s c II QQ 20s 160s',footer)
    print(offset)
    print(f"Version: {version}")

    stream.seek(offset, 0)
    mount_point = read_path(stream, "utf-8")
    print(f"Mount Point: {mount_point}")

    entry_count = st_unpack('<I', stream.read(4))[0]
    print(f"Entry Count: {entry_count}")

    path_hash_seed = st_unpack('<Q', stream.read(8))[0]
    print(f"path_hash_seed: {path_hash_seed}")

    has_path_hash_index = st_unpack('<I', stream.read(4))[0]
    print(f"has_path_hash_index: {has_path_hash_index}")

    if has_path_hash_index != 0:
        has_path_index_offset = st_unpack('<Q', stream.read(8))[0]
        print(f"has_path_index_offset: {has_path_index_offset}")

        has_path_index_size = st_unpack('<Q', stream.read(8))[0]
        print(f"has_path_index_size: {has_path_index_size}")

        has_path_index_hash = st_unpack('<20s', stream.read(20))[0]
        print(f"has_path_index_hash: {has_path_index_hash}")

    has_full_directory_index = st_unpack('<I', stream.read(4))[0]
    print(f"has_full_directory_index: {has_full_directory_index}")

    if has_full_directory_index != 0:
        full_directory_index_offset = st_unpack('<Q', stream.read(8))[0]
        print(f"full_directory_index_offset: {full_directory_index_offset}")

        full_directory_index_size = st_unpack('<Q', stream.read(8))[0]
        print(f"full_directory_index_size: {full_directory_index_size}")

        full_directory_index_hash = st_unpack('<20s', stream.read(20))[0]
        print(f"full_directory_index_hash: {full_directory_index_hash}")

    encoded_entry_info_size = st_unpack('<I', stream.read(4))[0]
    print(f"encoded_entry_info_size: {encoded_entry_info_size}")

    encoded_entry_info  = st_unpack(f'<{encoded_entry_info_size}s', stream.read(encoded_entry_info_size))[0]
    #print(f"encoded_entry_info: {encoded_entry_info}")

    file_count = st_unpack('<I', stream.read(4))[0]
    print(f"file_count: {file_count}")

    ######## INDEX RECORD ########
    directory_count = st_unpack('<I', stream.read(4))[0]
    print(f"directory_count: {directory_count}")


    stream.seek(full_directory_index_offset)


    total_items = st_unpack('<I', stream.read(4))[0]
    print(f"total_items: {total_items}")

    file_num = 0

    for i in range(directory_count):
        directory_name_size = st_unpack('<I', stream.read(4))[0]
        print(f"{i} - directory_name_size: {directory_name_size}")

        directory_name = st_unpack(f'<{directory_name_size}s', stream.read(directory_name_size))[0]
        print(f"{i} - directory_name: {directory_name}")

        file_count = st_unpack('<I', stream.read(4))[0]
        print(f"{i} - file_count: {file_count}")

        if file_num >= directory_count:
            print(file_num)
            break


        for j in range(file_count):
            file_name_size = st_unpack('<I', stream.read(4))[0]
            print(f"    {j} - file_name_size: {file_name_size}")

            file_name = st_unpack(f'<{file_name_size}s', stream.read(file_name_size))[0]
            print(f"    {j} - file_name: {file_name}")

            encoded_entry_offset = st_unpack('<I', stream.read(4))[0]
            print(f"    {j} - encoded_entry_offset: {encoded_entry_offset}")
            file_num += 1


with open("C:\Program Files (x86)\Steam\steamapps\common\Ready Or Not\ReadyOrNot\Content\Paks\pakchunk99-Everything_Unlocked_15_P.pak", "rb") as stream:
    read_file(stream)
    stream.close()


