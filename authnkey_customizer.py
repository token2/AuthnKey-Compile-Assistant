#!/usr/bin/env python3
"""
Script to fork and customize the Authnkey project for Token2 Companion integration
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

def run_command(cmd, cwd=None):
    """Execute a shell command"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"Exception: {e}")
        return False

def clone_repo(repo_url, target_dir):
    """Clone the repository"""
    print(f"Cloning repository from {repo_url}...")
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    return run_command(f"git clone {repo_url} {target_dir}")

def change_package_name(project_dir):
    """Change package name from pl.lebihan.authnkey to com.token2.fidobridge"""
    print("Changing package name...")
    
    old_package = "pl.lebihan.authnkey"
    new_package = "com.token2.fidobridge"
    
    # Change in build.gradle.kts
    build_gradle = Path(project_dir) / "app" / "build.gradle.kts"
    if build_gradle.exists():
        content = build_gradle.read_text()
        content = content.replace(old_package, new_package)
        build_gradle.write_text(content)
        print(f"  Updated {build_gradle}")
    
    # Rename directories
    old_path = Path(project_dir) / "app" / "src" / "main" / "java" / "pl" / "lebihan" / "authnkey"
    new_base = Path(project_dir) / "app" / "src" / "main" / "java" / "com" / "token2" / "fidobridge"
    
    if old_path.exists():
        new_base.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(old_path), str(new_base))
        print(f"  Moved source files to {new_base}")
        
        # Clean up old directories
        old_base = Path(project_dir) / "app" / "src" / "main" / "java" / "pl"
        if old_base.exists() and not any(old_base.iterdir()):
            shutil.rmtree(old_base)
    
    # Update package declarations in all Kotlin files
    for kt_file in new_base.glob("**/*.kt" ):
        content = kt_file.read_text()
        content = re.sub(
            f"^package {re.escape(old_package)}",
            f"package {new_package}",
            content,
            flags=re.MULTILINE
        )
        kt_file.write_text(content)
        
      
    
    # Update imports in other source directories
    test_base = Path(project_dir) / "app" / "src" / "test" / "java"
    if test_base.exists():
        for kt_file in test_base.glob("**/*.kt" ):
            content = kt_file.read_text()
            content = content.replace(old_package, new_package)
            kt_file.write_text(content)
            
    # Update imports in other source directories
    test_base = Path(project_dir) / "app" / "src" / "test" / "java"
    if test_base.exists():
        for kt_file in test_base.glob("**/*.xml" ):
            content = kt_file.read_text()
            content = content.replace(old_package, new_package)
            kt_file.write_text(content)   

# Iterate over all XML files
    for xml_file in Path(project_dir).rglob("*.xml"):
        try:
            content = xml_file.read_text(encoding="utf-8")
        # Replace old package references in element names
            content_new = re.sub(rf"\b{re.escape(old_package)}\.", f"{new_package}.", content)
        
            if content != content_new:
                xml_file.write_text(content_new, encoding="utf-8")
                print(f"Updated {xml_file}")
        except Exception as e:
            print(f"Failed to update {xml_file}: {e}")            
         

def replace_strings(project_dir):
    """Replace 'Authnkey' with 'FIDO Bridge' in all strings.xml files"""
    print("Replacing 'Authnkey' with 'FIDO Bridge' in strings.xml files...")
    
    res_dir = Path(project_dir) / "app" / "src" / "main" / "res"
    
    if not res_dir.exists():
        print(f"  Warning: {res_dir} not found")
        return
    
    # Find all strings.xml files in values* directories
    for strings_file in res_dir.glob("values*/strings.xml"):
        try:
            content = strings_file.read_text(encoding='utf-8')
            # Replace Authnkey with FIDO Bridge (case-insensitive variations)
            content = re.sub(r'Authnkey', 'FIDO Bridge', content, flags=re.IGNORECASE)
            content = re.sub(r'authnkey', 'FIDO Bridge', content)
            content = re.sub(r'AuthnKey', 'FIDO Bridge', content)
            strings_file.write_text(content, encoding='utf-8')
            print(f"  Updated {strings_file}")
        except Exception as e:
            print(f"  Error updating {strings_file}: {e}")

def add_button_to_layout(project_dir):
    """Add Token2 Companion App button to activity_main.xml"""
    print("Adding Token2 Companion App button to layout...")
    
    layout_file = Path(project_dir) / "app" / "src" / "main" / "res" / "layout" / "activity_main.xml"
    
    if not layout_file.exists():
        print(f"  Warning: {layout_file} not found")
        return
    
    content = layout_file.read_text()
    
    # Button XML to add before closing tag
    button_xml = '''
    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="16dp">
        
        <TextView
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="For advanced FIDO management features, use Token2 Companion App"
            android:textSize="14sp"
            android:gravity="center"
            android:paddingBottom="8dp" />
        
        <Button
            android:id="@+id/token2_button"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:text="Token2 Companion App" />
    </LinearLayout>
    '''
    
    # Find the last closing tag and insert before it
    closing_tag_pattern = r'(</.*>)\s*$'
    if re.search(closing_tag_pattern, content):
        content = re.sub(closing_tag_pattern, button_xml + r'\n\1', content)
        layout_file.write_text(content)
        print(f"  Updated {layout_file}")
    else:
        print(f"  Error: Could not find closing tag in {layout_file}")

def load_icon_source(source, dest_path):
    """Load an icon from a URL or copy from local file"""
    try:
        source_path = Path(source)
        
        # Check if it's a local file
        if source_path.exists() and source_path.is_file():
            shutil.copy(source, dest_path)
            return True
        
        # Otherwise try to download from URL
        import urllib.request
        urllib.request.urlretrieve(source, dest_path)
        return True
    except Exception as e:
        print(f"  Warning: Could not load icon from {source}: {e}")
        return False

def generate_placeholder_icon(dest_path, size=512):
    """Generate a placeholder icon using PIL if available"""
    try:
        from PIL import Image, ImageDraw
        
        # Create a simple icon with Token2 branding
        # Convert #ff3565 hex to RGB
        token2_color = (255, 53, 101)
        img = Image.new('RGB', (size, size), color=token2_color)
        draw = ImageDraw.Draw(img)
        
        # Draw a simple circle with white
        margin = size // 6
        draw.ellipse(
            [margin, margin, size - margin, size - margin],
            fill=(255, 255, 255),
            outline=token2_color,
            width=5
        )
        
        img.save(dest_path)
        return True
    except ImportError:
        print(f"  Warning: PIL not available, skipping icon generation")
        return False
    except Exception as e:
        print(f"  Warning: Could not generate icon: {e}")
        return False

def replace_icons(project_dir, icon_source=None):
    """Replace all icons in the project with Token2 branding"""
    print("Replacing icons with Token2 branding...")
    
    res_dir = Path(project_dir) / "app" / "src" / "main" / "res"
    
    if not res_dir.exists():
        print(f"  Warning: {res_dir} not found")
        return
    
    # First, remove all existing icon files from mipmap directories
    print("  Removing existing icons...")
    for mipmap_dir in res_dir.glob("mipmap*"):
        if mipmap_dir.is_dir():
            # Remove PNG files
            for icon_file in mipmap_dir.glob("*.png"):
                try:
                    icon_file.unlink()
                    print(f"  Deleted {icon_file}")
                except Exception as e:
                    print(f"  Warning: Could not delete {icon_file}: {e}")
            
            # Remove WebP files
            for icon_file in mipmap_dir.glob("*.webp"):
                try:
                    icon_file.unlink()
                    print(f"  Deleted {icon_file}")
                except Exception as e:
                    print(f"  Warning: Could not delete {icon_file}: {e}")
    
    # Icon sizes and their drawable folders
    # Sizes are in dp, but we generate at higher resolution (4x) for better quality
    icon_configs = {
        'mipmap-ldpi': 144,    # 36dp * 4
        'mipmap-mdpi': 192,    # 48dp * 4
        'mipmap-hdpi': 288,    # 72dp * 4
        'mipmap-xhdpi': 384,   # 96dp * 4
        'mipmap-xxhdpi': 576,  # 144dp * 4
        'mipmap-xxxhdpi': 768, # 192dp * 4
    }
    
    icon_names = ['ic_launcher.png', 'ic_launcher_foreground.png', 'ic_launcher_round.png', 'ic_launcher_playstore.png']
    
    for folder, size in icon_configs.items():
        folder_path = res_dir / folder
        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True)
        
        for icon_name in icon_names:
            icon_path = folder_path / icon_name
            
            # If icon source is provided, load it
            if icon_source:
                if load_icon_source(icon_source, str(icon_path)):
                    print(f"  Loaded {icon_path}")
                    continue
            
            # Otherwise generate a placeholder
            if generate_placeholder_icon(str(icon_path), size=size):
                print(f"  Generated placeholder {icon_path}")
            else:
                print(f"  Skipped {icon_path} (PIL not available)")
    
    # Also update ic_launcher.xml files in color directories
    for color_dir in res_dir.glob("values*/"):
        ic_launcher_xml = color_dir / "ic_launcher_background.xml"
        if ic_launcher_xml.exists():
            content = ic_launcher_xml.read_text()
            # Change color to Token2 pink/red (#ff3565)
            content = re.sub(r'<color[^>]*>.*?</color>', '<color name="ic_launcher_background">#ff3565</color>', content)
            ic_launcher_xml.write_text(content)
            print(f"  Updated {ic_launcher_xml}")
    
    # Replace ic_launcher-playstore.png in app/src/main directory
    playstore_icon_path = Path(project_dir) / "app" / "src" / "main" / "ic_launcher-playstore.png"
    if playstore_icon_path.exists():
        try:
            playstore_icon_path.unlink()
            print(f"  Deleted {playstore_icon_path}")
        except Exception as e:
            print(f"  Warning: Could not delete {playstore_icon_path}: {e}")
    
    # Generate new playstore icon if icon source is provided
    if icon_source:
        if load_icon_source(icon_source, str(playstore_icon_path)):
            print(f"  Loaded custom icon to {playstore_icon_path}")
    else:
        # Generate placeholder playstore icon (512x512)
        if generate_placeholder_icon(str(playstore_icon_path), size=512):
            print(f"  Generated placeholder {playstore_icon_path}")

def add_launch_function_to_mainactivity(project_dir):
    """Add function to launch Token2 Companion App in MainActivity.kt"""
    print("Adding Token2 Companion App launcher function...")
    
    main_activity = Path(project_dir) / "app" / "src" / "main" / "java" / "com" / "token2" / "fidobridge" / "MainActivity.kt"
    
    if not main_activity.exists():
        print(f"  Warning: {main_activity} not found")
        return
    
    content = main_activity.read_text()
    
    # Functions to add
    launcher_function = '''
    
    private fun openPlayStore(packageName: String) {
        val context = this
        try {
            context.startActivity(
                android.content.Intent(
                    android.content.Intent.ACTION_VIEW,
                    android.net.Uri.parse("https://play.google.com/store/apps/details?id=$packageName")
                )
            )
        } catch (e: Exception) {
            // Fallback if Play Store app is not available
        }
    }
    
    private fun launchToken2App() {
        val token2PackageName = "com.token2.companion"
        val context = this
        
        try {
            // Try to launch the app if installed
            val intent = context.packageManager.getLaunchIntentForPackage(token2PackageName)
            if (intent != null) {
                context.startActivity(intent)
            } else {
                // App not installed, go to Play Store
                openPlayStore(token2PackageName)
            }
        } catch (e: Exception) {
            // Fallback to Play Store
            openPlayStore(token2PackageName)
        }
    }
    '''
    
    # Find onCreate method and insert functions just before it
    oncreate_pattern = r'(\s+override fun onCreate\()'
    if re.search(oncreate_pattern, content):
        content = re.sub(oncreate_pattern, launcher_function + r'\n    \1', content)
        main_activity.write_text(content)
        print(f"  Added functions before onCreate in {main_activity}")
    else:
        print(f"  Warning: Could not find onCreate method in {main_activity}")
    
    # Now add button setup code after setContentView in onCreate
    setup_button_code = '''
        
        // Setup Token2 button listener
        findViewById<android.widget.Button>(R.id.token2_button)?.setOnClickListener {
            launchToken2App()
        }
    '''
    
    # Find setContentView and add after it
    setcontentview_pattern = r'(setContentView\(.*?\))'
    if re.search(setcontentview_pattern, content):
        content = re.sub(setcontentview_pattern, r'\1' + setup_button_code, content)
        main_activity.write_text(content)
        print(f"  Added button listener after setContentView in {main_activity}")

def main():
    """Main execution"""
    repo_url = "https://github.com/mimi89999/Authnkey.git"
    target_dir = "./Authnkey-Token2"
    
    # CONFIGURATION: Specify your custom icon here
    # Option 1: Use a local file path (e.g., "./my_icon.png")
    # Option 2: Use a URL (e.g., "https://example.com/icon.png")
    # Option 3: Leave as None to generate a placeholder icon
    CUSTOM_ICON = "./FIDOBridge.png"  # Change this to your icon path or URL
    
    print("=" * 60)
    print("Authnkey to Token2 FidoBridge Customization Script")
    print("=" * 60)
    
    # Step 1: Clone
    if not clone_repo(repo_url, target_dir):
        print("Failed to clone repository")
        sys.exit(1)
    
    # Step 2: Change package name
    change_package_name(target_dir)
    
    # Step 3: Replace strings
    replace_strings(target_dir)
    
    # Step 4: Add button to layout
    add_button_to_layout(target_dir)
    
    # Step 4: Replace icons
    replace_icons(target_dir, icon_source=CUSTOM_ICON)
    
    # Step 5: Add launcher function
    add_launch_function_to_mainactivity(target_dir)
    
    print("\n" + "=" * 60)
    print("Customization complete!")
    print(f"Modified project is in: {target_dir}")
    print("=" * 60)
    print("\nChanges made:")
    print("  ✓ Package name changed to com.token2.fidobridge")
    print("  ✓ 'Authnkey' replaced with 'FIDO Bridge' in strings.xml")
    print("  ✓ Token2 Companion App button added to layout")
    print("  ✓ Launcher function added to MainActivity.kt")
    print("  ✓ Icons replaced with Token2 branding")
    print("\nNext steps:")
    print("1. Review the changes in the generated files")
    print("2. Test the build: cd {} && ./gradlew assembleDebug".format(target_dir))
    print("3. Check R.id references are properly imported")
    print("4. Commit your changes")

if __name__ == "__main__":
    main()
