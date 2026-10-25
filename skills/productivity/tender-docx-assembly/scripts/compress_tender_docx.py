#!/usr/bin/env python3
# 压缩投标 docx 到 <20MB 可聊天发送: 重采样内嵌图片, 文本/格式零改动
# 用法: python3 compress_tender_docx.py <in.docx> <out.docx> [max_side=1400] [jpg_quality=82]
import sys, zipfile, io, os
from PIL import Image

def main():
    src, out = sys.argv[1], sys.argv[2]
    max_side = int(sys.argv[3]) if len(sys.argv) > 3 else 1400
    jq = int(sys.argv[4]) if len(sys.argv) > 4 else 82
    z = zipfile.ZipFile(src)
    zo = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
    before = saved = 0
    for n in z.namelist():
        data = z.read(n); before += len(data)
        if n.startswith('word/media/') and n.lower().endswith(('.jpg', '.jpeg', '.png')):
            try:
                img = Image.open(io.BytesIO(data))
                if max(img.size) > max_side:
                    r = max_side / max(img.size)
                    img = img.resize((int(img.size[0] * r), int(img.size[1] * r)))
                buf = io.BytesIO()
                if n.lower().endswith(('.jpg', '.jpeg')):
                    img.convert('RGB').save(buf, 'JPEG', quality=jq, optimize=True)
                else:
                    img.save(buf, 'PNG', optimize=True)
                newd = buf.getvalue(); zo.writestr(n, newd); saved += len(data) - len(newd); continue
            except Exception as e:
                print('skip', n, e)
        zo.writestr(n, data)
    zo.close()
    print(f'before={before/1024/1024:.1f}MB after={os.path.getsize(out)/1024/1024:.1f}MB saved={saved/1024/1024:.1f}MB')

if __name__ == '__main__':
    main()
