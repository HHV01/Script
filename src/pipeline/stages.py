"""Ordered stages shared by CLI and production worker."""
STAGES = {
    'script': 's1_script', 'review': 'script_review', 'voice': 's2_voice',
    'scenes': 's3_scenes', 'prompts': 's4_prompts', 'generate': 's5_generate',
    'collect': 's6_collect', 'render': 's7_render', 'publish': 's8_publish',
    'qc': 'qc',
}
