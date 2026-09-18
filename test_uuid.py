import subprocess
def get_uuid(name):
    cmd = f'Get-CimInstance Win32_NetworkAdapter | Where-Object {{ \.NetConnectionID -eq "{name}" }} | Select-Object -ExpandProperty GUID'
    out = subprocess.check_output(["powershell", "-Command", cmd], text=True).strip()
    return f"\\Device\\NPF_{out}"
print(get_uuid("Wi-Fi"))
