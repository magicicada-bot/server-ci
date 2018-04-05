# Copyright 2008-2015 Canonical
# Copyright 2015-2018 Chicharreros (https://launchpad.net/~chicharreros)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# For further info, check  http://launchpad.net/magicicada-server

"""Test interserver notification bus."""

import logging
import uuid

from mocker import Mocker, expect
from twisted.internet.defer import inlineCallbacks, succeed
from twisted.internet import defer, reactor
from twisted.python.failure import Failure
from twisted.trial.unittest import TestCase as TwistedTestCase
from ubuntuone.storageprotocol import protocol_pb2, request

from magicicada.filesync.models import Share
from magicicada.filesync.notifier import notifier
from magicicada.filesync.notifier.notifier import (
    ShareAccepted,
    ShareCreated,
    ShareDeclined,
    ShareDeleted,
    UDFCreate,
    UDFDelete,
    VolumeNewGeneration,
)
from magicicada.filesync.notifier.tests.test_notifier import FakeNotifier
from magicicada.server.server import (
    StorageServer,
    StorageServerFactory,
    logger,
)
from magicicada.server.testing.testcase import FactoryHelper, TestWithDatabase


class DummyReactor(object):
    """Very simplistic "reactor"."""

    def callInThread(self, func, *args):
        """Calls func immediately."""
        func(*args)

    def callFromThread(self, func, *args):
        """Calls func immediately."""
        func(*args)


class TestDelivery(TwistedTestCase):
    """More delivery testing."""
    @inlineCallbacks
    def setUp(self):
        """Set up test."""
        yield super(TestDelivery, self).setUp()
        self.mocker = Mocker()
        self.fake_reactor = DummyReactor()
        self.content = self.mocker.mock()
        self.node_owner_id = 1
        self.node_uuid = uuid.uuid4()
        self.node_hash = "hash:blah"
        self.owner_id = 0
        self.free_bytes = 0
        self.node_volume_id = uuid.uuid4()
        self.content_node = self.mocker.mock()
        self.factory = StorageServerFactory(
            content_class=lambda _: self.content, reactor=self.fake_reactor)

    @inlineCallbacks
    def tearDown(self):
        """Tear down test."""
        try:
            self.mocker.verify()
        finally:
            yield super(TestDelivery, self).tearDown()
            self.mocker.restore()

    @inlineCallbacks
    def test_new_volume_generation_ok(self):
        """Test new volume generation delivery ok."""
        user = self.mocker.mock()
        expect(self.content.get_user_by_id('user_id')
               ).count(1).result(succeed(user))
        expect(user.broadcast).count(1).result(lambda *a, **kw: None)

        # test
        self.mocker.replay()
        notif = VolumeNewGeneration('user_id', 'vol_id', 23)
        yield self.factory.deliver_volume_new_generation(notif)

    @inlineCallbacks
    def test_new_volume_generation_not_connected(self):
        """Test new volume generation delivery for a not connected user."""
        expect(self.content.get_user_by_id('user_id')
               ).count(1).result(succeed(None))

        # test
        self.mocker.replay()
        notif = VolumeNewGeneration('user_id', 'vol_id', 23)
        yield self.factory.deliver_volume_new_generation(notif)

    @inlineCallbacks
    def test_new_volume_generation_broadcasting_message(self):
        """Test new volume generation delivery with correct message."""
        deferred = defer.Deferred()
        protocol = self.mocker.mock()

        def test(resp, filter):
            """Check that the broadcast message info is ok."""
            self.assertEqual(resp.type,
                             protocol_pb2.Message.VOLUME_NEW_GENERATION)
            self.assertEqual(resp.volume_new_generation.volume, 'vol_id')
            self.assertEqual(resp.volume_new_generation.generation, 66)

            # other session, and generations
            self.mocker.reset()
            expect(protocol.session_id).count(0, 1).result(uuid.uuid4())
            expect(protocol.working_caps).count(0, 1).result(['generations'])
            self.mocker.replay()
            self.assertTrue(filter(protocol))

            # same session, and generations
            self.mocker.reset()
            expect(protocol.session_id).count(0, 1).result(session_id)
            expect(protocol.working_caps).count(0, 1).result(['generations'])
            self.mocker.replay()
            self.assertFalse(filter(protocol))

            deferred.callback(None)

        user = self.mocker.mock()
        expect(self.content.get_user_by_id('user_id')
               ).count(1).result(succeed(user))
        expect(user.broadcast).result(test)

        # test
        self.mocker.replay()
        session_id = uuid.uuid4()
        notif = VolumeNewGeneration('user_id', 'vol_id', 66, session_id)
        yield self.factory.deliver_volume_new_generation(notif)
        yield deferred

    @inlineCallbacks
    def test_share_accepted_broadcasting_message(self):
        """Test that ShareAccepted gets broadcast to both users properly."""
        deferred_from = defer.Deferred()
        deferred_to = defer.Deferred()
        share_id = uuid.uuid4()
        from_user = 1
        to_user = 2
        root_id = uuid.uuid4()

        def test_from(resp, filter):
            """Check that the broadcast message info is ok."""
            self.assertEqual(resp.type,
                             protocol_pb2.Message.SHARE_ACCEPTED)
            self.assertEqual(resp.share_accepted.share_id, str(share_id))
            self.assertEqual(resp.share_accepted.answer,
                             protocol_pb2.ShareAccepted.YES)
            deferred_from.callback(None)

        def test_to(resp, filter):
            """Check that the broadcast message info is ok."""
            self.assertEqual(resp.type,
                             protocol_pb2.Message.VOLUME_CREATED)
            self.assertEqual(resp.volume_created.share.share_id, str(share_id))
            self.assertEqual(resp.volume_created.share.subtree, str(root_id))
            self.assertEqual(resp.volume_created.share.direction,
                             protocol_pb2.Shares.TO_ME)
            deferred_to.callback(None)

        user = self.mocker.mock()
        user2 = self.mocker.mock()

        for i in range(2):
            expect(
                self.content.get_user_by_id(from_user)).result(succeed(user))
            expect(
                self.content.get_user_by_id(to_user)).result(succeed(user2))

        expect(user.id).count(2).result(1)
        expect(user.broadcast).count(1).result(test_from)
        expect(user.username).count(1).result(u"username")
        expect(user.visible_name).count(1).result(u"username")
        expect(user2.id).count(2).result(2)
        expect(user2.broadcast).count(1).result(test_to)

        # test
        self.mocker.replay()
        notif_to = ShareAccepted(share_id, u"name", root_id, from_user,
                                 to_user, Share.VIEW, True)
        notif_from = ShareAccepted(share_id, u"name", root_id, from_user,
                                   to_user, Share.VIEW, True)
        yield self.factory.deliver_share_accepted(notif_to,
                                                  recipient_id=to_user)
        yield self.factory.deliver_share_accepted(notif_from,
                                                  recipient_id=from_user)
        yield deferred_from
        yield deferred_to

    @inlineCallbacks
    def test_share_accepted_broadcasting_no_from(self):
        """Test ShareAccepted when the from user isn't present."""
        deferred_to = defer.Deferred()
        share_id = uuid.uuid4()
        to_user = 1
        from_user = 2
        root_id = uuid.uuid4()

        def test_to(resp, filter):
            """Check that the broadcast message info is ok."""
            self.assertEqual(resp.type,
                             protocol_pb2.Message.VOLUME_CREATED)
            self.assertEqual(resp.volume_created.share.share_id, str(share_id))
            self.assertEqual(resp.volume_created.share.subtree, str(root_id))
            self.assertEqual(resp.volume_created.share.direction,
                             protocol_pb2.Shares.TO_ME)
            deferred_to.callback(None)

        user = self.mocker.mock()
        user2 = self.mocker.mock()
        for i in range(2):
            expect(self.content.get_user_by_id(from_user)
                   ).result(succeed(None))
            expect(self.content.get_user_by_id(to_user)).result(succeed(user2))
        expect(self.content.get_user_by_id(from_user, required=True)
               ).result(succeed(user))
        expect(user.username).count(1).result(u"username")
        expect(user.visible_name).count(1).result(u"username")
        expect(user2.id).count(2).result(2)
        expect(user2.broadcast).count(1).result(test_to)
        # test
        self.mocker.replay()
        notif = ShareAccepted(share_id, u"name", root_id, from_user, to_user,
                              Share.VIEW, True)
        notif2 = ShareAccepted(share_id, u"name", root_id, from_user, to_user,
                               Share.VIEW, True)
        yield self.factory.deliver_share_accepted(notif,
                                                  recipient_id=from_user)
        yield self.factory.deliver_share_accepted(notif2, recipient_id=to_user)
        yield deferred_to


class NotificationsTestCase(TestWithDatabase):
    """Notification tests."""

    def test_new_volume_generation(self):
        """Test VolumeNewGeneration notification delivery."""
        @defer.inlineCallbacks
        def test(client):
            """Test."""
            yield client.dummy_authenticate("open sesame")
            root = yield client.get_root()
            d = defer.Deferred()

            # hook the client callback
            client.set_volume_new_generation_callback(lambda *a: d.callback(a))
            notif = VolumeNewGeneration(self.usr0.id, root, 15)

            try:
                yield self.service.factory.deliver_volume_new_generation(notif)
            except Exception, e:
                client.test_fail(e)
            else:
                volume_id, new_generation = yield d
                self.assertEqual(str(volume_id), root)
                self.assertEqual(new_generation, 15)
                client.test_done()
        return self.callback_test(test)

    def test_notify_multi_clients(self):
        """Create 2 clients, make changes in one, check notif in the other."""

        def login1(client):
            """client1 login"""
            self._state.client1 = client
            d = client.dummy_authenticate("open sesame")
            d.addCallback(lambda _: new_client())
            d.addCallback(make_notification)

        def login2(client):
            """client2 login"""
            self._state.client2 = client
            client.set_volume_new_generation_callback(on_notification)
            d = client.dummy_authenticate("open sesame")
            d.addCallback(done_auth)

        # setup
        factory = FactoryHelper(login1)
        factory2 = FactoryHelper(login2)
        d1 = defer.Deferred()
        d2 = defer.Deferred()
        timeout = reactor.callLater(3, d1.errback, Exception("timeout"))

        def new_client():
            """add the second client"""
            reactor.connectTCP('localhost', self.port, factory2)
            return d2

        def on_notification(*args):
            """notification arrived, cleanup"""
            factory.timeout.cancel()
            factory2.timeout.cancel()
            timeout.cancel()
            d1.callback(True)
            self._state.client1.transport.loseConnection()
            self._state.client2.transport.loseConnection()

        def done_auth(result):
            """authentication done for client2, we can start making changes"""
            d2.callback(result)

        @defer.inlineCallbacks
        def make_notification(_):
            """Create a change that should create a notification."""
            root_id = yield self._state.client1.get_root()
            yield self._state.client1.make_file(request.ROOT, root_id, "hola")

        reactor.connectTCP('localhost', self.port, factory)
        return d1


class NotificationErrorsTestCase(TestWithDatabase):
    """Test Notification error handling.

    These tests will throw notifications at the server that will raise
    exceptions. Some events don't trigger exceptions in themselves, but an
    exception is created at broadcast.

    """

    induced_error = Failure(ValueError("Test error"))

    @defer.inlineCallbacks
    def setUp(self):
        yield super(NotificationErrorsTestCase, self).setUp()
        self.event_sent = defer.Deferred()
        self.notifier = FakeNotifier(event_sent_deferred=self.event_sent)
        self.patch(notifier, 'get_notifier', lambda: self.notifier)
        self.fake_reactor = DummyReactor()

        self.ssfactory = StorageServerFactory(reactor=self.fake_reactor)

        protocol = StorageServer()
        protocol.factory = self.ssfactory
        protocol.working_caps = ["volumes", "generations"]
        protocol.session_id = uuid.uuid4()
        self.patch(self.ssfactory.content, 'get_user_by_id',
                   lambda *a: self.induced_error)
        self.handler = self.add_memento_handler(logger)

    @defer.inlineCallbacks
    def check_event(self, event, **kwargs):
        """Test an error in node update."""
        self.notifier.send_event(event)
        yield self.event_sent

        actual = self.handler.records_by_level[logging.ERROR]
        self.assertEqual(len(actual), 1)
        expected = '%s in notification %r while calling deliver_%s(**%r)' % (
            self.induced_error.value, event, event.event_type, kwargs)
        self.assertEqual(actual[0].getMessage(), expected)

    def test_share_created(self):
        """Test the share events."""
        event_args = (
            uuid.uuid4(), u"name", uuid.uuid4(), 1, 2, Share.VIEW, False)
        return self.check_event(ShareCreated(*event_args))

    def test_share_deleted(self):
        """Test the share events."""
        event_args = (
            uuid.uuid4(), u"name", uuid.uuid4(), 1, 2, Share.VIEW, False)
        return self.check_event(ShareDeleted(*event_args))

    def test_share_declined(self):
        """Test the share events."""
        event_args = (
            uuid.uuid4(), u"name", uuid.uuid4(), 1, 2, Share.VIEW, False)
        return self.check_event(ShareDeclined(*event_args))

    def test_share_accepted(self):
        """Test the share events."""
        event_args = (
            uuid.uuid4(), u"name", uuid.uuid4(), 1, 2, Share.VIEW, True)
        return self.check_event(
            ShareAccepted(*event_args), recipient_id=u'test')

    def test_udf_delete(self):
        """Test UDF Delete."""
        return self.check_event(UDFDelete(1, uuid.uuid4(), uuid.uuid4()))

    def test_udf_create(self):
        """Test UDF Create."""
        return self.check_event(
            UDFCreate(1, uuid.uuid4(), uuid.uuid4(), u"path", uuid.uuid4()))

    def test_new_volume_gen(self):
        """Test the new gen for volume events."""
        event = VolumeNewGeneration(1, uuid.uuid4(), 77, uuid.uuid4())
        return self.check_event(event)
