# -*- coding: utf-8 -*-
 
"""Simple HTTP Server With Upload and del
"""
 
 
__version__ = "1.0"
__all__ = ["fileServer"]
 
import os, sys
import os.path, time
import posixpath
import http.server
import socketserver
import urllib.request, urllib.parse, urllib.error
import html
import shutil
import mimetypes
import re
import argparse
import base64
import socket# 获取ip地址
from datetime import datetime# 时间

# 启动时间
date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print("----------------------------------------")
print (f"服务器启动时间:{date_now}")
print("----------------------------------------")

# 获取本机电脑名
myname = socket.getfqdn(socket.gethostname(  ))

# 获取本机ip
myaddr = socket.gethostbyname(myname)
print("计算机名称:",myname)
print("本机IP:",myaddr)


from io import BytesIO
global file_del,path_del,enc,path_del_map
file_del,path_del,path_del_map='del','d_y',{'/favicon.ico/':5000000000}
enc = sys.getfilesystemencoding()
def fbytes(num):
    n=[9-i for i in range(10) if int(num)>1024**(9-i)][0] if num else 0
    return f"{num/float(1024**n):.2f}{'KMGTPPE'[n-1]}b" if n else f"{num}b"

def log(*str):
    return
    print(str)

class fileServer(http.server.BaseHTTPRequestHandler):
 
    server_version = "SimpleHTTPWithUploadandDel/" + __version__
 
    def do_GET(self):
        global path_del_map
        """获取路径，忽视已删除的删除路径"""
        log(77,self.path)
        if self.path in path_del_map.keys():
            path_1=os.path.dirname(self.path[:-1])
            self.path=os.path.dirname(path_1[:-1]) if len(path_1)>1 else path_1
        log(771,self.path)
        [path_del_map.pop(k) for k in [i for i in path_del_map.keys()] if time.time()>path_del_map[k]+3]
        f = self.send_head()
        if f:
            shutil.copyfileobj(f, self.wfile)
            f.close()
 
    def do_HEAD(self):
        """请求头"""
        log(88,self.path)
        f = self.send_head()
        if f:
            f.close()
 
    def do_POST(self):
        """上传"""
        r, info = self.deal_post_data()
        log((r, info, "by: ", self.client_address))
        file_path=info.split("'")[1]
        f = BytesIO()
        f.write(b'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write("<html>\n<title>文件上传结果</title>\n".encode("GBK"))
        f.write(b'<style type="text/css">\n')
        f.write(b'* {font-family: Helvetica; font-size: 16px; }\n')
        f.write(b'a { text-decoration: none; }\n')
        f.write(b'</style>\n')
        f.write(b"<body>\n<h2>"+("文件【%s】上传结果"%(os.path.basename(file_path)  if r else "")).encode("GBK")+b"</h2><hr>\n")
        if r:

            f.write(b"<strong>"+("禁止上传该文件！" if self.is_self(file_path) else "上传成功！").encode("GBK")+b"</strong>\n")
            f.write(b"&nbsp&nbsp<a href=\"%s\">" % (self.headers['referer']).encode("GBK") + f"<button>返回目录</button></a>\n".encode("GBK")) if len(self.path)>1 else 0
            f.write(f"&nbsp&nbsp<a href=\"/\"><button>返回根目录</button></a>\n".encode("GBK") )
            f.write(b"<br/>"+f"文件时间【{self.getctime(file_path)}】，文件大小【{fbytes(os.path.getsize(file_path))}】，文件名【{os.path.basename(file_path)}】".encode('GBK'))
            f.write(b"<br/>"+f"文件路径【{file_path}】".encode("GBK"))
        else:
            f.write(b"<strong>"+"上传失败！".encode("GBK")+b"</strong>\n")
            f.write(b"<a href=\"%s\">" % (self.headers['referer']).encode() + b"<button>" + "返回目录".encode("GBK") + b"</button></a>\n")
        f.write(b"<hr><form ENCTYPE=\"multipart/form-data\" method=\"post\">")
        f.write(b"<input name=\"file\" type=\"file\" multiple/>")
        f.write("<input type=\"submit\" value=\"上传文件\"/></form>\n".encode("GBK"))
        f.write(b"<hr></body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        if f:
            shutil.copyfileobj(f, self.wfile)
            f.close()

    def deal_post_data(self):
        uploaded_files = []   
        content_type = self.headers['content-type']
        if not content_type:
            return (False, "Content-Type header doesn't contain boundary")
        boundary = content_type.split("=")[1].encode()
        remainbytes = int(self.headers['content-length'])
        line = self.rfile.readline()
        remainbytes -= len(line)
        if not boundary in line:
            return (False, "Content NOT begin with boundary")
        while remainbytes > 0:
            line = self.rfile.readline()
            remainbytes -= len(line)
            print(line)
            try:
                fn = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"', line.decode("GBK"))
            except:
                fn = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"', line.decode(enc))
            if not fn:
                return (False, "Can't find out file name...")
            log(fn,self.path)
            path_del_num=self.path.find(path_del)
            self.path=os.path.dirname(self.path[:path_del_num-1]) if path_del_num>0 else self.path

            log(fn,self.path)
            path = self.translate_path(self.path)
            fn = os.path.join(path, fn[0])
            line = self.rfile.readline()
            remainbytes -= len(line)
            line = self.rfile.readline()
            remainbytes -= len(line)
            log(fn,path,self.path)
            try:
                out = open(fn, 'wb')
            except IOError:
                return (False, "<br><br>Can't create file to write.<br>Do you have permission to write?")
            else:
                with out:
                    preline = self.rfile.readline()
                    remainbytes -= len(preline)
                    while remainbytes > 0:
                        line = self.rfile.readline()
                        remainbytes -= len(line)
                        if boundary in line:
                            preline = preline[0:-1]
                            if preline.endswith(b'\r'):
                                preline = preline[0:-1]
                            out.write(preline)
                            uploaded_files.append(fn)
                            break
                        else:
                            out.write(preline)
                            preline = line
        return (True, "<br><br>'%s'" % "'<br>'".join(uploaded_files))

    def make_dir(self,path):
        if not(os.path.isfile(path)) and not(os.path.isdir(path)):
            os.makedirs(path)

    def is_self(self,fullname):
        return os.path.normcase(fullname) == os.path.normcase(sys.argv[0])


    def do_del(self, path):
        global file_del,path_del,path_del_map
        file_del_len,dir_del_len,find_file_del,find_self_del=len(file_del),len(path_del),path.find(file_del),self.path.find(file_del)
        log(11,path, self.path)
        if path.find(file_del)>0 :
            file_path=path[:find_file_del]
            test1=os.remove(file_path) if os.path.isfile(file_path) and find_self_del>1 and not(self.is_self(file_path)) else "pass"
            test2=shutil.rmtree(path) if os.path.isdir(path) and len(path)>2  else "pass"
            log("file",test1,test2,path,self.path)
            if str(test1)!="pass" or str(test2)!="pass":
                path, self.path = os.path.dirname(path[:-1]), os.path.dirname(self.path[:-1])
        else:
            dir_path1,dir_path2 = os.path.join(path, path_del),path[:path.find(path_del)]
            test1=shutil.rmtree(dir_path1) if os.path.isdir(dir_path1) else "pass"
            test2=shutil.rmtree(dir_path2) if self.path.find(path_del)>1 and os.path.isdir(dir_path2) else "pass"
            log("dir",test1,test2,path,self.path)
            if str(test1)!="pass" or str(test2)!="pass":
                path_del_map[dir_path1]=path_del_map[dir_path2]=time.time()
                path, self.path = os.path.dirname(path[:path.find(path_del)-1]), os.path.dirname(self.path[:self.path.find(path_del)-1])
        log(22,path, self.path)
        return path

    def send_head(self):
        path = self.translate_path(self.path)
        f = None
        log('00',path,self.path)
        self.make_dir(path)
        path=self.do_del(path)
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        log(33,path,self.path)
        ctype = self.guess_type(path)
        try:
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f
 
    def getctime(self,fullname):
        time0=time.localtime(os.path.getctime(fullname))
        wekmap=dict(zip(range(7),"一二三四五六日"))
        return time.strftime("%F %H:%M:%S",time0).replace(" ","星期"+wekmap[time0.tm_wday])

    def list_directory(self, path):
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = BytesIO()
        log(66,path,self.path,enc)
        displaypath = html.escape(urllib.parse.unquote(self.path))
        f.write(b'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write(b'<html>\n')
        f.write(('<meta http-equiv="Content-Type" '
                 'content="text/html; charset=%s">' % enc).encode(enc))
        f.write(("<title>当前目录 %s</title>\n" % displaypath).encode(enc))
        f.write(b'<style type="text/css">\n')
        f.write(b'* {font-family: Helvetica; font-size: 16px; }\n')
        f.write(b'a { text-decoration: none; }\n')
        f.write(b'a:link { text-decoration: none; font-weight: bold; color: #0000ff; }\n')
        f.write(b'a:visited { text-decoration: none; font-weight: bold; color: #0000ff; }\n')
        f.write(b'a:active { text-decoration: none; font-weight: bold; color: #0000ff; }\n')
        f.write(b'a:hover { text-decoration: none; font-weight: bold; color: #ff0000; }\n')
        f.write(b'table {\n  border-collapse: separate;\n}\n')
        f.write(b'th, td {\n  padding:0px 10px;\n}\n')
        f.write(b'</style>\n')

        f.write(("<body>\n<h2>当前目录 %s</h2>\n" % displaypath).encode(enc))
        f.write(b"<hr>\n")
        f.write(b"<form ENCTYPE=\"multipart/form-data\" method=\"post\">")
        f.write(b"<input name=\"file\" type=\"file\" multiple/>")
        f.write("<input type=\"submit\" value=\"上传文件\"/></form>\n".encode(enc))
        f.write(b"<hr>\n")
        f.write(b'<table>\n')
        f.write(b'<tr><td><a href="/" >&nbsp&nbsp&nbsp/&nbsp&nbsp</a></td><td>['+(os.path.basename(displaypath[:-1]) if displaypath[:-1] else "根目录").encode(enc)+b']</td><td><a href="../" >'+('上级目录'  if displaypath[:-1] else "").encode(enc)+b'</a></td><td>'+self.getctime(path).encode(enc)+b'</td></tr>\n')
        dir_list=[name for name in list if os.path.isdir(os.path.join(path, name)) and name!='favicon.ico']
        file_list=[name for name in list if os.path.isfile(os.path.join(path, name))]
        for name in dir_list+file_list:
            dirimage = 'data:image/gif;base64,R0lGODlhGAAYAMIAAP///7+/v7u7u1ZWVTc3NwAAAAAAAAAAACH+RFRoaXMgaWNvbiBpcyBpbiB0aGUgcHVibGljIGRvbWFpbi4gMTk5NSBLZXZpbiBIdWdoZXMsIGtldmluaEBlaXQuY29tACH5BAEAAAEALAAAAAAYABgAAANdGLrc/jAuQaulQwYBuv9cFnFfSYoPWXoq2qgrALsTYN+4QOg6veFAG2FIdMCCNgvBiAxWlq8mUseUBqGMoxWArW1xXYXWGv59b+WxNH1GV9vsNvd9jsMhxLw+70gAADs='
            fullname = os.path.join(path, name)
            if self.is_self(fullname):
                continue
            displayname = linkname = name
            fsize = fbytes(os.path.getsize(fullname))
            created_date = self.getctime(fullname)
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                dirimage = 'data:image/png;base64,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'
                displayname = name
                linkname = self.path+name + "/"
                fsize = ''
            elif os.path.islink(fullname):
                dirimage = 'data:image/gif;base64,R0lGODlhGAAYAPf/AJaWlpqampubm5ycnJ2dnZ6enp+fn6CgoKGhoaKioqOjo6SkpKWlpaampqioqKmpqaqqqqurq6ysrK2tra6urq+vr7CwsLGxsbKysrOzs7S0tLW1tba2tre3t7i4uLm5ubq6uru7u7y8vL29vb6+vr+/v8LCwsPDw8bGxtDQ0NTU1NXV1dbW1tfX19jY2Nra2tzc3N3d3eDg4OHh4eLi4uPj4+Tk5OXl5efn5+np6erq6uvr6+zs7O7u7u/v7/Dw8PHx8fLy8vPz8/T09PX19fb29vf39/j4+Pr6+vv7+/39/f7+/v///wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACwAAAAAGAAYAAAI/wCZCBxIsKDBgwgLrsigwUXChEVGYNBwIYKIJA8LFunwocKGDA8ieMg4kAiHDxRmCGyhIAEKkhtR2iCYYYEAkiNQ3ijYIQGAjDkuVFBJsIcBAhcyttCgoSCQBQcUFMn44gIFEiwE/oAqIAfJIREeQLDAZIeCAwO8IuQRowYSIxQgBFhAoQBatQaFiLCQoQIFCxEMREUwoAEPhEA0dMQwQSwCIEFYpKCR8IfiCjWYgJCr4AhJyx13CFRhQYECGBmRcKwgmmAEBCsyltBQQUfBGwUG4MjoYMOIgjsSIJBAskGGEAR3IEhw4AdJExIeyBCIY/kBHySZLNEwgcGGDQYQNBbPLpAIBgULEhB4AIQ8wRMFBIhQ4j4gADs='
                displayname = name + "@"
            elif name.endswith(('.bmp','.gif','.jpg','.png','.ico')):
                dirimage = name
            elif name.endswith(('.avi','.mpg')):
                dirimage = 'data:image/gif;base64,R0lGODlhGAAYAMIAAP///7+/v7u7u1ZWVTc3NwAAAAAAAAAAACH+RFRoaXMgaWNvbiBpcyBpbiB0aGUgcHVibGljIGRvbWFpbi4gMTk5NSBLZXZpbiBIdWdoZXMsIGtldmluaEBlaXQuY29tACH5BAEAAAEALAAAAAAYABgAAANvGLrc/jAuQqu99BEh8OXE4GzdYJ4mQIZjNXAwp7oj+MbyKjY6ntstyg03E9ZKPoEKyLMll6UgAUCtVi07xspTYWptqBOUxXM9scfQ2Ttx+sbZifmNbiLpbEUPHy1TrIB1Xx1cFHkBW4VODmGNjQ4JADs='
            elif name.endswith(('.idx','.srt','.sub')):
                dirimage = 'data:image/gif;base64,R0lGODlhGAAYAPf/AAAbDiAfDSoqHjQlADs+J3sxJ0BALERHMk5LN1pSPUZHRk9NQU1OR05ZUFBRRFVXTVdYTVtVQFlVRFtbSF5bTVZWUltbUFlZVFtcVlxdWl5eWl1gWmBiV2FiXWNhXGRjXWlpYmtqZ2xtZmxsaG5ubHJva3Jzb3J0bHN0b3Z5dHd8eXh4dX18dXx/dnt8e31+eahMP4JdWIdnZox4cpVoYKJkXrxqablwcNA6Otg7O/8AAPwHB/0GBvgODvsMDPMbG/ceHvkSEuYqKvYqKvU2NvM6OvQ6OsFQUNVbW8N4eNd0duNeXu9aWvFUVOVqau1jY+1mZu5mZuh5eYSFgIWGgYaFgIiGgYqKiY6LioyMiY2NiYyMio2OiI6OjZCSjZSQi5OSkJGUkpSVk5WVlJWVlZiZlpiZmJ6emp2dnZSko6GhnKGhoKOjoaKnoqSkpKSmpKWmpaampqqrqKurqKqrqq2sqq6urrSyrrCwsLa3tb63tbi4t7q6ur+/vsCbm96Li9iUlMqursmwr9KwsN69veSCguiMjOiOjuaQkOWVleaXmOGfn+aYmOaamuebm+adneecnOeenuiQkOWgoOWsrOasrOWxseW2tue3t+e8vOi+vsHBwcfHx8jIxs7Mx8nJyMvLy8zMy83NzM7Pzs/Pz9PR0dTU1NXV1dXW1tbW1tfX19bb29jY2NnZ2djb29ra2tvb2tvb29za2tzc3N3d3d7e3t/f3+bCwufDw+fGxuTJyejCwujHx+nHx+vPz+rT0+rU1OrX1+vX1+rY2Ojf3+Hh4eLi4uPj4+Hn5+Tk5OXl5ebm5ufn5+nn5+jo6Onp6erp6evr6+zs7PDn5/Dq6vDt7fHv7/Lu7vPu7vPv7/Dw8PHx8fLy8vPz8/Tx8fbz8/T09PX19fX39/b29vj39/j4+Pn4+Pn5+fr5+fr6+vv7+/z7+/z8/P39/f7+/v/+/v///wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACwAAAAAGAAYAAAI/wDhCRxIsKDBgwgTZis00F27hAbRNSpSaSC7ZM6ePQsXjdmzZekKUpOio0lBVShjJXvYjp07gsEm/dLhqKC2aNG2LesES13BXJTg4dLBi2C7kPDSyQFTRY26c8akZbolkJGOaQTZFTO2LA8KCCA+zDFTp4aggVCCmCtYrJUxNiI4nAjh4o2HGW1CrhvCxGC5cOVqvcCgQQUWGRtanOkG75qOQwXbhWvZ7lOZMIGSsJjihY5AYTowFWRnipUtT6BGWIARY8IXPc1eXtIxrKC7cqJCjdJCIcIBAwRoaLqU6IkRHthGnwPzoEGKDBISMHDAZWAvHUTWjaa1J42NAgAELMBAMGCNwHbWekQxqA4VMkBKSokZE8AKtHLpjuHxo0OSQXfuLKJIOHdc0IECFaxgQivpxHGDDpYc9McS5oBTAhxUbNHFFX2I4Q4fR+iwi0GPCCGLK6rYgQYJWZDhBil7cMMJDjpAAg85L8ETCRDVqAONMuGMA0446rDjEzzi5KDDD4j48g48huxAyCqtODNZOeWcM85DAxEDzDcE+YDEK5u0EostbZ2SyizsQASPE4PAo4466TxVZzptuqmLN266GRAAOw=='
            elif name.endswith('.iso'):
                dirimage = 'data:image/png;base64,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'
                # Note: a link to a directory displays with @ and links with /
            f.write(('<tr><td><img src="%s" width="24" height="24"></td><td><a href="%s">%s</a></td><td style="text-align:right; font-weight: bold; color:#FF0000">%s</td><td style="text-align:right; font-weight: bold;">%s</td></tr>\n'
                    % ( dirimage, urllib.parse.quote(linkname), html.escape(displayname) , fsize , created_date )).encode(enc))
        f.write(b"</table><hr>\n</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def translate_path(self, path):
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = [_f for _f in words if _f]
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

    def guess_type(self, path):
        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']
 
    if not mimetypes.inited:
        mimetypes.init() # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        })
 
parser = argparse.ArgumentParser()
parser.add_argument('--bind', '-b', default='', metavar='ADDRESS',
                        help='Specify alternate bind address '
                             '[default: all interfaces]')

while True:
    try:
        port = int(input("设置服务器端口（1024-65535）:"))
        print ("局域网服务器地址：" , myaddr ,":", port)
        print("----------------------------------------")
        break
    except ValueError:
        print("您输入的内容太奇怪，请再次尝试输入！！！")

parser.add_argument('port', action='store',        
                        default=port, type=int,
                        nargs='?',
                        help='Specify alternate port [default: 8000]')
args = parser.parse_args()

PORT = args.port
BIND = args.bind
HOST = BIND

if HOST == '':
	HOST = 'localhost'

Handler = fileServer

with socketserver.TCPServer((BIND, PORT), Handler) as httpd:
	serve_message = "Serving HTTP on {host} port {port} (http://{host}:{port}/) ..."
	log(serve_message.format(host=HOST, port=PORT))
	httpd.serve_forever()

