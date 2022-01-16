from tools import data
import unittest

class TestUrl(unittest.TestCase):
    """
    Test case for data.validUrl class
    """
    def setUp(self):
        self.url_list = ['https://pytutorial.com/check-strig-url',
                            'https;?fakeurl',
                            'https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/2021/visa-bulletin-for-january-2021.html'
                            ]

    def test_valid(self):
        result = []
        for url in self.url_list:
            obj = data.validUrl(url)
            result.append(obj.is_valid_url())

        self.assertEqual(result, [True, False, True])

    def tearDown(self) -> None:
        return super().tearDown()

if __name__ == '__main__':
    unittest.main() #command line interface to this test script