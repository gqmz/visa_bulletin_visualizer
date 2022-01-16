from tools import data
import unittest

class TestUrlData(unittest.TestCase):
    """
    Test case for data.getUrlData class
    Assumption: ONLY urls from data.urlGen get passed to data.getUrlData class, so formatting will always be consistent
    """
    def setUp(self):
        self.url_list = [
                            # 'https://pytutorial.com/check-strig-url', #non-pertinent url
                            # 'https;?fakeurl', #fake url
                            'https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/2021/visa-bulletin-for-january-2021.html', #should have correct tables & return data
                            'https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/2021/visa-bulletin-for-january-2030.html', #non-existent url
                            'https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/3000/visa-bulletin-for-january-2030.html' #non-existent url
                            ]

    def test_data(self):
        """
        Test data output from data.getUrlData class
        """
        result = []
        for url in self.url_list:
            obj = data.getUrlData(url)
            result.append(len(obj.data))

        self.assertEqual(result, [16, 0, 0])

    def tearDown(self) -> None:
        return super().tearDown()

if __name__ == '__main__':
    unittest.main() #command line interface to this test script