import os
from pathlib import Path
from n9010a_controller import __version__


def pyinstaller() -> None:
    # icon: str = f"--icon {cwd().joinpath('assets', 'settings.ico')}"
    flags: list[str] = [f"--name SpectrumAnalizer_v{__version__}",
                        "--console", "--onefile", "--clean", "--noconfirm"]
    main_path: str = str(Path(__file__).parent / 'pyqt_client' /'backend.py')
    ui_paths: list[str] = ['--add-data ' + str(f"\"{file};.\"")
                           for file in (Path(__file__).parent / 'pyqt_client').glob("*.ui")]

    destination: str = f"--distpath {Path.cwd()}"
    to_exe_cmd: str = ' '.join(["pyinstaller", main_path,
                                *flags,
                                destination,
                                *ui_paths,
                                ])
    os.system(to_exe_cmd)
    for flag in to_exe_cmd.split('--'):
        print(f'--{flag}')


if __name__ == '__main__':
    pyinstaller()