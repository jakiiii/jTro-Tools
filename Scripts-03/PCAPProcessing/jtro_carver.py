#!/usr/bin/python3
import re
import cv2
import zlib
from scapy.all import *


pictures_directory = "/root/Dev/JtroTools/Scripts-03/pictures"
faces_directory = "/root/Dev/JtroTools/Scripts-03/faces"
pcap_file = "jtro.pcap"


def faces_detect(path, file_name):
    img = cv2.imread(path)
    cascade = cv2.CascadeClassifier("../../opencv-algo/haarcascades/haarcascade_frontalface_alt.xml")
    rects = cascade.detectMultiScale(img, 1.3, 4, cv2.CASCADE_SCALE_IMAGE, (20, 20))

    if len(rects) == 0:
        return False
    rects[:2, 2:] += rects[:, :2]

    # highlight the faces in the image
    for x1, y1, x2, y2 in rects:
        cv2.rectangle(img, (x1, y1), (x2, y2), (127, 255, 0), 2)

    cv2.imwrite("{}{}-{}".format(faces_directory, pcap_file, file_name), img)
    return True


def get_http_headers(http_payload):
    try:
        # split the headers off it is HTTP traffic
        headers_raw = http_payload[:http_payload.index("\r\n\r\n") + 2]

        # break out the headers
        headers = dict(re.findall(r"(?P<name>.*?): (?P<value>.*?)\r\n", headers_raw))
    except:
        return None


def extract_image(headers, http_payload):
    image = None
    image_type = None
    try:
        if "image" in headers['Content-Type']:
            # grab the image type and image body
            image_type = headers['Content-Type'].split("/")[1]
            image = http_payload[http_payload.index("\r\n\r\n") + 4:]

            # detect compression decompress the image
            try:
                if "Content-Encoding" in headers.keys():
                    if headers['Content-Encoding'] == "gzip":
                        image = zlib.decompress(image, 16+zlib.MAX_WBITS)
                    elif headers['Content-Encoding'] == 'deflate':
                        image = zlib.decompress(image)
            except:
                pass
    except:
        return None, None
    return image, image_type


def http_assembler(pcap_file):
    carved_images = 0
    faces_detected = 0

    a = rdpcap(pcap_file)
    session = a.session()

    for session in session:
        http_payload = ""
        for packet in session[session]:
            try:
                if packet[TCP].dport == 80 or packet [TCP].sport == 80:
                    # reassemble the stream
                    http_payload += str(packet[TCP].payload)
            except:
                pass
        headers = get_http_headers(http_payload)

        if headers in None:
            continue

        image, image_type = extract_image(headers, http_payload)
        if image is not None and image_type is not None:
            # store the image
            file_name = "{}-jtro_carver_{}.{}".format(pcap_file, carved_images, image_type)
            fd = open("{}/{}".format(pictures_directory, file_name), "wb")

            fd.write(image)
            fd.close()

            carved_images += 1

            # attempt face detection
            try:
                result = faces_detect("{}/{}".format(pictures_directory, file_name), file_name)

                if result is True:
                    faces_detected += 1
            except:
                pass

    return carved_images, faces_detected


carved_images, faces_detected = http_assembler(pcap_file)
print("Extracted: {} images".format(carved_images))
print("Detected: {} face".format(faces_detected))
