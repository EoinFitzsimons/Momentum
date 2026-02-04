#!/usr/bin/env python3
"""
Draw.io Export Script - Converts .drawio files to PNG using draw.io web API
"""
import os
import requests
import base64
import sys
from pathlib import Path

def export_drawio_to_png(drawio_file, png_file):
    """Export a draw.io file to PNG using draw.io API"""
    
    # Read the drawio file
    with open(drawio_file, 'rb') as f:
        drawio_content = f.read()
    
    # Encode to base64
    b64_content = base64.b64encode(drawio_content).decode('utf-8')
    
    # Use draw.io export endpoint
    url = "https://www.draw.io/export"
    
    params = {
        'format': 'png',
        'mimeType': 'application/octet-stream',
        'scale': 2,  # Higher quality
        'width': 2400,
        'height': 1600,
    }
    
    data = {
        'xml': drawio_content.decode('utf-8')
    }
    
    try:
        print(f"Exporting {drawio_file} to {png_file}...")
        
        # Try direct file upload method
        with open(drawio_file, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files, params=params, timeout=30)
        
        if response.status_code == 200:
            with open(png_file, 'wb') as f:
                f.write(response.content)
            print(f"✓ Successfully exported: {png_file}")
            return True
        else:
            print(f"✗ Export failed (status {response.status_code}): {drawio_file}")
            return False
            
    except Exception as e:
        print(f"✗ Error exporting {drawio_file}: {e}")
        return False

def main():
    diagrams_dir = Path(__file__).parent
    # Export every .drawio file in this directory
    drawio_files = [p.name for p in diagrams_dir.glob('*.drawio')]
    
    os.chdir(diagrams_dir)
    
    success_count = 0
    for drawio_file in drawio_files:
        if not os.path.exists(drawio_file):
            print(f"✗ File not found: {drawio_file}")
            continue
        
        png_file = str(diagrams_dir / drawio_file.replace('.drawio', '.png'))
        if export_drawio_to_png(str(diagrams_dir / drawio_file), png_file):
            success_count += 1
    
    print(f"\n{'='*60}")
    print(f"Export Summary: {success_count}/{len(drawio_files)} diagrams exported")
    print(f"All PNG files saved in: {diagrams_dir}")

if __name__ == '__main__':
    main()
