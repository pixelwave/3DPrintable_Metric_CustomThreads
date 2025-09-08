# 🚀 USER INPUT SECTION — CHANGE THESE VALUES TO CUSTOMIZE YOUR THREADS

# 🔧 Set the pitch range you want to generate:
pitch_start = .25     # Starting pitch value in mm (e.g., 1.0)
pitch_end = 3.5       # Ending pitch value in mm (e.g., 6.0)
pitch_step = 0.01      # Interval between pitches in mm (e.g., 0.5)

# 📏 Set the thread diameters you want to include:
thread_sizes = list(range(8, 51))  # Diameters from 8mm to 50mm

# ⚙️ Set tolerance offsets to simulate different thread classes:
tolerance_offsets = [0.0, 0.1, 0.2, 0.4, 0.8]

# 🧾 Set the name of the output XML file:
output_filename = "3DPrintedMetricV3.xml"

# 🧾 Metadata for the thread type
thread_name = "3D-Printed Metric Threads V3"
unit = "mm"
thread_angle = 60.0  # Standard ISO metric thread angle

# 📦 Import required modules
import math
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod

# 🔢 Generate pitch list from user input
def generate_pitch_list(start, end, step):
    pitches = []
    current = start
    while current <= end + 1e-9:
        pitches.append(round(current, 4))
        current += step
    return pitches

# 🧼 Format numbers for display
def format_number(val):
    return str(int(val)) if val == int(val) else str(val)

# 🧵 Thread object to store dimensions
class Thread:
    def __init__(self):
        self.gender = None
        self.thread_class = None
        self.major_dia = 0.0
        self.pitch_dia = 0.0
        self.minor_dia = 0.0
        self.tap_drill = None

# 🧩 Abstract base class
class ThreadProfile(ABC):
    @abstractmethod
    def sizes(self):
        pass

    @abstractmethod
    def designations(self, size):
        pass

    @abstractmethod
    def threads(self, designation):
        pass

# 🧵 Metric thread generator class
class MetricThreadGenerator(ThreadProfile):
    class Designation:
        def __init__(self, diameter, pitch):
            self.nominal_diameter = diameter
            self.pitch = pitch
            self.name = f"M{format_number(diameter)}x{format_number(pitch)}"

    def __init__(self, pitch_list):
        self.pitches = pitch_list

    def sizes(self):
        return thread_sizes

    def designations(self, size):
        return [self.Designation(size, pitch) for pitch in self.pitches]

    def threads(self, designation):
        threads = []
        P = designation.pitch
        D = designation.nominal_diameter
        H = (P / 2) / math.tan(math.radians(thread_angle / 2))
        pitch_dia = D - 2 * (3 * H / 8)
        minor_dia = D - 2 * (5 * H / 8)

        for offset in tolerance_offsets:
            class_label = f"O.{str(offset)[2:]}"  # e.g., 0.1 → "O.1"

            ext = Thread()
            ext.gender = "external"
            ext.thread_class = class_label
            ext.major_dia = D - offset
            ext.pitch_dia = pitch_dia - offset
            ext.minor_dia = minor_dia - offset
            threads.append(ext)

            int_thread = Thread()
            int_thread.gender = "internal"
            int_thread.thread_class = class_label
            int_thread.major_dia = D + offset
            int_thread.pitch_dia = pitch_dia + offset
            int_thread.minor_dia = minor_dia + offset
            int_thread.tap_drill = D - P
            threads.append(int_thread)

        return threads

# 🧾 XML generator
def generate_xml():
    pitch_list = generate_pitch_list(pitch_start, pitch_end, pitch_step)
    profile = MetricThreadGenerator(pitch_list)

    root = ET.Element("ThreadType")
    tree = ET.ElementTree(root)

    ET.SubElement(root, "Name").text = thread_name
    ET.SubElement(root, "CustomName").text = thread_name
    ET.SubElement(root, "Unit").text = unit
    ET.SubElement(root, "Angle").text = str(thread_angle)
    ET.SubElement(root, "SortOrder").text = "3"

    for size in profile.sizes():
        size_elem = ET.SubElement(root, "ThreadSize")
        ET.SubElement(size_elem, "Size").text = str(size)
        for designation in profile.designations(size):
            des_elem = ET.SubElement(size_elem, "Designation")
            ET.SubElement(des_elem, "ThreadDesignation").text = designation.name
            ET.SubElement(des_elem, "CTD").text = designation.name
            ET.SubElement(des_elem, "Pitch").text = str(designation.pitch)
            for thread in profile.threads(designation):
                thread_elem = ET.SubElement(des_elem, "Thread")
                ET.SubElement(thread_elem, "Gender").text = thread.gender
                ET.SubElement(thread_elem, "Class").text = thread.thread_class
                ET.SubElement(thread_elem, "MajorDia").text = f"{thread.major_dia:.4g}"
                ET.SubElement(thread_elem, "PitchDia").text = f"{thread.pitch_dia:.4g}"
                ET.SubElement(thread_elem, "MinorDia").text = f"{thread.minor_dia:.4g}"
                if thread.tap_drill is not None:
                    ET.SubElement(thread_elem, "TapDrill").text = f"{thread.tap_drill:.4g}"

    ET.indent(tree)
    tree.write(output_filename, encoding="UTF-8", xml_declaration=True)

# 🚀 Run the generator
if __name__ == "__main__":
    generate_xml()
    print(f"✅ XML file '{output_filename}' created for pitches from {pitch_start} mm to {pitch_end} mm in {pitch_step} mm steps.")

