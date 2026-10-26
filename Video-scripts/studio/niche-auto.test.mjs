import test from 'node:test';
import assert from 'node:assert/strict';
import { runNicheAuto } from './public/niche-auto.mjs';

const base = () => ({ id: 's1', market: 'US', language: 'en', format: 'long', nicheMode: 'live', probeMode: 'live', leadChannel: '@ref', angle: '', nicheFlow: {} });

function fakeAct(survey, calls, { probePassed = true, sameTemplate = 1, groupsPassed = true, angle = 'Góc kể đã chọn' } = {}) {
  return async (stage, extras = {}) => {
    calls.push({ stage, extras });
    const flow = survey.nicheFlow ||= {};
    if (stage === 'field') { flow.field = { passed: true }; return flow.field; }
    if (stage === 'template') { 
      const tplAngle = extras.angle || angle; 
      flow.template = { passed: true, value: 'the entire history of', angle: tplAngle }; 
      if (tplAngle) survey.angle ||= tplAngle; 
      return flow.template; 
    }
    if (stage === 'shelf') {
      if (extras.override === true) { flow.shelf = { ...flow.shelf, passed: true, overridden: true }; return flow.shelf; }
      flow.shelf = { passed: false, count: sameTemplate, channels: Array.from({ length: sameTemplate }, (_, i) => ({ channelId: 'c' + i, sameTemplate: true })), videos: [] };
      return flow.shelf;
    }
    if (stage === 'groups') {
      if (extras.groupId) { flow.groups = { ...flow.groups, chosen: extras.groupId }; return flow.groups; }
      if (!groupsPassed) { flow.groups = { passed: false, count: 3, groups: [] }; return flow.groups; }
      flow.groups = { passed: true, count: 5, chosen: null, suggestedGroup: 'group-1', suggestedQueries: ['q1', 'q2', 'q3'], groups: [{ id: 'group-0' }, { id: 'group-1' }] };
      return flow.groups;
    }
    if (stage === 'probe') { flow.probe = { passed: probePassed, medianHits: probePassed ? 14 : 6 }; return flow.probe; }
    if (stage === 'topics') { flow.topics = { passed: true, chosen: Array.from({ length: 20 }, (_, i) => 'topic ' + i) }; return flow.topics; }
    throw Error('unexpected stage ' + stage);
  };
}

test('auto runs the whole niche flow from channel to 20 topics without extra clicks', async () => {
  const calls = [], s = base();
  await runNicheAuto({ getSurvey: () => s, act: fakeAct(s, calls), save: async () => {} });
  assert.deepEqual(calls.map(c => c.stage), ['field', 'template', 'shelf', 'shelf', 'groups', 'groups', 'probe', 'topics']);
  assert.equal(calls[3].extras.override, true, 'kho chưa đủ 3 kênh thì tự ghi nhận ngoại lệ');
  assert.deepEqual(calls[5].extras, { groupId: 'group-1' }, 'tự chọn nhóm tốt nhất');
  assert.equal(calls[6].extras.mode, 'live');
  assert.deepEqual(calls[6].extras.queries, ['q1', 'q2', 'q3'], 'tự gõ thử bằng câu gợi ý');
  assert.equal(s.nicheFlow.topics.chosen.length, 20);
});

test('auto resumes at the first unfinished stage and does not redo passed work', async () => {
  const calls = [], s = base();
  s.nicheFlow = {
    field: { passed: true },
    template: { passed: true, value: 'the entire history of', angle: 'A' },
    shelf: { passed: true, overridden: true },
    groups: { passed: true, chosen: 'group-0', suggestedGroup: 'group-0', suggestedQueries: ['q'], groups: [{ id: 'group-0' }] },
  };
  await runNicheAuto({ getSurvey: () => s, act: fakeAct(s, calls), save: async () => {} });
  assert.deepEqual(calls.map(c => c.stage), ['probe', 'topics'], 'chỉ chạy phần còn thiếu');
});

test('auto falls back to a default angle when the template stage has no suggestion', async () => {
  const calls = [], s = base();
  let saved = false;
  await runNicheAuto({ getSurvey: () => s, act: fakeAct(s, calls, { angle: '' }), save: async () => { saved = true; } });
  assert.ok(s.angle.trim(), 'phải có góc kể để kho và chủ đề chạy được');
  // Giờ góc kể được gửi qua template action (không gọi save cục bộ riêng).
  // Kiểm tra là template được gọi 2 lần: lần 1 có angle mặc định, lần 2 không cần.
  assert.ok(calls.some(c => c.stage === 'template' && c.extras.angle && c.extras.angle !== ''), 'template action phải nhận angle mặc định');
  assert.equal(calls.filter(c => c.stage === 'probe').length, 1);
});

test('auto stops with an actionable error when the shelf has no same-template channel', async () => {
  const calls = [], s = base();
  await assert.rejects(runNicheAuto({ getSurvey: () => s, act: fakeAct(s, calls, { sameTemplate: 0 }), save: async () => {} }), /chưa có kênh nào cùng khuôn/);
  assert.ok(!calls.some(c => c.stage === 'groups'), 'không được chạy tiếp khi kho không có kênh cùng khuôn');
});

test('auto stops at group failure and at a failed probe without calling topics', async () => {
  const groupCalls = [], gs = base();
  await assert.rejects(runNicheAuto({ getSurvey: () => gs, act: fakeAct(gs, groupCalls, { groupsPassed: false }), save: async () => {} }), /4–7 nhóm/);
  assert.ok(!groupCalls.some(c => c.stage === 'probe'));

  const probeCalls = [], ps = base();
  await assert.rejects(runNicheAuto({ getSurvey: () => ps, act: fakeAct(ps, probeCalls, { probePassed: false }), save: async () => {} }), /Nhu cầu chưa đạt/);
  assert.ok(!probeCalls.some(c => c.stage === 'topics'));
});
