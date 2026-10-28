import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pipeline import local_animation as animation, s4_prompts, s5_generate, s6_collect, s7_render
from pipeline.common import audio_duration


class LocalAnimationTests(unittest.TestCase):
    def test_all_local_scenes_skip_llm_and_browser(self):
        p=SimpleNamespace(load_scenes=lambda:[{'id':1,'animation':{'preset':'stone_transport'}}])
        with patch.object(s4_prompts.llm,'complete',side_effect=AssertionError('No LLM')), \
             patch.object(s5_generate,'connect',side_effect=AssertionError('No browser')), \
             patch.object(s6_collect,'connect',side_effect=AssertionError('No browser')):
            s4_prompts.run(p);s5_generate.run(p);s6_collect.run(p)

    def test_generation_preserves_local_scenes_in_mixed_project(self):
        scenes=[{'id':1,'animation':{'preset':'stone_transport'}},{'id':2,'image_prompt':'A pyramid'}]
        p=SimpleNamespace(load_scenes=lambda:scenes,save_scenes=Mock(),settings={'flow':{
            'retries':0,'submit_timeout':1,'pick':'first','delay_seconds':[0,0]}})
        bridge=SimpleNamespace(call=lambda *a,**kw:{'tiles':['new-image']})
        with patch.object(s5_generate,'connect',return_value=bridge):
            s5_generate.run(p)
        saved=p.save_scenes.call_args.args[0]
        self.assertEqual(len(saved),2)
        self.assertEqual(saved[0]['animation']['preset'],'stone_transport')
        self.assertEqual(saved[1]['tile_key'],'new-image')

    def test_bad_preset_rejected_and_frames_change(self):
        with self.assertRaises(ValueError):
            animation.is_local_scene({'animation':{'preset':'unknown'}})
        first=animation.frame('stone_transport',0,320,180)
        last=animation.frame('stone_transport',1,320,180)
        self.assertNotEqual(first.tobytes(),last.tobytes())

    def test_branding_is_removed_from_public_content(self):
        from pipeline.branding import contains_brand,remove_branded_sentences
        original='Một câu chuyện lịch sử.\n\nĐăng ký kênh Dấu Vết Văn Minh nhé.\n\nHẹn gặp lại bạn.'
        clean=remove_branded_sentences(original)
        self.assertFalse(contains_brand(clean))
        self.assertIn('Một câu chuyện lịch sử.',clean)
        self.assertIn('Hẹn gặp lại bạn.',clean)
        self.assertTrue(contains_brand('@LsDauVetVanMinh'))

    def test_cinematic_shots_and_local_sound_export(self):
        images=[animation.frame('giza_cinematic',p,320,180) for p in (.12,.5,.85)]
        self.assertEqual(len({image.tobytes() for image in images}),3)
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'cinematic.mp4'
            animation.render('giza_cinematic',output,1,width=320,height=180,fps=9)
            from pipeline.local_cinematic import add_sound
            add_sound(output,1)
            streams=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(output)]))['streams']
            self.assertEqual({s['codec_type'] for s in streams},{'video','audio'})
            subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(output),'-f','null','-'],check=True)

    def test_real_local_animation_renders_with_audio_and_subtitles_without_images(self):
        with tempfile.TemporaryDirectory() as directory:
            d=Path(directory)
            voice=d/'voice.wav'
            subprocess.run(['ffmpeg','-y','-loglevel','error','-f','lavfi','-i','sine=frequency=440:duration=1.5',str(voice)],check=True)
            scenes=[{'id':1,'text':'Minh họa việc vận chuyển đá.','start':0,'end':1.5,
                     'animation':{'preset':'stone_transport'}}]
            p=SimpleNamespace(dir=d,voice=voice,final=d/'final.mp4',srt=d/'subtitles.srt',
                              image_path=lambda _:None,load_scenes=lambda:scenes,
                              settings={'render':{'width':320,'height':180,'fps':12,'ken_burns':True,'burn_subtitles':True}})
            s7_render.run(p)
            self.assertGreater(p.final.stat().st_size,1000)
            self.assertAlmostEqual(audio_duration(p.final),1.5,delta=.15)
            streams=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(p.final)]))['streams']
            self.assertEqual({s['codec_type'] for s in streams},{'video','audio'})
            self.assertIn('vận chuyển',p.srt.read_text())
            # Mixed clips must also concatenate and decode correctly.
            from PIL import Image
            still=d/'still.png';Image.new('RGB',(320,180),(20,80,140)).save(still)
            scenes[0]['end']=.75
            scenes.append({'id':2,'text':'Tiếp tục câu chuyện.','start':.75,'end':1.5})
            p.image_path=lambda scene: still if scene['id']==2 else None
            s7_render.run(p,force=True)
            self.assertAlmostEqual(audio_duration(p.final),1.5,delta=.15)
            subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(p.final),'-f','null','-'],check=True)


if __name__=='__main__':
    unittest.main()
