"""
UI Components Test Script
- Test UI components data loading and display
- Verify correct data structure
"""

import json
from pathlib import Path

def test_ui_components():
    """Test UI components data loading"""
    
    # Load analysis data
    analysis_dir = Path("./tvmes_enhanced_analysis")
    json_path = analysis_dir / 'sapui5_deep_analysis.json'
    
    if not json_path.exists():
        print("❌ Analysis JSON file not found!")
        return
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("📊 UI Components Analysis Test")
    print("=" * 50)
    
    # Data is directly in root level
    sapui5_data = data
    
    # Check UI components
    if 'ui_components' not in sapui5_data:
        print("❌ No ui_components data found!")
        return
    
    ui_components = sapui5_data['ui_components']
    
    print("✅ UI Components Data Found:")
    print(f"   Buttons: {ui_components.get('buttons', 0)}")
    print(f"   Tables: {ui_components.get('tables', 0)}")
    print(f"   Inputs: {ui_components.get('inputs', 0)}")
    print(f"   Forms: {ui_components.get('forms', 0)}")
    print(f"   Dialogs: {ui_components.get('dialogs', 0)}")
    
    # Check if data is correct
    total_components = sum(ui_components.values())
    print(f"\n📈 Total UI Components: {total_components}")
    
    if total_components > 0:
        print("✅ UI Components data is correct!")
    else:
        print("❌ UI Components data is empty!")
    
    # Check for Button references in controllers
    print("\n🔍 Button References in Controllers:")
    button_count = 0
    for ctrl in sapui5_data.get('controllers', []):
        functions = ctrl.get('functions', [])
        for func in functions:
            if 'Button' in func:
                button_count += 1
                print(f"   - {ctrl.get('file', 'Unknown')}: {func}")
    
    print(f"\n📊 Total Button References: {button_count}")
    
    # Check for Button controls in views
    print("\n🎨 Button Controls in Views:")
    view_button_count = 0
    for view in sapui5_data.get('views', []):
        controls = view.get('controls', [])
        for control in controls:
            if control.get('type') == 'Button':
                view_button_count += 1
                print(f"   - {view.get('file', 'Unknown')}: Button")
    
    print(f"\n📊 Total Button Controls in Views: {view_button_count}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 SUMMARY:")
    print(f"   UI Components (JSON): {ui_components}")
    print(f"   Button References: {button_count}")
    print(f"   Button Controls: {view_button_count}")
    print(f"   Expected Buttons: 48")
    
    if ui_components.get('buttons', 0) == 48:
        print("✅ Button count matches expected value!")
    else:
        print(f"❌ Button count mismatch! Expected: 48, Found: {ui_components.get('buttons', 0)}")

if __name__ == "__main__":
    test_ui_components()
