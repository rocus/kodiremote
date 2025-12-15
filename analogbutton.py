"""
Analog Button Reader for Raspberry Pi Pico
Connect the button board's signal pin to GP26 (ADC0) or any ADC pin
"""

from machine import ADC, Pin
import time

class AnalogButtonPico:
    def __init__(self, pin_num=26):
        """
        Initialize the ADC pin
        Pin options for ADC on Pico: 26, 27, 28 (GP26, GP27, GP28)
        """
        self.adc_pin = ADC(Pin(pin_num))
#        self.adc_pin.atten(ADC.ATTN_11DB)  # Full range: 0-3.3V
        
        # LED for visual feedback (optional - connect LED to GP15)
        self.led = Pin("LED", Pin.OUT)
        
        # Button mapping - you MUST calibrate these for your board!
        # These are example ranges for 12-bit ADC (0-4095)
        self.button_map = {
            "NO_PRESS": {"min": 3500, "max": 4095, "name": "No Press"},
            "BUTTON_1": {"min": 2800, "max": 3200, "name": "Button 1"},
            "BUTTON_2": {"min": 2200, "max": 2600, "name": "Button 2"},
            "BUTTON_3": {"min": 1600, "max": 2000, "name": "Button 3"},
            "BUTTON_4": {"min": 1000, "max": 1400, "name": "Button 4"},
            "BUTTON_5": {"min": 0, "max": 800, "name": "Button 5"},
        }


        
        self.button_map = {
            "NO_PRESS": {"min": 3686, "max": 4504, "name": "No Press"},
            "BUTTON_1": {"min": 2686, "max": 3282, "name": "Button 1"},
            "BUTTON_2": {"min": 1835, "max": 2241, "name": "Button 2"},
            "BUTTON_3": {"min": 1203, "max": 1469, "name": "Button 3"},
            "BUTTON_4": {"min":  531, "max":  649, "name": "Button 4"},
            "BUTTON_5": {"min":  -32, "max":   67, "name": "Button 5"},
        }  
        # For statistics
        self.button_counts = {name: 0 for name in self.button_map.keys()}
        
    def read_raw(self):
        """Read raw ADC value (12-bit: 0-4095)"""
        return self.adc_pin.read_u16() >> 4  # Convert 16-bit to 12-bit
    
    def read_voltage(self):
        """Convert ADC reading to voltage (0-3.3V)"""
        raw = self.read_raw()
        return (raw / 4095) * 3.3
    
    def get_button(self):
        """Identify which button is pressed based on ADC value"""
        raw_value = self.read_raw()
        voltage = self.read_voltage()
        
        for button_name, ranges in self.button_map.items():
            if ranges["min"] <= raw_value <= ranges["max"]:
                # Flash LED when a button is pressed (not NO_PRESS)
                if button_name != "NO_PRESS":
                    self.led.value(1)
                    time.sleep(0.05)
                    self.led.value(0)
                    self.button_counts[button_name] += 1
                return button_name, ranges["name"], raw_value, voltage
        
        return "UNKNOWN", "Unknown", raw_value, voltage
    
    def continuous_read(self):
        """Display continuous readings"""
        print("\n" + "="*60)
        print("Analog Button Reader - Raspberry Pi Pico")
        print("Press Ctrl+C to stop")
        print("="*60)
        print(f"{'State':<12} {'Name':<12} {'Raw':<8} {'Voltage':<8}")
        print("-" * 45)
        
        last_button = None
        try:
            while True:
                button_state, button_name, raw_val, voltage = self.get_button()
                
                # Only print when button changes
                if button_state != last_button:
                    print(f"{button_state:<12} {button_name:<12} {raw_val:<8} {voltage:<8.3f}V")
                    last_button = button_state
                
                time.sleep(0.1)  # Small delay
                
        except KeyboardInterrupt:
            print("\n\n" + "="*60)
            print("STATISTICS:")
            print("="*60)
            for btn, count in self.button_counts.items():
                if count > 0:
                    print(f"{self.button_map.get(btn, {}).get('name', btn)}: {count} presses")
            print("\nExiting...")
    
    def calibration_mode(self, duration=30):
        """Help you calibrate your button values"""
        print("\n" + "="*60)
        print("CALIBRATION MODE")
        print("="*60)
        print("Press and hold each button one at a time")
        print(f"Sampling for {duration} seconds...")
        print("="*60)
        
        # Dictionary to store samples for each detected range
        readings = {}
        
        start_time = time.time()
        sample_count = 0
        
        try:
            while time.time() - start_time < duration:
                raw_value = self.read_raw()
                voltage = self.read_voltage()
                
                # Group similar readings (within ±50 of center)
                found = False
                for center in list(readings.keys()):
                    if abs(raw_value - center) < 50:
                        readings[center].append((raw_value, voltage))
                        found = True
                        break
                
                if not found:
                    readings[raw_value] = [(raw_value, voltage)]
                
                sample_count += 1
                # Show current reading
                print(f"Sample {sample_count}: Raw={raw_value:4d}, Voltage={voltage:.3f}V", end='\r')
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\nCalibration stopped by user")
        
        print("\n\n" + "="*60)
        print("CALIBRATION RESULTS")
        print("="*60)
        
        # Filter out groups with enough samples
        valid_groups = {k: v for k, v in readings.items() if len(v) > 10}
        
        if not valid_groups:
            print("Not enough samples! Try again and hold buttons longer.")
            return
        
        # Sort by raw value (descending - highest is usually NO_PRESS)
        sorted_groups = sorted(valid_groups.items(), key=lambda x: x[0], reverse=True)
        
        print(f"\nFound {len(sorted_groups)} distinct button states:")
        print("-" * 60)
        
        for i, (center, samples) in enumerate(sorted_groups):
            raw_values = [s[0] for s in samples]
            voltages = [s[1] for s in samples]
            
            min_raw = min(raw_values)
            max_raw = max(raw_values)
            avg_raw = sum(raw_values) / len(raw_values)
            avg_voltage = sum(voltages) / len(voltages)
            
            # Determine likely button
            if i == 0:
                label = "NO_PRESS (highest value)"
            else:
                label = f"BUTTON_{i}"
            
            print(f"\n{label}:")
            print(f"  Samples: {len(samples)}")
            print(f"  Raw range: {min_raw} - {max_raw}")
            print(f"  Average: {avg_raw:.1f}")
            print(f"  Voltage: {avg_voltage:.3f}V")
            
            # Calculate safe margin (±10% or ±50, whichever is larger)
            margin = max(50, int(avg_raw * 0.1))
            print(f"  Suggested range: {int(avg_raw-margin)} - {int(avg_raw+margin)}")
        
        print("\n" + "="*60)
        print("To use these values, update the button_map in your code:")
        print("="*60)
        
        for i, (center, samples) in enumerate(sorted_groups):
            raw_values = [s[0] for s in samples]
            avg_raw = sum(raw_values) / len(raw_values)
            margin = max(50, int(avg_raw * 0.1))
            
            if i == 0:
                key = "NO_PRESS"
            else:
                key = f"BUTTON_{i}"
            
            print(f'    "{key}": {{"min": {int(avg_raw-margin)}, "max": {int(avg_raw+margin)}}},')


def interactive_menu():
    """Display menu and handle user input"""
    print("\n" + "="*60)
    print("RASPBERRY PI PICO ANALOG BUTTON READER")
    print("="*60)
    
    # Initialize the button reader (default pin 26)
    # Change to 27 or 28 if using different ADC pin
    reader = AnalogButtonPico(pin_num=26)
    
    while True:
        print("\nOptions:")
        print("  1. Start continuous reading")
        print("  2. Calibration mode")
        print("  3. Test single reading")
        print("  4. View current button map")
        print("  5. Exit")
        
        try:
            choice = input("\nEnter choice (1-5): ").strip()
            
            if choice == '1':
                reader.continuous_read()
                
            elif choice == '2':
                try:
                    duration = int(input("Calibration duration (seconds, default 30): ") or "30")
                    reader.calibration_mode(duration)
                except ValueError:
                    print("Invalid duration, using 30 seconds")
                    reader.calibration_mode(30)
                    
            elif choice == '3':
                print("\nSingle reading test (press any button):")
                print("Press Ctrl+C to return to menu")
                try:
                    while True:
                        btn_state, btn_name, raw_val, voltage = reader.get_button()
                        print(f"Button: {btn_name:<12} | Raw: {raw_val:4d} | Voltage: {voltage:.3f}V", end='\r')
                        time.sleep(0.2)
                except KeyboardInterrupt:
                    print("\n")
                    
            elif choice == '4':
                print("\nCurrent button map configuration:")
                print("-" * 50)
                for key, values in reader.button_map.items():
                    print(f"{key:12}: min={values['min']:4d}, max={values['max']:4d} ({values['name']})")
                    
            elif choice == '5':
                print("Exiting...")
                break
                
            else:
                print("Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n\nReturning to menu...")
        except Exception as e:
            print(f"Error: {e}")


# Quick test function (run this directly to test)
def quick_test():
    """Simple test without menu - just show readings"""
    reader = AnalogButtonPico(pin_num=26)
    
    print("Quick Test Mode - Press buttons on your board")
    print("Press Ctrl+C to exit")
    print("\nWaiting for button presses...")
    
    try:
        while True:
            btn_state, btn_name, raw_val, voltage = reader.get_button()
            if btn_state != "NO_PRESS":
                print(f"Pressed: {btn_name} | Raw: {raw_val} | Voltage: {voltage:.3f}V")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nTest complete!")


# Main execution
if __name__ == "__main__":
    # You can run either the full menu or quick test
    # Uncomment the one you want to use:
    
    # Option 1: Full interactive menu (recommended)
    #interactive_menu()
    
    # Option 2: Quick test (simpler)
    quick_test()

