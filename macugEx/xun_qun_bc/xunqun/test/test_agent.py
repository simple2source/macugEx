import unittest
import testrunner
import time
from agent.client import Demand, Dispose
from agent.alphabet import OK, NO, TIMEOUT, DEMANDTIMEOUT
import setting

resource = {
    'device1': 'device1',
}


def interact(identity, instruct, message):
    if instruct == 'ok':
        return OK
    if instruct == 'no':
        return NO
    if instruct == 'timeout':
        time.sleep(DEMANDTIMEOUT)


def interact_noblock(identity, instruct, message):
    return OK if instruct == 'hello' else NO


class TestDemand(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dispose = Dispose(resource, setting.broker['host'], setting.broker['respond_port'],
                          setting.broker['channel_port'], interact=interact, interact_noblock=interact_noblock)
        dispose.start()
        # make the dispose connect to broker server before demand send any request
        time.sleep(0.1)

        cls.demand = Demand(setting.broker['host'], setting.broker['request_port'])

    def test_find(self):
        result = self.demand.find('device1')
        self.assertEqual(result, OK)
        result = self.demand.find('device2')
        self.assertEqual(result, NO)

    def test_send(self):
        result = self.demand.send('device1', 'ok', '')
        self.assertEqual(result, OK)
        result = self.demand.send('device1', 'no', '')
        self.assertEqual(result, NO)
        # result = self.demand.send('device1', 'timeout', '')
        # self.assertEqual(result, TIMEOUT)

    def test_get_list(self):
        dev_list = self.demand.getlist(0, 10)
        self.assertEqual(dev_list, ['device1'])

    def test_get_total(self):
        num = int(self.demand.gettotal())
        self.assertEqual(num, 1)


if __name__ == '__main__':
    testrunner.main()
