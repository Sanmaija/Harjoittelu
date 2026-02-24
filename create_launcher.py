from __future__ import annotations

import os
import platform
from pathlib import Path

APP_NAME = "Taloussuunnittelija"


def project_root() -> Path:
    return Path(__file__).resolve().parent


def streamlit_command(root: Path) -> str:
    python_exe = Path(os.environ.get("VIRTUAL_ENV", "")) / "bin" / "python"
    if platform.system() == "Windows":
        python_exe = Path(os.environ.get("VIRTUAL_ENV", "")) / "Scripts" / "python.exe"

    if python_exe.exists():
        return f'"{python_exe}" -m streamlit run "{root / "app.py"}"'

    return f'python -m streamlit run "{root / "app.py"}"'


def create_linux_shortcut(root: Path) -> list[Path]:
    cmd = streamlit_command(root)
    desktop_entry = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={APP_NAME}
Comment=Henkilökohtaisen talouden suunnittelu
Exec=bash -lc '{cmd}'
Path={root}
Terminal=false
Categories=Office;Finance;
"""

    created: list[Path] = []

    applications_dir = Path.home() / ".local/share/applications"
    applications_dir.mkdir(parents=True, exist_ok=True)
    app_file = applications_dir / "taloussuunnittelija.desktop"
    app_file.write_text(desktop_entry, encoding="utf-8")
    app_file.chmod(0o755)
    created.append(app_file)

    desktop_dir = Path.home() / "Desktop"
    if desktop_dir.exists():
        desktop_file = desktop_dir / "Taloussuunnittelija.desktop"
        desktop_file.write_text(desktop_entry, encoding="utf-8")
        desktop_file.chmod(0o755)
        created.append(desktop_file)

    return created


def create_windows_shortcut(root: Path) -> list[Path]:
    cmd = streamlit_command(root)
    desktop = Path.home() / "Desktop"
    desktop.mkdir(parents=True, exist_ok=True)
    bat_file = desktop / "Avaa-Taloussuunnittelija.bat"
    bat_file.write_text(
        "@echo off\n"
        f"cd /d \"{root}\"\n"
        f"{cmd}\n",
        encoding="utf-8",
    )
    return [bat_file]


def create_macos_shortcut(root: Path) -> list[Path]:
    cmd = streamlit_command(root)
    desktop = Path.home() / "Desktop"
    desktop.mkdir(parents=True, exist_ok=True)
    command_file = desktop / "Avaa-Taloussuunnittelija.command"
    command_file.write_text(
        "#!/bin/bash\n"
        f"cd '{root}'\n"
        f"{cmd}\n",
        encoding="utf-8",
    )
    command_file.chmod(0o755)
    return [command_file]


def main() -> None:
    root = project_root()
    system = platform.system()

    if system == "Linux":
        created = create_linux_shortcut(root)
    elif system == "Windows":
        created = create_windows_shortcut(root)
    elif system == "Darwin":
        created = create_macos_shortcut(root)
    else:
        raise RuntimeError(f"Käyttöjärjestelmää ei tueta: {system}")

    print("Luotiin käynnistinkuvake/tiedosto:")
    for file in created:
        print(f" - {file}")


if __name__ == "__main__":
    main()
