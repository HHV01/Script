"""Local motion-graphics treatment of the supplied Babylon contract excerpt."""
import argparse
import json
import math
import random
import subprocess
import tempfile
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter
from .local_animation import font

WIDTH, HEIGHT = 720, 1280
TIMES = (0, 6.32, 11.36, 17)
TITLES = ('BỌC KÍN BẢN GỐC', 'KHẮC LẠI BÊN NGOÀI', 'LĂN DẤU XÁC NHẬN')
CAPTIONS = (
    'Tiếp theo, thư lại nặn một lớp đất sét mỏng bao bọc hoàn toàn phiến đá ban đầu, giống như một chiếc phong bì kín mít.',
    'Trên lớp vỏ ngoài này, toàn bộ nội dung hợp đồng lại được khắc lại một lần nữa, y hệt như bên trong.',
    'Cuối cùng, các bên và nhân chứng dùng con dấu lăn hình trụ của riêng mình, lăn lên lớp đất sét ướt bên ngoài… để tạo thành dải hoa văn độc nhất vô nhị.',
)


def ease(x):
    x=max(0,min(1,x));return x*x*(3-2*x)


def material(seed=11, dark=False):
    image=Image.new('RGBA',(620,390));mask=Image.new('L',image.size)
    ImageDraw.Draw(mask).rounded_rectangle((28,38,592,335),radius=42,fill=255)
    draw=ImageDraw.Draw(image)
    for y in range(390):
        rgb=(181-int(y*.055),119-int(y*.07),71-int(y*.04)) if dark else (211-int(y*.08),160-int(y*.09),102-int(y*.065))
        draw.line((0,y,620,y),fill=rgb+(255,))
    rng=random.Random(seed)
    for i in range(2600):
        x=rng.randrange(620);y=rng.randrange(390);r=rng.choice((1,1,2))
        tone=(183,132,81,255) if i%3 else (217,167,110,255)
        draw.ellipse((x,y,x+r,y+r),fill=tone)
    draw.rounded_rectangle((30,40,590,333),radius=40,outline=(87,52,30,255),width=4)
    draw.line((70,45,550,45),fill=(242,199,138,255),width=2)
    image.putalpha(mask)
    return image


def signs(draw,count,offset=(0,0),color=(96,57,32,255)):
    ox,oy=offset
    for i in range(min(36,max(0,int(count)))):
        row,col=divmod(i,12);x=65+col*41+ox;y=102+row*51+oy
        # Stylized marks only, not a transcription of any actual contract.
        for j in range(2+i%3):
            dx=(j%2)*12;dy=(j//2)*13
            draw.polygon([(x+dx,y+dy),(x+dx+13,y+dy-5),(x+dx+5,y+dy+8)],fill=color)
            draw.line((x+dx+5,y+dy+3,x+dx+19,y+dy+12),fill=color,width=2)


def centered(draw,text,y,size,fill,spacing=6):
    f=font(size,True)
    for line in text.split('\n'):
        box=draw.textbbox((0,0),line,font=f)
        draw.text(((WIDTH-(box[2]-box[0]))/2,y),line,font=f,fill=fill)
        y+=size+spacing


def render_frame(t,assets,clay,inner):
    stage=0 if t<TIMES[1] else 1 if t<TIMES[2] else 2
    p=(t-TIMES[stage])/(TIMES[stage+1]-TIMES[stage]);p=max(0,min(1,p))
    # Source illustration retained in a clear, larger panel; no blurred side-fill.
    image=Image.new('RGB',(WIDTH,HEIGHT),'#1e1712');draw=ImageDraw.Draw(image)
    for y in range(HEIGHT):
        u=y/HEIGHT;draw.line((0,y,WIDTH,y),fill=(int(43-18*u),int(30-12*u),int(20-8*u)))
    art=assets[stage];scale=1.015+.075*ease(p)
    art=art.resize((round(WIDTH*scale),round(345*scale)),Image.Resampling.LANCZOS)
    x=(art.width-WIDTH)//2+round(math.sin(p*math.pi)*9)
    art=art.crop((x,0,x+WIDTH,345))
    image.paste(art,(0,183))
    gradient=Image.new('RGBA',(WIDTH,345));gd=ImageDraw.Draw(gradient)
    for y in range(345):
        alpha=int(125*max(0,(y-235)/110))
        gd.line((0,y,WIDTH,y),fill=(23,17,12,alpha))
    image.paste(gradient,(0,183),gradient)
    draw=ImageDraw.Draw(image)
    centered(draw,'BABYLON · HỢP ĐỒNG ĐẤT SÉT',42,17,'#baa287')
    centered(draw,TITLES[stage],89,29,'#f5d49a')
    for i in range(3):
        x=253+i*80
        draw.rounded_rectangle((x,147,x+54,151),radius=2,fill='#e2b46e' if i<=stage else '#534333')
    # Ground shadow and local object animation.
    shadow=Image.new('RGBA',image.size);sd=ImageDraw.Draw(shadow)
    sd.ellipse((91,965,634,1043),fill=(0,0,0,140));shadow=shadow.filter(ImageFilter.GaussianBlur(17))
    image=Image.alpha_composite(image.convert('RGBA'),shadow)
    obj=Image.new('RGBA',(620,390))
    if stage==0:
        obj.alpha_composite(inner)
        d=ImageDraw.Draw(obj);signs(d,36)
        cover=ease((p-.10)/.66)
        overlay=clay.copy();mask=overlay.getchannel('A');reveal=Image.new('L',overlay.size)
        rd=ImageDraw.Draw(reveal);edge=int(310*cover)
        rd.rectangle((0,0,edge,390),fill=255);rd.rectangle((620-edge,0,620,390),fill=255)
        from PIL import ImageChops
        overlay.putalpha(ImageChops.multiply(mask,reveal));obj.alpha_composite(overlay)
        if p>.8:
            highlight=ImageDraw.Draw(obj)
            highlight.rounded_rectangle((34,44,586,329),radius=40,outline=(246,209,151,int(220*(1-(p-.8)/.2))),width=3)
        title='BẢN GỐC  →  LỚP VỎ BẢO VỆ'
    elif stage==1:
        obj.alpha_composite(clay);d=ImageDraw.Draw(obj)
        amount=min(36,int(ease(p)*36));signs(d,amount)
        pos=min(35,amount);row,col=divmod(pos,12);x=80+col*41;y=105+row*51
        # A reed stylus actually traverses each row as inscriptions appear.
        nib=(x,y+7+math.sin(t*20)*2);end=(x+74,y-126)
        d.line((nib[0]+4,nib[1]+6,end[0]+7,end[1]+6),fill=(68,41,24,110),width=11)
        d.polygon([nib,(x+69,y-130),(x+82,y-126)],fill='#e3bd78',outline='#503722')
        d.line((nib[0]+4,nib[1]-5,x+74,y-126),fill='#f4d69a',width=2)
        title='NỘI DUNG BÊN NGOÀI KHỚP BÊN TRONG'
    else:
        obj.alpha_composite(clay);d=ImageDraw.Draw(obj);signs(d,36,offset=(0,-22))
        x=75+ease(p)*465
        # Rolled impression appears behind a turning cylindrical seal.
        for j in range(24):
            xx=58+j*21
            if xx<x-19:
                d.arc((xx,264,xx+18,292),0,340,fill='#6d4126',width=3)
                d.line((xx+2,292,xx+17,263),fill='#7d4d2b',width=2)
        roller=Image.new('RGBA',(120,180));r=ImageDraw.Draw(roller)
        for xx in range(77):
            shade=int(95+70*math.sin(xx/77*math.pi))
            r.line((xx+16,22,xx+16,144),fill=(shade,shade-9,shade-17,255))
        r.ellipse((16,7,92,39),fill='#b3ac99',outline='#514b42',width=3)
        r.ellipse((16,127,92,159),fill='#8d8777',outline='#514b42',width=3)
        r.ellipse((44,15,64,30),fill='#4e4c43')
        for k in range(8):
            sx=22+((k*11+t*45)%64)
            r.line((sx,42,sx+3,119),fill='#625e52',width=2)
        obj.alpha_composite(roller,(round(x)-50,153))
        title='CON DẤU LĂN  →  DẢI HOA VĂN'
    # Small camera tilt supplies depth while preserving readable silhouettes.
    angle=-5+2*ease(p)
    obj=obj.rotate(angle,Image.Resampling.BICUBIC,expand=False)
    image.alpha_composite(obj,(50,628))
    draw=ImageDraw.Draw(image)
    centered(draw,title,563,17,'#ddbc8c')
    centered(draw,'MÔ PHỎNG THAO TÁC · KÝ HIỆU MINH HỌA',1032,12,'#a28e78')
    # Original wording, reflowed away from the moving objects.
    lines=textwrap.wrap(CAPTIONS[stage],width=55)
    y=1120+(4-len(lines))*10
    for line in lines:
        f=font(18);box=draw.textbbox((0,0),line,font=f)
        draw.text(((WIDTH-(box[2]-box[0]))/2,y),line,font=f,fill='#f2e8dc')
        y+=25
    draw.line((60,1232,660,1232),fill='#594432',width=2)
    draw.line((60,1232,60+600*t/17,1232),fill='#d5a365',width=2)
    return image.convert('RGB')


def render_excerpt(source,output):
    source,output=Path(source),Path(output)
    if not source.is_file():raise ValueError('Không tìm thấy video nguồn.')
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(source)]))
    if float(info['format']['duration'])<26.56 or not any(s['codec_type']=='audio' for s in info['streams']):
        raise ValueError('Mẫu Babylon cần video nguồn có âm thanh và dài ít nhất 26,56 giây.')
    output.parent.mkdir(parents=True,exist_ok=True)
    fps=25;duration=17;start=9.56;clay=material();inner=material(27,True)
    with tempfile.TemporaryDirectory() as directory:
        directory=Path(directory);assets=[]
        for timestamp,name in ((11,'wrap'),(17,'write'),(23,'seal')):
            file=directory/(name+'.png')
            subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',str(timestamp),'-i',str(source),
                            '-vf','crop=iw:ih*0.2695:0:ih*0.3414,scale=720:345','-frames:v','1',str(file)],check=True)
            with Image.open(file) as im:assets.append(im.convert('RGB'))
        silent=directory/'animation.mp4'
        command=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','720x1280',
                 '-r',str(fps),'-i','pipe:0','-an','-c:v','libx264','-preset','veryfast','-crf','19',
                 '-threads','2','-pix_fmt','yuv420p',str(silent)]
        with tempfile.TemporaryFile() as errors:
            process=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=errors)
            try:
                for i in range(round(duration*fps)):
                    process.stdin.write(render_frame(i/fps,assets,clay,inner).tobytes())
                process.stdin.close()
                if process.wait():
                    errors.seek(0);raise RuntimeError(errors.read().decode(errors='replace')[-1500:])
            finally:
                if process.poll() is None:process.kill();process.wait()
                if not process.stdin.closed:process.stdin.close()
        temp=output.with_name(output.stem+'.partial.mp4')
        try:
            subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(silent),'-ss',str(start),'-i',str(source),
                            '-map','0:v:0','-map','1:a:0','-t',str(duration),'-c:v','copy','-c:a','aac',
                            '-b:a','160k','-movflags','+faststart',str(temp)],check=True)
            temp.replace(output)
        finally:temp.unlink(missing_ok=True)
    return output


def main(argv=None):
    parser=argparse.ArgumentParser(description='Mẫu Babylon: giữ âm thanh nguồn 00:09.56–00:26.56, animation cục bộ')
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(argv)
    render_excerpt(args.input,args.output)
    print('Đã xuất đoạn 17 giây, giữ âm thanh gốc: '+str(args.output))


if __name__=='__main__':main()
