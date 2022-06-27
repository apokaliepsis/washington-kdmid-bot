import base64
import os
import random
import string
import urllib.request

from PIL import Image, ImageEnhance
from cffi.backend_ctypes import xrange
from easyocr import easyocr

from manager.manager_app import ManagerApp


class Captcha:
    def recognize_captcha(self):
        try:
            driver = ManagerApp().get_driver()
            captcha_element = driver.find_element_by_id("ctl00_MainContent_imgSecNum")

            file = self.get_captcha(driver, captcha_element)
            print("captcha_file=", file)
            text = self.recognize_image(file)
            print("Captcha: " + text)
            return text
        except Exception as e:
            print(e)

    def recognize_image(self, file_path):
        try:
            print(file_path)
            im = Image.open(file_path)
            enhancer = ImageEnhance.Contrast(im)
            factor = 2
            im_output = enhancer.enhance(factor)
            im_output.save(file_path)
            print("im_output=", im_output)
            reader = easyocr.Reader(["en"], gpu=False)
            print("reader=", reader)
            result = reader.readtext(file_path, detail=0, allowlist='0123456789')
            print("result=", result)
            self.remove_file(file_path)
            if result == []:
                return ""
            else:
                return result[0].lower().replace("!", "").replace("@", "").replace("#", "") \
                    .replace("$", "").replace("%", "").replace("^", "").replace("&", "") \
                    .replace("*", "").replace("(", "").replace(")", "").replace("-", "") \
                    .replace("+", "").replace("=", "").replace("`", "").replace("~", "") \
                    .replace("{", "").replace("}", "").replace("[", "").replace("]", "") \
                    .replace(":", "").replace(";", "").replace("'", "").replace("\"", "") \
                    .replace(",", "").replace(".", "").replace("<", "").replace(">", "") \
                    .replace("?", "").replace("/", "").replace("\\", "").replace("|", "") \
                    .replace("№", "").replace("%", "").replace(" ", "")
        except Exception as e:
            print(e)

    def remove_file(self, file_path):
        ManagerApp().get_logger().info("Remove captcha file: "+file_path)
        os.remove(file_path)

    def save_image(self, url):

        img_path = str("temp/captcha_img/") + "".join([random.choice(string.ascii_letters) for i in xrange(10)]) + str(".jpg")
        return urllib.request.urlretrieve(url, img_path)[0]

    def get_captcha(self, driver, captcha_element):
        img_base64 = driver.execute_script("""
                var ele = arguments[0];
                var cnv = document.createElement('canvas');
                cnv.width = 200; cnv.height = 50;
                cnv.getContext('2d').drawImage(ele, 0, 0);
                return cnv.toDataURL('image/jpeg').substring(22);    
                """, captcha_element)
        img_path = str("temp/captcha_img/") + "".join([random.choice(string.ascii_letters) for i in xrange(10)]) + str(".jpg")
        with open(img_path, 'wb') as f:
            f.write(base64.b64decode(img_base64))
            return img_path


if __name__ == '__main__':
    # 0111101011
    #
    #
    # img_path = "captcha.jpg"
    # urllib.request.urlretrieve("http://washington.kdmid.ru/queue/CodeImage.aspx?id=c816", img_path)
    # print(Captcha.captcha_recognition("captcha.jpg"))
    print()
