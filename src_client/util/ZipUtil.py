import zipfile
import os
def zip_compress(folder_path, zip_path, progress_callback=None):
    """带进度回调的zip压缩"""
    # 预先计算总文件大小和文件列表
    total_size = 0
    file_list = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            total_size += file_size
            file_list.append((file_path, file_size))
    compressed_size = 0
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path, file_size in file_list:
            # 计算在zip中的相对路径
            arcname = os.path.relpath(file_path, folder_path)
            zipf.write(file_path, arcname)
            # 更新已压缩大小
            compressed_size += file_size
            # 调用进度回调
            if progress_callback:
                progress = (compressed_size / total_size) * 100 if total_size > 0 else 100
                progress_callback(compressed_size, os.path.basename(file_path), progress)
    print(f"✅ ZIP压缩完成: {folder_path} -> {zip_path}")

def zip_decompress(zip_path, extract_path=None, progress_callback=None):
    """带进度回调的zip解压"""
    if extract_path is None:
        extract_path = os.path.splitext(zip_path)[0] + "_extracted"

    os.makedirs(extract_path, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zipf:
        # 获取文件列表和总大小
        file_list = zipf.filelist
        total_size = sum(file_info.file_size for file_info in file_list)
        extracted_size = 0

        for file_info in file_list:
            # 解压单个文件
            zipf.extract(file_info, extract_path)
            # 更新已解压大小
            extracted_size += file_info.file_size
            # 调用进度回调
            if progress_callback:
                progress = (extracted_size / total_size) * 100 if total_size > 0 else 100
                progress_callback(extracted_size, file_info.filename, progress)

    print(f"✅ ZIP解压完成: {zip_path} -> {extract_path}")
    return extract_path


if __name__ == '__main__':
    import time
    start = time.time()
    # 进度回调函数示例
    def progress_callback(processed_size, filename, progress):
        """进度回调函数"""
        print(f"\r进度: {progress:.1f}% | 已处理: {processed_size / 1024 / 1024:.2f} MB | 当前文件: {filename}",end="",flush=True)
    zip_compress(r"D:\PycharmProjects\indexdoc_win\my_builder3\dist\launcher",fr"..\tmp\test11.zip",progress_callback)
    print(f"zip_compress :{time.time()-start}")
    # import shutil
    # shutil.rmtree(r'..\tmp\test\uppacked', ignore_errors=True)
    # start = time.time()
    # zip_decompress_with_progress(fr"..\tmp\test11.zip",r'..\tmp\test\uppacked',progress_callback)
    # print(f"zip_decompress :{time.time()-start}")

