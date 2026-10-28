import sys
import unittest
from pathlib import Path
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pipeline.source_animation import render_frame,material,CAPTIONS
from pipeline.branding import contains_brand


class SourceAnimationTests(unittest.TestCase):
    def test_three_phases_and_source_assets_are_preserved(self):
        assets=[Image.new('RGB',(720,345),color) for color in ('#9d7044','#b88054','#b19b78')]
        before=[im.tobytes() for im in assets]
        frames=[render_frame(t,assets,material(),material(27,True)) for t in (2,9,14)]
        self.assertTrue(all(im.size==(720,1280) and im.mode=='RGB' for im in frames))
        self.assertEqual(len(set(im.tobytes() for im in frames)),3)
        self.assertEqual(before,[im.tobytes() for im in assets])
        self.assertFalse(any(contains_brand(caption) for caption in CAPTIONS))

    def test_action_changes_within_same_scene(self):
        assets=[Image.new('RGB',(720,345),'#9d7044') for _ in range(3)]
        clay,inner=material(),material(27,True)
        first=render_frame(7,assets,clay,inner)
        second=render_frame(10,assets,clay,inner)
        self.assertNotEqual(first.crop((70,660,650,1020)).tobytes(),second.crop((70,660,650,1020)).tobytes())


if __name__=='__main__':unittest.main()
