# Standard Library
import io
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import timezone as tz
from inspect import cleandoc as trim_multiline

# Third Party Packages
import pytest

from toggl2harvest import utils
from toggl2harvest.utils import HOUR_IN_SECONDS


class TestParseStartEnd:
    @pytest.mark.parametrize('start,end,result', [
        ('2019-02-20', '2019-02-20', (dt(2019, 2, 20), dt(2019, 2, 20))),
    ])
    def test_parse_start_end(self, start, end, result):
        parsed = utils.parse_start_end(start, end)
        assert parsed == result


class TestIsoTimestamp:
    @pytest.mark.parametrize('result,time_value,', [
        ('2019-02-07T16:41:30-0700', dt(2019, 2, 7, 16, 41, 30, tzinfo=tz(td(-1, 61200)))),
        ('2019-03-19T16:41:30-0600', dt(2019, 3, 19, 16, 41, 30, tzinfo=tz(td(-1, 64800)))),
    ])
    def test_iso_timestamp(self, time_value, result):
        formatted = utils.iso_timestamp(time_value)
        assert formatted == result


class TestStrpIso8601:
    @pytest.mark.parametrize('time_string,result', [
        ('2019-02-07T16:41:30-07:00', dt(2019, 2, 7, 16, 41, 30, tzinfo=tz(td(-1, 61200)))),
        ('2019-03-19T16:41:30-06:00', dt(2019, 3, 19, 16, 41, 30, tzinfo=tz(td(-1, 64800)))),
    ])
    def test_parse_date(self, time_string, result):
        parsed = utils.strp_iso8601(time_string)
        assert parsed == result


class TestFmtTimedelta:
    @pytest.mark.parametrize('delta,correct', [
        (td(seconds=0), '0:00'),
        (td(seconds=1), '0:00'),
        (td(seconds=59), '0:00'),
        (td(minutes=1), '0:01'),
        (td(minutes=1, seconds=59), '0:01'),
        (td(minutes=59), '0:59'),
        (td(minutes=60), '1:00'),
        (td(hours=25), '25:00'),
        (td(hours=25, minutes=22), '25:22'),
        (td(days=3), '72:00'),
    ])
    def test_fmt_timedelta(self, delta, correct):
        formatted = utils.fmt_timedelta(delta)
        assert formatted == correct


class TestDeltaHours:
    @pytest.mark.parametrize('delta,correct', [
        (td(seconds=0), 0),
        (td(seconds=1), 1 / HOUR_IN_SECONDS),
        (td(seconds=59), 59 / HOUR_IN_SECONDS),
        (td(minutes=1), 60 / HOUR_IN_SECONDS),
        (td(minutes=1, seconds=59), 119 / HOUR_IN_SECONDS),
        (td(minutes=59), 3540 / HOUR_IN_SECONDS),
        (td(minutes=60), 1),
        (td(hours=25), 25),
        (td(hours=25, minutes=22), 25 + 1320 / HOUR_IN_SECONDS),
        (td(days=3), 72),
    ])
    def test_fmt_timedelta(self, delta, correct):
        hours = utils.delta_hours(delta)
        assert hours == correct


class TestCalcTotalTime:
    @pytest.mark.parametrize('entries,result', [
        # No difference should be 0
        (
            [{
                's': '2019-01-01T00:00:00-07:00',
                'e': '2019-01-01T00:00:00-07:00',
            }],
            td(seconds=0)
        ),
        # Adding 0 should be 0
        (
            [{
                's': '2019-01-01T00:00:00-07:00',
                'e': '2019-01-01T00:00:00-07:00',
            }, {
                's': '2019-01-01T00:00:00-07:00',
                'e': '2019-01-01T00:00:00-07:00',
            }],
            td(seconds=0)
        ),
        # We should be counting time between start and end
        (
            [{
                's': '2019-01-01T00:00:00-07:00',
                'e': '2019-01-01T00:00:01-07:00',
            }],
            td(seconds=1)
        ),
        # Times are purely additive, don't try and de-duplicate
        (
            [{
                's': '2019-01-01T00:00:00-07:00',
                'e': '2019-01-01T00:00:01-07:00',
            }, {
                's': '2019-01-01T00:00:00-07:00',
                'e': '2019-01-01T00:00:01-07:00',
            }],
            td(seconds=2)
        ),
        # Track more than just seconds
        (
            [{
                's': '2019-01-01T00:00:00-07:00',
                'e': '2019-01-02T00:00:00-07:00',
            }],
            td(days=1)
        ),
        # Time Zones should be taken into account
        (
            [{
                's': '2019-01-01T00:00:00-07:00',
                'e': '2019-01-01T01:00:00-06:00',
            }],
            td(seconds=0)
        ),
    ])
    def test_calculates_correct_time(self, entries, result):
        assert utils.calc_total_time(entries) == result


class TestGenerateSelectedDays:
    @pytest.mark.parametrize('start,end,result', [
        (dt(2019, 2, 20), dt(2019, 2, 20, 1), ['2019-02-20']),
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
        selected_days = utils.generate_selected_days(start, end)
        assert selected_days == result


class TestOperateOnDayData:
    @pytest.mark.parametrize('file_contents', [
        trim_multiline(entry) + '\n' for entry in [
        """
        a: key
        to: test  # with comment
        """,
        """
        a: key
        to: test  # with comment
        ---
        another: document
        """,
    ]])
    def test_operate_on_day_data(self, file_contents):
        def noop(i, data, **kwargs):
            return (data, kwargs)

        with io.StringIO() as output:
            utils.operate_on_day_data(file_contents, output, noop)

            output_value = output.getvalue()

        assert output_value == file_contents
