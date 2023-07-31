import xml.etree.ElementTree as ET
import threading
import queue
import random
import time
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
from xml.dom import minidom


class ITstudent:
    def __init__(self, name, student_id, programme, courses):
        self.name = name
        self.student_id = student_id
        self.programme = programme
        self.courses = courses

def prettify(elem):
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def generate_student():
    name = f"Student {random.randint(1, 10)}"
    student_id = f"{random.randint(10000000, 99999999)}"
    programme = f"Programme {random.randint(1, 7)}"
    courses = {f"Course {i}": random.randint(0, 100) for i in range(1, 6)}
    return ITstudent(name, student_id, programme, courses)

def wrap_student(student):
    root = Element('student')
    SubElement(root, 'name').text = student.name
    SubElement(root, 'student_id').text = student.student_id
    SubElement(root, 'programme').text = student.programme
    courses_elem = SubElement(root, 'courses')
    for course_name, course_mark in student.courses.items():
        course_elem = SubElement(courses_elem, 'course')
        SubElement(course_elem, 'name').text = course_name
        SubElement(course_elem, 'mark').text = str(course_mark)
    return prettify(root)

def unwrap_student(xml_string):
    root = ET.fromstring(xml_string)
    name = root.find('name').text
    student_id = root.find('student_id').text
    programme = root.find('programme').text
    courses_elem = root.find('courses')
    courses = {}
    for course_elem in courses_elem.findall('course'):
        course_name = course_elem.find('name').text
        course_mark = int(course_elem.find('mark').text)
        courses[course_name] = course_mark
    return ITstudent(name, student_id, programme, courses)

class Producer(threading.Thread):
    def __init__(self, buffer):
        threading.Thread.__init__(self)
        self.buffer = buffer

    def run(self):
        while True:
            student = generate_student()
            xml_string = wrap_student(student)
            file_num = random.randint(1, 10)
            file_name = f"student{file_num}.xml"
            with open(file_name, 'w') as f:
                f.write(xml_string)
            self.buffer.put(file_num)
            print(f"Produced: {file_name}")
            time.sleep(random.random())

class Consumer(threading.Thread):
    def __init__(self, buffer):
        threading.Thread.__init__(self)
        self.buffer = buffer

    def run(self):
        while True:
            file_num = self.buffer.get()
            file_name = f"student{file_num}.xml"
            with open(file_name) as f:
                xml_string = f.read()
            student = unwrap_student(xml_string)
            average_mark = sum(student.courses.values()) / len(student.courses)
            passed = average_mark >= 50
            print(f"Consumed: {file_name}")
            print(f"Name: {student.name}")
            print(f"Student ID: {student.student_id}")
            print(f"Programme: {student.programme}")
            for course_name, course_mark in student.courses.items():
                print(f"{course_name}: {course_mark}")
            print(f"Average mark: {average_mark:.2f}")
            print(f"Passed: {passed}")
            open(file_name,'w').close()
            time.sleep(random.random())

buffer_size=10

buffer=queue.Queue(buffer_size)

producer=Producer(buffer)

consumer=Consumer(buffer)

producer.start()

consumer.start()

producer.join()

consumer.join()

