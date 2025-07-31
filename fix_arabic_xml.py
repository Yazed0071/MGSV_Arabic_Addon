import xml.etree.ElementTree as ET
from arabic_reshaper import ArabicReshaper
from bidi.algorithm import get_display
import re
import os

# Regex to detect Arabic text
arabic_re = re.compile(r'[\u0600-\u06FF]')

# Arabic reshaper with Harakat preservation
reshaper = ArabicReshaper({
    'delete_harakat': False  # <<< This keeps diacritics like َ ُ ِ
})

def fix_arabic_text(text):
    """Reshape and reorder Arabic text if needed"""
    if not text or not arabic_re.search(text):
        return text
    reshaped = reshaper.reshape(text)
    return get_display(reshaped)

def process_file(file_path):
    print(f"🔧 Processing: {file_path}")
    tree = ET.parse(file_path)
    root = tree.getroot()

    changes = 0
    for elem in root.iter():
        if 'Value' in elem.attrib:
            original = elem.attrib['Value']
            fixed = fix_arabic_text(original)
            if original != fixed:
                elem.attrib['Value'] = fixed
                changes += 1

    out_path = os.path.splitext(file_path)[0] + "_fixed.xml"
    tree.write(out_path, encoding='utf-8', xml_declaration=True)
    print(f"✅ Done: {out_path} ({changes} changes)\n")

def main():
    folder = os.path.dirname(os.path.abspath(__file__))
    xml_files = [f for f in os.listdir(folder) if f.lower().endswith('.xml')]

    if not xml_files:
        print("❌ No XML files found in this folder.")
        return

    for xml_file in xml_files:
        full_path = os.path.join(folder, xml_file)
        process_file(full_path)

if __name__ == "__main__":
    main()
