import subprocess
import time
import os
from typing import Dict, Optional

class AndroidVirtualSystem:
    def __init__(self):
        self.emulator_name = "pixel2_api_30"
        self.system_info = {}

    def start_emulator(self) -> bool:
        """Start the Android emulator"""
        try:
            # Start the emulator in a separate process
            subprocess.Popen([
                "emulator",
                "-avd", self.emulator_name,
                "-no-snapshot-load"
            ])
            
            # Wait for emulator to boot
            print("Starting emulator, please wait...")
            self._wait_for_device()
            return True
        except Exception as e:
            print(f"Error starting emulator: {str(e)}")
            return False

    def _wait_for_device(self, timeout: int = 60):
        """Wait for the device to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                result = subprocess.run(
                    ["adb", "shell", "getprop", "sys.boot_completed"],
                    capture_output=True,
                    text=True
                )
                if result.stdout.strip() == "1":
                    print("Emulator is ready!")
                    return
                time.sleep(2)
            except Exception:
                pass
        raise TimeoutError("Emulator failed to start within timeout period")

    def install_app(self, apk_path: str) -> bool:
        """Install an APK file to the virtual device"""
        if not os.path.exists(apk_path):
            print(f"APK file not found: {apk_path}")
            return False

        try:
            result = subprocess.run(
                ["adb", "install", apk_path],
                capture_output=True,
                text=True
            )
            if "Success" in result.stdout:
                print(f"Successfully installed {apk_path}")
                return True
            else:
                print(f"Failed to install APK: {result.stderr}")
                return False
        except Exception as e:
            print(f"Error installing APK: {str(e)}")
            return False

    def get_system_info(self) -> Dict[str, str]:
        """Retrieve system information from the virtual device"""
        try:
            # Dictionary to store system information
            info = {}
            
            # Commands to get different system information
            commands = {
                "Android Version": "getprop ro.build.version.release",
                "Device Model": "getprop ro.product.model",
                "Device Manufacturer": "getprop ro.product.manufacturer",
                "Total Memory": "cat /proc/meminfo | grep MemTotal",
                "CPU Info": "cat /proc/cpuinfo | grep Processor"
            }

            # Execute each command and store results
            for key, command in commands.items():
                result = subprocess.run(
                    ["adb", "shell", command],
                    capture_output=True,
                    text=True
                )
                info[key] = result.stdout.strip()

            self.system_info = info
            return info

        except Exception as e:
            print(f"Error getting system info: {str(e)}")
            return {}

    def display_system_info(self):
        """Display the collected system information"""
        if not self.system_info:
            self.get_system_info()
        
        print("\n=== System Information ===")
        for key, value in self.system_info.items():
            print(f"{key}: {value}")

    def cleanup(self):
        """Clean up resources and shut down the emulator"""
        try:
            subprocess.run(["adb", "emu", "kill"])
            print("Emulator shutdown successfully")
        except Exception as e:
            print(f"Error shutting down emulator: {str(e)}")

def main():
    # Create instance of Android Virtual System
    avs = AndroidVirtualSystem()

    try:
        # Start the emulator
        if avs.start_emulator():
            print("Android Virtual System started successfully")

            # Install a sample APK (replace with actual APK path)
            sample_apk = "path/to/your/sample.apk"
            if os.path.exists(sample_apk):
                avs.install_app(sample_apk)

            # Get and display system information
            avs.display_system_info()

            # Keep the system running until user interrupts
            input("Press Enter to shutdown the virtual system...")
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Clean up resources
        avs.cleanup()

if __name__ == "__main__":
    main()
