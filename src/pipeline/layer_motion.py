"""Deterministic cutout/rig motion. Plans animate objects, not the whole camera.

Prototype renders do not certify voice synchronization. Production adapters bind
plans to exact narration, voice and scene hashes before rendering any frames.
"""
import hashlib
import json
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def local_path(root, relative):
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError('Motion asset/plan must be an existing file inside this episode.')
    return path


def scene_hash(scene):
    return hashlib.sha256(json.dumps({k: scene[k] for k in ('id', 'text', 'start', 'end')},
                                    sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def validate(plan):
    def number(v):
        return type(v) in (int, float) and math.isfinite(v)
    def check_props(props):
        if not isinstance(props, dict):
            raise ValueError('Motion props must be an object.')
        allowed = ('x', 'y', 'width', 'height', 'scale', 'font_size', 'opacity',
                   'left_arm', 'right_arm', 'look', 'blink', 'mouth', 'brow', 'text', 'color')
        for name, value in props.items():
            if name not in allowed:
                raise ValueError('Unknown motion property.')
            if name in ('text', 'color'):
                if not isinstance(value, str):
                    raise ValueError('Text/color must be strings.')
            elif not number(value):
                raise ValueError('Motion numeric properties must be finite.')
            if name == 'opacity' and not 0 <= value <= 1:
                raise ValueError('Opacity must be between 0 and 1.')
            if name in ('width', 'height', 'scale', 'font_size') and value <= 0:
                raise ValueError('Size/scale must be positive.')
    duration = plan.get('duration')
    if not number(duration) or not 0 < duration <= 3600:
        raise ValueError('Motion duration must be finite and positive.')
    layers = plan.get('layers')
    if not isinstance(layers, list) or not 1 <= len(layers) <= 256:
        raise ValueError('Motion requires 1–256 layers.')
    ids = set()
    for layer in layers:
        if not layer.get('id') or layer['id'] in ids:
            raise ValueError('Motion layer IDs must be unique.')
        ids.add(layer['id'])
        if layer.get('kind') not in ('image', 'text', 'stick_character'):
            raise ValueError('Unknown motion layer kind.')
        check_props(layer.get('props', {}))
        keys = layer.get('keyframes', [])
        previous = -1
        if not keys:
            raise ValueError('Every layer requires keyframes.')
        for key in keys:
            at = key.get('at')
            if not number(at) or not 0 <= at <= duration or at <= previous:
                raise ValueError('Keyframe times must be ordered, unique and inside the scene.')
            previous = at
            if key.get('ease', 'smooth') not in ('smooth', 'linear', 'hold'):
                raise ValueError('Unknown easing.')
            check_props(key.get('props'))
    return plan


def properties(layer, t):
    """Each property has its own track; omitted properties keep their last value."""
    out = dict(layer.get('props', {}))
    names = {name for key in layer['keyframes'] for name in key['props']}
    for name in names:
        track = [(key['at'], key['props'][name], key.get('ease', 'smooth'))
                 for key in layer['keyframes'] if name in key['props']]
        if t < track[0][0]:
            out[name] = out.get(name, track[0][1])
            continue
        out[name] = track[-1][1]
        for (a, av, ease), (b, bv, _) in zip(track, track[1:]):
            if a <= t < b:
                u = (t-a)/(b-a)
                if ease == 'hold' or not isinstance(av, (int, float)) or not isinstance(bv, (int, float)):
                    out[name] = av
                else:
                    if ease == 'smooth':
                        u = u*u*(3-2*u)
                    out[name] = av + (bv-av)*u
                break
    return out


def character(props):
    """Original stick-orange rig; mouth is expression control, not lip sync."""
    im = Image.new('RGBA', (320, 470))
    d = ImageDraw.Draw(im)
    ink = '#35312d'
    d.line([(137, 325), (115, 436), (87, 443)], fill=ink, width=8)
    d.line([(182, 325), (204, 436), (234, 443)], fill=ink, width=8)
    d.ellipse((108, 215, 212, 341), fill='#b96d3b', outline=ink, width=5)
    d.rectangle((179, 241, 193, 255), fill='#dc7565')
    for x, angle in ((111, props.get('left_arm', 140)), (209, props.get('right_arm', 40))):
        radians = math.radians(angle)
        hand = (x+84*math.cos(radians), 245+84*math.sin(radians))
        d.line([(x, 245), hand], fill=ink, width=7)
        d.ellipse((hand[0]-5, hand[1]-5, hand[0]+5, hand[1]+5), fill=ink)
    d.ellipse((64, 33, 256, 220), fill='#fff9ed', outline=ink, width=6)
    look = max(-12, min(12, props.get('look', 0)))
    blink = max(0, min(1, props.get('blink', 0)))
    for x in (124+look, 196+look):
        if blink > .8:
            d.line((x-8, 122, x+8, 122), fill=ink, width=5)
        else:
            d.ellipse((x-8, 110, x+8, 130), fill=ink)
    opening = max(0, min(1, props.get('mouth', 0)))
    if opening > .15:
        d.ellipse((145, 159, 175, 167+opening*32), fill=ink)
    else:
        d.arc((129, 141, 191, 183), 15, 165, fill=ink, width=5)
    brow = props.get('brow', 0)
    d.line((108, 96+brow, 139, 94-brow), fill=ink, width=4)
    d.line((181, 94-brow, 212, 96+brow), fill=ink, width=4)
    return im


class Painter:
    def __init__(self, plan, root, width, height):
        self.plan = validate(plan)
        self.root, self.width, self.height = Path(root), width, height
        self.canvas_width = plan.get('canvas_width', width)
        self.canvas_height = plan.get('canvas_height', height)
        if (type(self.canvas_width) is not int or type(self.canvas_height) is not int
                or not 64 <= self.canvas_width <= 3840 or not 64 <= self.canvas_height <= 2160
                or abs(self.canvas_width/self.canvas_height-width/height) > .001):
            raise ValueError('Motion design canvas must match output aspect ratio.')
        self.images, self.fonts = {}, {}
        for layer in plan['layers']:
            if layer['kind'] == 'image':
                path = local_path(root, layer['asset'])
                with Image.open(path) as im:
                    self.images[layer['id']] = im.convert('RGBA')

    def frame(self, t):
        scene = Image.new('RGBA', (self.canvas_width, self.canvas_height), self.plan.get('background', '#f8f1e3'))
        for layer in self.plan['layers']:
            p = properties(layer, t)
            opacity = p.get('opacity', 1)
            if opacity <= 0:
                continue
            if layer['kind'] == 'image':
                sprite = self.images[layer['id']].copy()
            elif layer['kind'] == 'stick_character':
                sprite = character(p)
            else:
                size = max(8, min(240, int(p.get('font_size', 40))))
                font_path = layer.get('font', 'system:arial')
                if font_path == 'system:arial':
                    font_path = 'arial.ttf'
                else:
                    font_path = str(local_path(self.root, font_path))
                key = (str(font_path), size)
                if key not in self.fonts:
                    try:
                        self.fonts[key] = ImageFont.truetype(str(font_path), size)
                    except OSError:
                        if font_path != 'arial.ttf':
                            raise
                        self.fonts[key] = ImageFont.truetype('DejaVuSans.ttf', size)
                font = self.fonts[key]
                text = p.get('text', layer.get('text', ''))
                bbox = font.getbbox(text)
                sprite = Image.new('RGBA', (max(1, bbox[2]-bbox[0]+8), max(1, bbox[3]-bbox[1]+8)))
                ImageDraw.Draw(sprite).text((4-bbox[0], 4-bbox[1]), text, font=font, fill=p.get('color', '#35312d'))
            scale = p.get('scale', 1)
            w = max(1, int(p.get('width', sprite.width)*scale))
            h = max(1, int(p.get('height', sprite.height)*scale))
            sprite = sprite.resize((w, h), Image.Resampling.LANCZOS)
            if opacity < 1:
                sprite.putalpha(sprite.getchannel('A').point(lambda alpha: int(alpha*opacity)))
            scene.alpha_composite(sprite, (round(p.get('x', 0)), round(p.get('y', 0))))
        if scene.size != (self.width, self.height):
            scene = scene.resize((self.width, self.height), Image.Resampling.LANCZOS)
        return scene.convert('RGB')


def render_plan(plan, root, output, width=1280, height=720, fps=30, frames=None):
    """Render a silent clip; callers must supply/bind any narration separately."""
    if type(fps) is not int or not 1 <= fps <= 60 or not 64 <= width <= 3840 or not 64 <= height <= 2160:
        raise ValueError('Invalid output format.')
    painter = Painter(plan, root, width, height)
    frames = frames if frames is not None else math.ceil(plan['duration']*fps)
    if abs(frames/fps-plan['duration']) > 1/fps+.000001:
        raise ValueError('Frame duration differs from motion plan.')
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_name(output.stem+'.rendering.mp4')
    process = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                                '-s', f'{width}x{height}', '-r', str(fps), '-i', '-', '-an',
                                '-c:v', 'libx264', '-preset', 'fast', '-crf', '20', '-pix_fmt', 'yuv420p',
                                '-movflags', '+faststart', str(temp)], stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for i in range(frames):
            process.stdin.write(painter.frame(i/fps).tobytes())
        process.stdin.close()
        error = process.stderr.read().decode(errors='replace')
        if process.wait() != 0:
            raise RuntimeError('Motion FFmpeg failed: '+error[-1000:])
        temp.replace(output)
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()
        process.stderr.close()
        if temp.exists():
            temp.unlink()


def render_scene(project, scene, output, width, height, fps, frames):
    path = local_path(project.dir, scene['motion_plan'])
    plan = json.loads(path.read_text(encoding='utf-8'))
    expected = {'script_sha256': sha(project.script), 'voice_sha256': sha(project.voice),
                'scene_sha256': scene_hash(scene)}
    if plan.get('sources') != expected or plan.get('scene_id') != scene['id']:
        raise ValueError('Motion plan has missing/stale script, voice or scene provenance.')
    if abs(plan['duration']-(scene['end']-scene['start'])) > 1/fps+.000001:
        raise ValueError('Motion plan does not cover scene duration.')
    render_plan(plan, project.dir, output, width, height, fps, frames)
