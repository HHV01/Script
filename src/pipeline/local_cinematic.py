"""Procedural low-poly 3D cinematography rendered locally with Pillow."""
import math
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFilter


def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def unit(v):
    length=math.sqrt(dot(v,v)) or 1
    return tuple(x/length for x in v)
def color(rgb,factor): return tuple(max(0,min(255,int(c*factor))) for c in rgb)


@lru_cache(maxsize=6)
def background(w,h):
    sky=Image.new('RGB',(w,h));d=ImageDraw.Draw(sky)
    top,bottom=(34,42,53),(221,154,95)
    for y in range(h):
        p=min(1,y/(h*.74))
        d.line((0,y,w,y),fill=tuple(int(a+(b-a)*p) for a,b in zip(top,bottom)))
    glow=Image.new('RGBA',(w,h));g=ImageDraw.Draw(glow)
    cx,cy=int(w*.77),int(h*.28);radius=int(w*.053)
    g.ellipse((cx-radius*2,cy-radius*2,cx+radius*2,cy+radius*2),fill=(255,184,95,100))
    glow=glow.filter(ImageFilter.GaussianBlur(w*.045));sky=Image.alpha_composite(sky.convert('RGBA'),glow)
    ImageDraw.Draw(sky).ellipse((cx-radius,cy-radius,cx+radius,cy+radius),fill=(255,217,157,255))
    return sky.convert('RGB')


class World:
    def __init__(self,camera,target,w,h):
        self.camera=camera;self.forward=unit(sub(target,camera))
        self.right=unit(cross(self.forward,(0,1,0)));self.up=cross(self.right,self.forward)
        self.w,self.h=w,h;self.faces=[]
    def point(self,p):
        v=sub(p,self.camera);depth=dot(v,self.forward)
        if depth<.3:return None
        return (self.w*.5+dot(v,self.right)/depth*self.w*.87,
                self.h*.52-dot(v,self.up)/depth*self.w*.87,depth)
    def face(self,points,base,shade=True):
        # Clip large floor/water polygons against the near plane before projecting.
        original = points
        clipped = []
        for a,b in zip(points,points[1:]+points[:1]):
            da=dot(sub(a,self.camera),self.forward);db=dot(sub(b,self.camera),self.forward)
            inside_a,inside_b=da>=.31,db>=.31
            if inside_a:clipped.append(a)
            if inside_a != inside_b:
                ratio=(.31-da)/(db-da)
                clipped.append(tuple(a[k]+ratio*(b[k]-a[k]) for k in range(3)))
        if len(clipped)<3:return
        projected=[self.point(p) for p in clipped]
        points=original
        if shade:
            normal=unit(cross(sub(points[1],points[0]),sub(points[2],points[0])))
            light=.58+.4*abs(dot(normal,unit((-.6,1,-.5))))
        else:light=1
        self.faces.append((sum(p[2] for p in projected)/len(projected),[(p[0],p[1]) for p in projected],color(base,light)))
    def box(self,x,y,z,w,h,d,c):
        a=(x,y,z);b=(x+w,y,z);e=(x,y,z+d);f=(x+w,y,z+d)
        A=(x,y+h,z);B=(x+w,y+h,z);E=(x,y+h,z+d);F=(x+w,y+h,z+d)
        for points in ((a,b,B,A),(b,f,F,B),(f,e,E,F),(e,a,A,E),(A,B,F,E)):
            self.face(points,c)
    def rod(self,a,b,r,c):
        axis=unit(sub(b,a));right=unit(cross(axis,(0,1,0) if abs(axis[1])<.9 else (1,0,0)))
        up=cross(axis,right);rings=[]
        for center in (a,b):
            rings.append([tuple(center[k]+r*(right[k]*math.cos(i*math.pi/3)+up[k]*math.sin(i*math.pi/3)) for k in range(3)) for i in range(6)])
        for i in range(6):self.face([rings[0][i],rings[0][(i+1)%6],rings[1][(i+1)%6],rings[1][i]],c)
        self.face(rings[1],c)
    def shadow(self,x,z,rx,rz):
        self.face([(x+math.cos(i*math.pi/12)*rx,.012,z+math.sin(i*math.pi/12)*rz) for i in range(24)],(94,71,48),False)
    def pyramid(self,x,z,size=10,height=12):
        # Distinct stepped stone courses, not a claim of archaeological accuracy.
        rows=19
        for row in range(rows):
            low=size*(1-row/rows);high=size*(1-(row+1)/rows)
            y=row/rows*height;top=(row+1)/rows*height
            count=max(1,int(low/1.2));width=low*2/count
            for side in range(4):
                for j in range(count):
                    left=-low+j*width+.018;right=left+width-.035
                    tone=1+math.sin(row*12.13+j*4.7+side)*.065
                    base=color((217,183,126),tone)
                    if side==0:pts=[(x+left,y,z-low),(x+right,y,z-low),(x+right,top,z-low),(x+left,top,z-low)]
                    elif side==1:pts=[(x+low,y,z+left),(x+low,y,z+right),(x+low,top,z+right),(x+low,top,z+left)]
                    elif side==2:pts=[(x+left,y,z+low),(x+right,y,z+low),(x+right,top,z+low),(x+left,top,z+low)]
                    else:pts=[(x-low,y,z+left),(x-low,y,z+right),(x-low,top,z+right),(x-low,top,z+left)]
                    self.face(pts,base)
            self.face([(x-low,top,z-low),(x+low,top,z-low),(x+low,top,z+low),(x-low,top,z+low)],(224,193,140))
    def worker(self,x,z,t,scale=1,lean=0,base=0):
        skin=(133,86,58);cloth=(224,210,169)
        def p(dx,y,dz):return (x+dx*scale,y*scale+base,z+dz*scale)
        if base==0:self.shadow(x,z,.32*scale,.55*scale)
        self.rod(p(0,.8,0),p(lean,1.35,0),.15*scale,skin)
        self.box(x-.2*scale,.63*scale+base,z-.16*scale,.4*scale,.3*scale,.32*scale,cloth)
        self.box(x+(lean-.12)*scale,1.39*scale+base,z-.12*scale,.24*scale,.29*scale,.24*scale,skin)
        self.box(x+(lean-.14)*scale,1.6*scale+base,z-.14*scale,.28*scale,.1*scale,.28*scale,cloth)
        step=math.sin(t*6)*.23
        for side in (-1,1):
            self.rod(p(side*.12,.7,0),p(side*.15,.34,step*side),.072*scale,skin)
            self.rod(p(side*.15,.34,step*side),p(side*.15,.06,step*side*.6),.065*scale,skin)
            self.rod(p(lean,1.25,side*.18),p(lean-.42,1,side*.2),.065*scale,skin)
    def palm(self,x,z,height=5):
        self.rod((x,0,z),(x+.3,height,z),.17,(94,74,47))
        for i in range(9):
            a=i*math.pi*2/9
            end=(x+math.cos(a)*2.4,height-.7,z+math.sin(a)*2.4)
            mid=(x+math.cos(a)*1.1,height+.5,z+math.sin(a)*1.1)
            self.face([(x,height,z),(mid[0]+.3,mid[1],mid[2]),end,(mid[0]-.3,mid[1],mid[2])],(74,93,55))
    def paint(self,image):
        d=ImageDraw.Draw(image)
        for _,points,c in sorted(self.faces,key=lambda f:f[0],reverse=True):d.polygon(points,fill=c)


def frame(progress,w=960,h=540):
    from .local_animation import font
    p=max(0,min(.999999,progress));shot=int(p*3);u=(p*3)%1;t=progress*12
    if shot==0:camera=(25-u*5,13-u*2,-24+u*5);target=(0,4,12)
    elif shot==1:camera=(6-u*1.5,2.6,-11+u*1.4);target=(-1,1.05,0)
    else:camera=(11-u*3,5.7,-12+u*2);target=(0,1.3,5)
    image=background(w,h).copy();world=World(camera,target,w,h)
    if shot<2:
        world.face([(-100,-.03,-100),(100,-.03,-100),(100,-.03,150),(-100,-.03,150)],(178,142,88),False)
        world.pyramid(0,17,10,12)
        # Low ruins and irregular stones give foreground parallax and human scale.
        for i in range(14):
            x=-15+(i*7.1)%29;z=-5+(i*3.3)%13
            if -8<x<5 and -3<z<3:continue
            world.box(x,0,z,1.2,.35+(i%3)*.2,.8,(165,130,83))
        if shot==0:
            for i in range(10):world.worker(-8+i*1.4,1+math.sin(i)*1.7,t+i,.9)
            world.box(-2,0,-1,2.6,1.8,2,(207,171,113))
            title='HỌ ĐÃ LÀM ĐIỀU ĐÓ THẾ NÀO?'
        else:
            bx=2-u*1.5
            world.shadow(bx+1,0,3,2)
            world.box(bx-.3,.04,-1.35,3.3,.15,2.7,(96,64,39))
            world.box(bx,.19,-1,2.65,2.05,2,(218,184,127))
            for j in range(4):
                x=-1.4-j*1.35-u*.25;z=-.7+(j%2)*1.4
                world.worker(x,z,t+j,1,-.22)
                world.rod((x-.5,1,z),(bx,.6,z),.025,(97,69,41))
            for j in range(3):
                cx=-3+j*1.9;cz=4.5+math.sin(t*.8+j)*.25
                world.worker(cx,cz,t+j,.9)
                world.box(cx-.28,1.2*.9,cz-.24,.56,.45,.48,(207,177,128))
            title='TỪNG KHỐI ĐÁ. TỪNG BƯỚC MỘT.'
    else:
        world.face([(-19,-.1,-100),(19,-.1,-100),(19,-.1,160),(-19,-.1,160)],(42,83,91),False)
        for side in (-1,1):
            x=side*19
            world.face([(x,.02,-100),(x+side*80,.02,-100),(x+side*80,.02,160),(x,.02,160)],(162,133,83),False)
            for j in range(3):world.palm(x+side*(j%2)*1.5,12+j*13,4+j*.8)
        for i in range(90):
            x=-15+(i*3.7)%30;z=-8+(i*1.71+t*.5)%55
            world.face([(x,-.04,z),(x+1.1,-.04,z+.12),(x+.8,-.04,z+.2)],(78+int(9*math.sin(i+t)),115,115),False)
        bx=-2+u*4;bz=4
        world.face([(bx-1.3,.4,bz-3.5),(bx+1.3,.4,bz-3.5),(bx+1.5,.5,bz+2.6),(bx,1,bz+4),(bx-1.5,.5,bz+2.6)],(120,77,43))
        world.face([(bx-1.3,.4,bz-3.5),(bx-1.5,.5,bz+2.6),(bx,1,bz+4),(bx-.6,.05,bz+1)],(80,53,34))
        world.face([(bx+1.3,.4,bz-3.5),(bx+1.5,.5,bz+2.6),(bx,1,bz+4),(bx+.6,.04,bz+1)],(103,66,37))
        for j in range(4):world.box(bx-.85+(j%2)*.9,.55,bz-1.5+(j//2)*1.4,.8,.85,1.2,(216,195,151))
        world.worker(bx,bz-2.5,t,.8,base=.55)
        world.worker(bx+.65,bz+2.2,t+1,.75,base=.6)
        # A small landing on the near bank: people carrying blocks toward the boat.
        world.box(-18,.03,7,6,.38,3.2,(134,101,64))
        for j in range(3):
            cx=-16+(j%2)*1.1;cz=7+j*.9-u*.5
            world.worker(cx,cz,t+j,.95,base=.42)
            world.box(cx-.28,1.58,cz-.24,.56,.45,.48,(218,191,143))

        for side in (-1,1):
            world.rod((bx+side*.8,.8,bz-2),(bx+side*(3+.3*math.sin(t*3)),-.03,bz-1),.055,(123,82,44))
        title='CẢ MỘT HỆ THỐNG PHÍA SAU KỲ QUAN.'
    world.paint(image)
    # Small drifting dust in desert scenes. Seeded math keeps rerenders deterministic.
    if shot<2:
        dust=Image.new('RGBA',(w,h));d=ImageDraw.Draw(dust)
        for i in range(45):
            x=((i*.618+t*.013)%1)*w;y=((i*.137+t*.008)%1)*h
            radius=1+(i%3)
            d.ellipse((x,y,x+radius,y+radius),fill=(255,215,151,30))
        image=Image.alpha_composite(image.convert('RGBA'),dust).convert('RGB')
    # A soft lower gradient gives text contrast without a giant opaque card.
    overlay=Image.new('RGBA',(w,h));d=ImageDraw.Draw(overlay)
    for y in range(int(h*.68),h):
        d.line((0,y,w,y),fill=(12,17,20,int((y/h-.68)/.32*185)))
    image=Image.alpha_composite(image.convert('RGBA'),overlay).convert('RGB');d=ImageDraw.Draw(image)
    d.text((int(w*.045),int(h*.875)),title,font=font(max(10,int(w*.023)),True),fill='#f6e6c7')
    d.text((int(w*.045),int(h*.94)),'TÁI DỰNG MINH HỌA · DỰNG CỤC BỘ',font=font(max(8,int(w*.011))),fill='#c1b6a2')
    return image


def add_sound(video, duration):
    """Quiet generated wind, work and water textures; no downloaded/licensed audio."""
    import array
    import random
    import subprocess
    import tempfile
    import wave
    from pathlib import Path
    video=Path(video);rng=random.Random(41);rate=24000;low=0;samples=array.array('h')
    for i in range(int(duration*rate)):
        t=i/rate;phase=t/max(duration,.001);noise=rng.uniform(-1,1)
        low=.97*low+.03*noise
        wind=low*.20
        if 1/3<=phase<2/3:
            beat=(t*1.8)%1
            value=wind+math.exp(-beat*23)*math.sin(t*math.tau*74)*.10+noise*.014
        elif phase>=2/3:
            value=wind+low*.25+math.sin(t*math.tau*130)*(.006+.006*math.sin(t*4))
        else:value=wind
        fade=min(1,t/.4,(duration-t)/.6)
        samples.append(int(max(-.7,min(.7,value))*max(0,fade)*32767))
    with tempfile.TemporaryDirectory() as directory:
        audio=Path(directory)/'ambience.wav'
        with wave.open(str(audio),'wb') as stream:
            stream.setnchannels(1);stream.setsampwidth(2);stream.setframerate(rate);stream.writeframes(samples.tobytes())
        muxed=video.with_name(video.stem+'.sound.mp4')
        try:
            subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(video),'-i',str(audio),
                            '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','96k',
                            '-t',str(duration),'-movflags','+faststart',str(muxed)],check=True)
            muxed.replace(video)
        finally:
            muxed.unlink(missing_ok=True)
