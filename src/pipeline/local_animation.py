"""Reusable local motion graphics: CPU rendering, no network or model calls."""
import math
import os
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path

PRESETS = ('stone_transport', 'stone_ramp', 'giza_cinematic')


def is_local_scene(scene):
    specification = scene.get('animation')
    if specification is None:
        return False
    if not isinstance(specification, dict) or specification.get('preset') not in PRESETS:
        raise ValueError('animation phải có preset stone_transport, stone_ramp hoặc giza_cinematic.')
    return True


@lru_cache(maxsize=32)
def font(size, bold=False):
    from PIL import ImageFont
    suffix = '-Bold' if bold else ''
    candidates = [Path(f'/usr/share/fonts/truetype/dejavu/DejaVuSans{suffix}.ttf'),
                  Path('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf')]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default(size=size)


def frame(preset, progress, width=960, height=540):
    if preset == 'giza_cinematic':
        from .local_cinematic import frame as cinematic_frame
        return cinematic_frame(progress, width, height)
    from PIL import Image, ImageDraw
    image = Image.new('RGB', (width, height), '#111d26')
    draw = ImageDraw.Draw(image)
    sx, sy = width/960, height/540
    def xy(point): return (round(point[0]*sx), round(point[1]*sy))
    def rect(bounds, fill, outline=None):
        draw.rectangle([xy(bounds[:2]), xy(bounds[2:])], fill=fill, outline=outline)
    def polygon(points, fill): draw.polygon([xy(p) for p in points], fill=fill)
    def line(points, color, thickness=2): draw.line([xy(p) for p in points], fill=color, width=max(1,round(thickness*sx)))
    def text(position, value, size=20, fill='#f2e4c2', bold=False):
        draw.text(xy(position), value, font=font(max(8,round(size*sx)),bold), fill=fill)
    p = max(0, min(1, progress))
    ease = p*p*(3-2*p)
    text((42,57),'VẬN CHUYỂN ĐÁ' if preset=='stone_transport' else 'ĐƯA ĐÁ LÊN CAO',30,bold=True)
    text((42,104),'SƠ ĐỒ MINH HỌA · Không phải bản đồ địa lý' if preset=='stone_transport' else 'MÔ HÌNH GIẢ THUYẾT · Không xác nhận thiết kế tại Giza',13,'#96a8ad')
    # Reusable sand plane and a schematic pyramid silhouette.
    polygon([(0,180),(960,155),(960,540),(0,540)],'#c1a76d')
    polygon([(0,360),(480,310),(960,355),(960,540),(0,540)],'#a78a52')
    polygon([(650,190),(530,350),(775,350)],'#dec98f')
    polygon([(650,190),(775,350),(835,320)],'#b79a60')
    line([(650,190),(775,350)],'#edda9f',2)
    if preset=='stone_transport':
        # A deliberately schematic waterway: no invented geographic coordinates.
        polygon([(95,210),(175,195),(325,245),(435,310),(565,330),(600,365),(545,390),(410,365),(285,285),(165,250),(110,265)],'#315f6b')
        line([(135,229),(301,266),(421,338),(558,363)],'#82a4aa',2)
        route=[(135,229),(301,266),(421,338),(558,363)]
        section=min(2,int(ease*3));local=ease*3-section
        if p>=1: section,local=2,1
        start,end=route[section],route[section+1]
        bx=start[0]+(end[0]-start[0])*local
        by=start[1]+(end[1]-start[1])*local
        line(route[:section+1]+[(bx,by)],'#f5df9a',4)
        polygon([(bx-34,by-3),(bx+34,by-3),(bx+22,by+13),(bx-22,by+13)],'#593f2c')
        rect((bx-19,by-25,bx+2,by-4),'#eee0bb')
        rect((bx+3,by-20,bx+20,by-4),'#d7c79d')
        line([(bx+22,by),(bx+41,by+22)],'#563e2f',3)
        for offset in (-19,0,18): line([(bx-25+offset,by+22),(bx-12+offset,by+22)],'#d1e4da',1)
        text((50,290),'MỎ ĐÁ TURA',15,'#293433',True)
        text((620,368),'CÔNG TRƯỜNG GIZA',15,'#293433',True)
        text((42,440),'ĐÁ VÔI → THUYỀN → ĐƯỜNG THỦY → CÔNG TRƯỜNG',18,bold=True)
    else:
        polygon([(160,390),(600,245),(620,274),(180,419)],'#e1c68a')
        line([(160,390),(600,245)],'#f3e2ad',3)
        bx=220+ease*330;by=365-ease*109
        polygon([(bx-27,by-39),(bx+22,by-50),(bx+33,by-11),(bx-17,by)],'#e9d6a6')
        polygon([(bx+22,by-50),(bx+40,by-41),(bx+49,by-4),(bx+33,by-11)],'#b89b64')
        line([(bx+34,by-18),(bx+110,by-43)],'#65502f',3)
        for i in range(3):
            x=bx+65+i*25;y=by-14-i*8
            draw.ellipse([xy((x-5,y-26)),xy((x+5,y-16))],fill='#503c2c')
            line([(x,y-15),(x+5,y),(x-1,y+12)],'#503c2c',4)
            line([(x+5,y),(x+15,y+9)],'#503c2c',3)
        text((42,440),'ĐƯỜNG DỐC · DÂY KÉO · PHỐI HỢP LAO ĐỘNG',18,bold=True)
    rect((42,500,918,503),'#465249')
    rect((42,500,42+876*p,503),'#e9cd83')
    return image


def render(preset, output, duration=8, width=960, height=540, fps=24, threads=2, frames=None):
    if preset not in PRESETS:
        raise ValueError('Preset animation không hỗ trợ.')
    if not 0 < duration <= 600 or not 2 <= width <= 3840 or not 2 <= height <= 2160 or width%2 or height%2 or not 1 <= fps <= 60:
        raise ValueError('Thời lượng/kích thước/FPS không hợp lệ; chiều rộng/cao phải chẵn.')
    count = frames if frames is not None else math.ceil(duration*fps)
    if type(count) is not int or count < 1:
        raise ValueError('Số frame không hợp lệ.')
    output = Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    temporary = output.with_name(output.stem+'.partial.mp4')
    command=['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pixel_format','rgb24',
             '-video_size',f'{width}x{height}','-framerate',str(fps),'-i','pipe:0',
             '-frames:v',str(count),'-an','-c:v','libx264','-preset','veryfast','-crf','20',
             '-threads',str(max(1,min(threads,os.cpu_count() or 1))),'-pix_fmt','yuv420p','-movflags','+faststart',str(temporary)]
    with tempfile.TemporaryFile() as errors:
        process=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=errors)
        try:
            for index in range(count):
                process.stdin.write(frame(preset,index/max(1,count-1),width,height).tobytes())
            process.stdin.close()
            code=process.wait()
            if code:
                errors.seek(0)
                raise RuntimeError('FFmpeg animation lỗi: '+errors.read().decode(errors='replace')[-1500:])
            temporary.replace(output)
        except BaseException:
            if process.poll() is None:
                process.kill();process.wait()
            if process.stdin and not process.stdin.closed:
                process.stdin.close()
            temporary.unlink(missing_ok=True)
            raise
    return output


def main(argv=None):
    import argparse
    parser=argparse.ArgumentParser(description='Animation cục bộ: không gọi API/LLM')
    parser.add_argument('--preset',choices=PRESETS,default='stone_transport')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--duration',type=float,default=8)
    parser.add_argument('--width',type=int,default=960)
    parser.add_argument('--height',type=int,default=540)
    parser.add_argument('--fps',type=int,default=24)
    parser.add_argument('--sound',action='store_true',help='Thêm âm thanh tổng hợp cục bộ, không gọi API')
    args=parser.parse_args(argv)
    render(args.preset,args.output,args.duration,args.width,args.height,args.fps)
    if args.sound:
        from .local_cinematic import add_sound
        add_sound(args.output,args.duration)
    print(f'Animation cục bộ đã xuất: {args.output} (không gọi API).')
