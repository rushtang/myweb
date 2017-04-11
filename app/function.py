import hashlib
import re
from datetime import datetime






def secure_filename(origin_name):
#用于生成安全文件名
    suffix = re.findall(r'.+?\.', origin_name[::-1])[0][::-1]     #获取文件后缀
    nowname=origin_name+str(datetime.utcnow())
    filename=hashlib.md5(nowname.encode()).hexdigest()+suffix

    return filename


def is_imgsuffix(origin_name):
#判断是否是图片后缀
    suffix = re.findall(r'.+?\.', origin_name[::-1])[0][::-1]
    if suffix in ['.jpg','.png','.gif']:
        return True
    return False

