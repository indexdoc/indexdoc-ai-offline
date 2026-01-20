import os
import platform
import uuid
import subprocess
import hashlib

import wmi


def get_machine_uuid():
    """
    尝试获取操作系统提供的硬件 UUID / machine-id。
    返回字符串，失败时返回 None。
    """
    sys = platform.system()
    try:
        if sys == "Windows":
            # UUID
            # 4C4C4544-0036-3710-8054-CAC04F4B3031
            # out = subprocess.check_output(
            #     ["wmic", "csproduct", "get", "UUID"], stderr=subprocess.DEVNULL, encoding="utf-8"
            # ).splitlines()
            # for line in out:
            #     line = line.strip()
            #     if line and line.lower() != "uuid":
            #         return line
            c = wmi.WMI()
            for system in c.Win32_ComputerSystemProduct():
                return system.UUID
        elif sys == "Linux":
            # /etc/machine-id 通常存在
            for path in ("/etc/machine-id", "/var/lib/dbus/machine-id"):
                if os.path.exists(path):
                    return open(path, "r").read().strip()
        elif sys == "Darwin":  # macOS
            # ioreg 输出中查询 IOPlatformUUID
            out = subprocess.check_output(
                ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"], encoding="utf-8"
            )
            for line in out.splitlines():
                if "IOPlatformUUID" in line:
                    # 格式："    |   \"IOPlatformUUID\" = \"XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX\""
                    return line.split('=')[1].strip().strip('"')
    except Exception:
        pass
    return None


def get_mac_address():
    """
    使用 uuid.getnode() 获取 MAC；如果返回值是随机生成的，则最低位会被设置为 1。
    """
    node = uuid.getnode()
    # 检查是否是“真实”MAC（如果最低位是 0，通常是真实硬件地址）
    if (node >> 40) % 2:
        return None  # 随机生成，不可信
    return ':'.join(f"{(node >> ele) & 0xff:02x}" for ele in range(40, -1, -8))


def generate_device_fingerprint():
    """
    综合硬件 UUID、MAC、主机名、用户名，
    然后通过 SHA-256 生成一段长度可控的唯一指纹。
    """
    parts = []
    # 硬件 UUID
    uuid_str = get_machine_uuid()
    if uuid_str:
        parts.append(uuid_str)
    # MAC 地址
    mac = get_mac_address()
    if mac:
        parts.append(mac)
    # 主机名 + 用户名
    parts.append(platform.node())
    parts.append(os.getlogin())
    # 操作系统信息
    parts.append(platform.platform())
    # 拼接并 SHA-256
    raw = "|".join(parts)
    fingerprint = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return fingerprint


def get_device_info():
    # return {}
    return {
        "Hardware UUID": get_machine_uuid(),
        "MAC Address": get_mac_address(),
        "Device Fingerprint": generate_device_fingerprint()
    }


if __name__ == "__main__":
    print("Hardware UUID:", get_machine_uuid())
    print("MAC Address:   ", get_mac_address())
    print("Device Fingerprint:", generate_device_fingerprint())
