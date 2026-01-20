import traceback

import aiohttp
import asyncio
import os
import hashlib
from tqdm import tqdm
import aiofiles
import time
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, AsyncGenerator, Any, Callable


@dataclass
class DownloadResult:
    """下载结果"""
    success: bool
    message: str
    error_type: str = ""
    total_size: int = 0
    downloaded_size: int = 0


@dataclass
class DownloadProgress:
    """下载进度信息"""
    stage: str  # 阶段：testing, downloading, completed
    source_speeds: Dict[int, float]  # 各源速度
    fastest_source: Optional[int] = None  # 最快源索引
    downloaded: int = 0  # 已下载字节数
    total: int = 0  # 总字节数
    progress: float = 0.0  # 进度百分比
    speed: float = 0.0  # 当前速度 KB/s
    remaining_time: float = 0.0  # 剩余时间（秒）


@dataclass
class DownloadSource:
    """下载源信息"""
    url: str
    speed: float = 0.0  # KB/s
    downloaded: int = 0  # 已下载字节数
    active: bool = True
    task: Optional[asyncio.Task] = None
    session: Optional[aiohttp.ClientSession] = None
    response: Optional[aiohttp.ClientResponse] = None
    file_handle: Optional[Any] = None


# 进度回调类型
ProgressCallback = Callable[[DownloadProgress], None]


async def download_source_with_progress(source: DownloadSource, temp_path: str, chunk_size: int):
    """带速度监控的单个源下载"""
    try:
        timeout = aiohttp.ClientTimeout(connect=10, sock_read=30, total=60)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            source.session = session
            async with session.get(source.url) as response:
                source.response = response
                if response.status != 200:
                    source.speed = 0
                    return

                source.file_handle = await aiofiles.open(temp_path, 'wb')
                start_time = time.time()
                downloaded = 0

                try:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        if not source.active:
                            break

                        if chunk:
                            await source.file_handle.write(chunk)
                            downloaded += len(chunk)
                            source.downloaded = downloaded

                            # 计算实时速度
                            elapsed = time.time() - start_time
                            if elapsed > 0:
                                source.speed = downloaded / elapsed / 1024
                finally:
                    if source.file_handle:
                        await source.file_handle.close()
                        source.file_handle = None

    except asyncio.CancelledError:
        pass
    except Exception as e:
        source.speed = 0
        # print(f"下载源 {source.url} 失败: {e}")
    finally:
        # 安全地清理资源
        if source.file_handle:
            try:
                await source.file_handle.close()
            except Exception:
                pass
            source.file_handle = None

        if source.response:
            try:
                source.response.close()
            except Exception:
                pass
            source.response = None

        if source.session:
            try:
                await source.session.close()
            except Exception:
                pass
            source.session = None


async def safe_delete_file(file_path: str, max_retries: int = 5, retry_delay: float = 0.5):
    """安全删除文件"""
    for attempt in range(max_retries):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except PermissionError:
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
            else:
                return False
        except FileNotFoundError:
            return True
        except Exception:
            return False
    return False


async def stop_source_download(source: DownloadSource, temp_file: str):
    """安全停止源下载"""
    try:
        source.active = False

        # 安全地关闭资源
        if source.file_handle:
            try:
                await source.file_handle.close()
            except Exception:
                pass
            source.file_handle = None

        if source.response:
            try:
                source.response.close()
            except Exception:
                pass
            source.response = None

        if source.session:
            try:
                await source.session.close()
            except Exception:
                pass
            source.session = None

        # 取消任务
        if source.task and not source.task.done():
            source.task.cancel()
            try:
                await asyncio.wait_for(source.task, timeout=3.0)
            except (asyncio.CancelledError, asyncio.TimeoutError):
                pass

        await asyncio.sleep(0.5)

        # 删除临时文件
        if temp_file:
            await safe_delete_file(temp_file)

    except Exception as e:
        print(f"停止下载源时出错: {e}")


async def download_from_fastest_source(source, save_path: str,
                                       initial_data: bytes, md5_hash,
                                       chunk_size: int = 8192,
                                       max_retries: int = 5):
    """从最快的源继续下载，失败时重试最多 max_retries 次"""
    total_downloaded = len(initial_data)
    start_time = time.time()
    last_update_time = start_time
    last_downloaded = total_downloaded

    for attempt in range(1, max_retries + 1):
        try:
            timeout = aiohttp.ClientTimeout(connect=10, sock_read=30, total=300)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {}
                if total_downloaded > 0:
                    headers['Range'] = f'bytes={total_downloaded}-'

                async with session.get(source.url, headers=headers) as response:
                    if response.status not in [200, 206]:
                        raise Exception(f"HTTP 状态码 {response.status}")

                    total_size = int(response.headers.get('content-length', 0)) + total_downloaded
                    current_speed = 0
                    async with aiofiles.open(save_path, 'ab') as file:
                        async for chunk in response.content.iter_chunked(chunk_size):
                            if chunk:
                                await file.write(chunk)
                                md5_hash.update(chunk)
                                total_downloaded += len(chunk)
                                current_time = time.time()
                                # elapsed = current_time - start_time
                                # current_speed = total_downloaded / elapsed / 1024 if elapsed > 0 else 0
                                # 计算瞬时速度（基于最近的数据）
                                time_diff = current_time - last_update_time
                                if time_diff >= 2.0:  # 每秒更新一次速度计算
                                    downloaded_diff = total_downloaded - last_downloaded
                                    current_speed = downloaded_diff / time_diff / 1024 if time_diff > 0 else 0
                                    last_update_time = current_time
                                    last_downloaded = total_downloaded
                                yield total_downloaded, total_size, current_speed, True

                    yield total_downloaded, total_size, 0.0, True
                    return  # 下载成功，退出循环

        except Exception as e:
            if attempt < max_retries:
                print(f"下载临时中断，继续尝试下载: {e}")
                await asyncio.sleep(2 ** attempt)  # 指数退避
            else:
                yield total_downloaded, 0, 0.0, False
                return


def format_file_size(size_bytes: float) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.2f} {size_names[i]}"


def format_time(seconds: float) -> str:
    """格式化时间"""
    if seconds <= 0:
        return "0秒"

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}小时{minutes}分{secs}秒"
    elif minutes > 0:
        return f"{minutes}分{secs}秒"
    else:
        return f"{secs}秒"


async def multi_source_download(sources: List[str], save_path: str,
                                expected_md5: Optional[str] = None,
                                test_duration: int = 10,
                                chunk_size: int = 8192,
                                progress_callback: Optional[ProgressCallback] = None) -> Tuple[bool, str]:
    """
    多源下载：测试后选择最快的源继续下载
    """

    def update_progress(stage: str, source_speeds: Dict[int, float] = None,
                        fastest_source: Optional[int] = None, downloaded: int = 0,
                        total: int = 0, speed: float = 0.0, remaining_time: float = 0.0):
        if progress_callback:
            if source_speeds is None:
                source_speeds = {}
            # 计算进度百分比
            progress_percent = downloaded / total if total > 0 else 0.0
            progress_info = DownloadProgress(
                stage=stage,
                source_speeds=source_speeds,
                fastest_source=fastest_source,
                downloaded=downloaded,
                total=total,
                progress=progress_percent,
                speed=speed,
                remaining_time=remaining_time
            )
            progress_callback(progress_info)

    download_sources = [DownloadSource(url=url) for url in sources]
    temp_dir = os.path.dirname(save_path)
    os.makedirs(temp_dir, exist_ok=True)

    source_files = []
    for i, source in enumerate(download_sources):
        temp_file = os.path.join(temp_dir, f"temp_source_{i}.part")
        source_files.append(temp_file)

    main_temp_path = save_path + ".downloading"
    md5_hash = hashlib.md5()

    try:
        # 阶段1: 速度测试
        update_progress("testing", source_speeds={i: 0.0 for i in range(len(sources))})

        tasks = []
        for i, source in enumerate(download_sources):
            task = asyncio.create_task(
                download_source_with_progress(source, source_files[i], chunk_size)
            )
            source.task = task
            tasks.append(task)

        start_test_time = time.time()
        while time.time() - start_test_time < test_duration:
            # 更新测试阶段进度
            source_speeds = {i: source.speed for i, source in enumerate(download_sources)}
            elapsed = time.time() - start_test_time
            test_progress_percent = min(elapsed / test_duration, 1.0)
            update_progress(
                stage="testing",
                source_speeds=source_speeds,
                downloaded=int(elapsed * 1000),
                total=test_duration * 1000,
                speed=0.0,
                remaining_time=0.0
            )
            await asyncio.sleep(0.5)

        # 选择最快的源
        active_sources = [s for s in download_sources if s.speed > 0]
        if not active_sources:
            return False, "所有下载源测试失败"

        fastest_source = max(active_sources, key=lambda x: x.speed)
        fastest_index = download_sources.index(fastest_source)

        print(f"🎯 测试完成，选择最快下载源: 源{fastest_index} (速度: {fastest_source.speed:.1f}KB/s)")

        # 停止其他下载任务
        stop_tasks = []
        for i, source in enumerate(download_sources):
            if source != fastest_source:
                stop_tasks.append(stop_source_download(source, source_files[i]))

        if stop_tasks:
            await asyncio.gather(*stop_tasks, return_exceptions=True)

        # 阶段2: 从最快源继续下载

        # 获取最快源已下载的数据
        total_downloaded = 0
        initial_data = b""
        if os.path.exists(source_files[fastest_index]):
            try:
                await stop_source_download(fastest_source, "")
                await asyncio.sleep(1)

                with open(source_files[fastest_index], 'rb') as f:
                    initial_data = f.read()
                    total_downloaded = len(initial_data)

                # 如果目标文件已存在，先删除它
                if os.path.exists(main_temp_path):
                    await safe_delete_file(main_temp_path)

                async with aiofiles.open(main_temp_path, 'wb') as f:
                    await f.write(initial_data)
                    md5_hash.update(initial_data)

                print(f"✅ 已复用 {total_downloaded / 1024 / 1024:.2f} MB 数据\n")

            except Exception as e:
                print(f"❌ 读取已下载数据失败: {e}")
                initial_data = b""
                total_downloaded = 0

        await safe_delete_file(source_files[fastest_index])

        # 主下载阶段
        download_success = False
        download_start_time = time.time()

        try:
            download_gen = download_from_fastest_source(
                fastest_source, main_temp_path, initial_data, md5_hash, chunk_size
            )

            async for current_downloaded, total_size, current_speed, still_going in download_gen:
                if still_going:
                    # 计算剩余时间
                    remaining_time = 0.0
                    if current_speed > 0 and total_size > current_downloaded:
                        remaining_bytes = total_size - current_downloaded
                        remaining_time = remaining_bytes / (current_speed * 1024)  # 转换为秒

                    update_progress(
                        stage="downloading",
                        source_speeds={fastest_index: current_speed},
                        fastest_source=fastest_index,
                        downloaded=current_downloaded,
                        total=total_size,
                        speed=current_speed,
                        remaining_time=remaining_time
                    )
                else:
                    break
            else:
                download_success = True

        except Exception as e:
            print(f"❌ 下载过程中出错: {e}")
            traceback.print_exc()
            download_success = False

        if not download_success:
            return False, "从最快源下载失败"

        # 完成阶段
        if os.path.exists(main_temp_path):
            # 如果目标文件已存在，先删除
            if os.path.exists(save_path):
                await safe_delete_file(save_path)

            os.rename(main_temp_path, save_path)
            final_size = os.path.getsize(save_path)
            update_progress(
                stage="completed",
                source_speeds={fastest_index: 0.0},
                fastest_source=fastest_index,
                downloaded=final_size,
                total=final_size,
                speed=0.0,
                remaining_time=0.0
            )
        else:
            return False, "下载文件不存在"

        if expected_md5:
            actual_md5 = md5_hash.hexdigest()
            if actual_md5 != expected_md5:
                return False, f"MD5校验失败: 期望 {expected_md5}, 实际 {actual_md5}"
            print("✅ MD5校验通过")

        return True, "下载成功"

    except Exception as e:
        return False, f"下载失败: {str(e)}"
    finally:
        cleanup_tasks = []
        for i, (source, temp_file) in enumerate(zip(download_sources, source_files)):
            cleanup_tasks.append(stop_source_download(source, temp_file))
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        await safe_delete_file(main_temp_path)


# 使用示例
async def main():
    print("=== 多源下载测试（带进度回调）===")

    # 进度回调函数
    def progress_callback(progress: DownloadProgress):
        if progress.stage == "testing":
            print(f"\r🔄 测试阶段 - 进度: {progress.progress * 100:.1f}% | " +
                  " | ".join([f"源{i}: {speed:.1f}KB/s" for i, speed in progress.source_speeds.items()]), end="",
                  flush=True)
        elif progress.stage == "downloading":
            # 格式化文件大小和剩余时间
            total_size_str = format_file_size(progress.total)
            downloaded_str = format_file_size(progress.downloaded)
            remaining_time_str = format_time(progress.remaining_time)

            print(f"\r📥 下载阶段 - 进度: {progress.progress * 100:.1f}% | " +
                  f"大小: {downloaded_str}/{total_size_str} | " +
                  f"速度: {progress.speed:.1f}KB/s | " +
                  f"剩余: {remaining_time_str}", end="", flush=True)
        elif progress.stage == "completed":
            total_size_str = format_file_size(progress.downloaded)
            print(f"✅ 下载完成! 总大小: {total_size_str}")

    # 多个下载地址
    sources = [
        "https://r2.aituple.cn/indexdoc_win.zst",
        "https://pub-023efc67a2674a00bbe4437f46ec740c.r2.dev/indexdoc_win.zst",
    ]

    save_path = "./downloads/Cyberduck.exe"

    success, message = await multi_source_download(
        sources=sources,
        save_path=save_path,
        test_duration=5,
        progress_callback=progress_callback
    )

    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")


if __name__ == "__main__":
    os.makedirs("./downloads", exist_ok=True)
    asyncio.run(main())