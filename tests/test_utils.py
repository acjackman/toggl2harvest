import pytest

from datetime import datetime as dt

from toggl2harvest.utils import parse_start_end, generate_selected_days

class TestParseStartEnd:
    @pytest.mark.parametrize("start,end,result", [
        ('2019-02-20', '2019-02-20', (dt(2019, 2, 20), dt(2019, 2, 20))),
    ])
    def test_parse_start_end(self, start, end, result):
        parsed = parse_start_end(start, end)
        assert parsed == result


class TestGenerateSelectedDays:
    @pytest.mark.parametrize("start,end,result", [
        (dt(2019, 2, 20), dt(2019, 2, 20), ['2019-02-20']),
        (dt(2019, 1, 1), dt(2019, 1, 2), ['2019-01-01', '2019-01-02']),
        (dt(2019, 1, 1), dt(2019, 1, 5), [
            '2019-01-01',
            '2019-01-02',
            '2019-01-03',
            '2019-01-04',
            '2019-01-05'
        ]),
    ])
    def test_generate_selected_days(self, start, end, result):
        selected_days = generate_selected_days(start, end)
        assert selected_days == result

