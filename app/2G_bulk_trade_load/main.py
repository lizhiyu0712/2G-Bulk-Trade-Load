from cx_Freeze import setup, Executable
import shutil
import os

setup(
    name="2G_Bulk_Trade_Load",
    version="0.1.0",
    description="",
    options={
        "build_exe": {
            "zip_include_packages": ["*"],  # Include all packages in the zip
            "zip_exclude_packages": [],     # Exclude none
            "build_exe": "dist",            # Output directory for the build
        }
    },
    executables=[Executable("./app/2G_bulk_trade_load/2G_bulk_trade_load.py", target_name="2G_bulk_trade_load.exe")]
)

# Create the zip file in the root directory after build completes
zip_path = shutil.make_archive("2G Bulk Trade Load", 'zip', "dist")
print(f"Build completed. Zip file location: {os.path.abspath(zip_path)}")