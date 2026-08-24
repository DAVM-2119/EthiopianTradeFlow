import assert from 'assert';
import { offlineQueue, generateUUID } from '../storage/offlineQueue.js';

async function runTests() {
  console.log('--- Running Mobile Offline Queue Engine Tests ---');

  // Test UUID Generator
  const uuid1 = generateUUID();
  const uuid2 = generateUUID();
  assert.notStrictEqual(uuid1, uuid2, 'UUIDs must be unique');
  assert.strictEqual(uuid1.length, 36, 'UUID must be 36 characters long');
  console.log('✓ UUID generation test passed.');

  // Test Enqueue
  await offlineQueue.clearQueue();
  const countInitial = await offlineQueue.count();
  assert.strictEqual(countInitial, 0, 'Queue should start empty');

  const event1 = await offlineQueue.enqueueEvent({
    eventType: 'TRACKING_EVENT',
    entityId: '123e4567-e89b-12d3-a456-426614174000',
    payload: { latitude: 11.589, longitude: 43.145, speed: 65 },
  });

  assert.ok(event1.client_event_id, 'Enqueued event must have client_event_id');
  assert.strictEqual(event1.event_type, 'TRACKING_EVENT');

  const countAfterOne = await offlineQueue.count();
  assert.strictEqual(countAfterOne, 1, 'Queue count should be 1 after enqueue');
  console.log('✓ Event enqueuing test passed.');

  // Test Batch Removal
  await offlineQueue.removeEvents([event1.client_event_id]);
  const countAfterRemoval = await offlineQueue.count();
  assert.strictEqual(countAfterRemoval, 0, 'Queue count should be 0 after removal');
  console.log('✓ Event queue removal test passed.');

  console.log('=== ALL MOBILE QUEUE ENGINE TESTS PASSED CLEANLY! ===');
}

runTests().catch((err) => {
  console.error('❌ Mobile Offline Queue Test Failed:', err);
  process.exit(1);
});
