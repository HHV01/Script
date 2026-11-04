import unittest,io,contextlib,sys,json
suite=unittest.TestSuite()
for pattern in ['test_layer_motion.py','test_script_review.py','test_vieneu.py','test_timeline_review.py','test_core.py','test_scene_handoff.py']:
 suite.addTests(unittest.defaultTestLoader.discover('tests',pattern=pattern))
with contextlib.redirect_stdout(io.StringIO()): result=unittest.TextTestRunner(verbosity=1).run(suite)
print(json.dumps({'run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped)}))
sys.exit(not result.wasSuccessful())
