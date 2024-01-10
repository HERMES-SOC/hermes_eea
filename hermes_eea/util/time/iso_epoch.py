import cdflib
import dateutil.parser
from sys import stderr
from datetime import datetime, date, timedelta
import spacepy.time as spt
import re
import numpy as np

def jday_to_iso(jday: str):
    try:
        dateobj = datetime.strptime(jday, '%Y-%jT%H:%M:%S.%f').date()
    except ValueError:
        dateobj = datetime.strptime(jday, '%Y-%jT%H:%M:%S').date()
    return dateobj

def parseJdayRep(rangeItem):
    _apid_pattern = (re.compile("APID\((?P<apid>\d+)\)"),)
    jdayRep = re.compile("(\d\d\d\d)-([\d]+)[/ T]*(\d\d:\d\d:\d\d)[.\d]*")
    year = jdayRep.match(rangeItem).group(1)
    assert int(year) > 0
    doy = jdayRep.match(rangeItem).group(2)
    assert int(doy) > 0
    tod = jdayRep.match(rangeItem).group(3)
    assert len(doy) > 0, f"expected 8, got: {len(doy)}"
    iso_version = datetime.strptime(year + doy, "%Y%j").date()
    full_iso = dateutil.parser.parse(iso_version.strftime("%Y-%m-%d") + "T" + tod)
    return full_iso


def tblenddate_to_iso(tblenddate):
    d = datetime.strptime(tblenddate, "%Y%m%d%H%M%S")
    return d


def convert_to_micro_seconds(iso_date: datetime):
    """
    PODA Doesn't need it but traditionally the http request is done using these
    kinds of times
    :param iso_date:
    :return:time in microseconds since 1980 for the PODA http request for packet dqta
    """
    epoch_start = dateutil.parser.parse("1980-01-06T00:00:00")
    iso_jd = spt.Ticktock(iso_date)
    epoch_start_jd = spt.Ticktock(epoch_start)
    diff = iso_jd.JD[0] - epoch_start_jd.JD[0]
    ss = diff * 86400 + iso_jd.leaps - epoch_start_jd.leaps
    ss = round(ss[0]) * 1000000
    return ss


def iso_obj_to_epoch(trange):
    """
    ISO to CDF EPOCH:
    cdflib.epochs.CDFepoch.parse('2012-01-01T01:01:01.000000000')

    :param trange: a list, typically 2, of datetime objects
    :return:18 digit epoch times for CDF
    """
    converted = []
    for t in trange:
        #dateString = t.strftime("%Y-%m-%dT%H:%M:%S.000000000")
        dateString = t.strftime("%Y-%m-%dT%H:%M:%S.%f000")
        try:
            c = cdflib.epochs.CDFepoch.parse(dateString)
            converted.append(c)
        except ValueError as e:
            print(t + " This time range value doesn't look too kosher...", file=stderr)
        # exit(1)
    return converted
def iso_to_epoch(trange):
    """
    ISO to CDF EPOCH:
    cdflib.epochs.CDFepoch.parse('2012-01-01T01:01:01.000000000')

    :param trange: a list, typically 2, of datetime strings
    :return:18 digit epoch times for CDF
    """
    converted = []
    for t in trange:
        try:
            c = cdflib.epochs.CDFepoch.parse(t)
            converted.append(c)
        except ValueError as e:
            print(t + " This time range value doesn't look too kosher...", file=stderr)
        # exit(1)
    return converted

'''
This returns a string, not a date object
'''
def epoch_to_iso(trange):
    """
    CDF EPOCH TO ISO:
    cdflib.epochs.CDFepoch.encode_tt2000(378651727184000000)

    :param trange:18 digit CDF epoch times
    :return:a list,typically 2, of datetime strings in iso format
    """
    in_iso = []
    for t in trange:
        c = cdflib.epochs.CDFepoch.encode_tt2000(int(t))
        in_iso.append(c)
    return in_iso

def epoch_to_eea_iso(trange):
    """
    CDF EPOCH TO ISO:
    cdflib.epochs.CDFepoch.encode_tt2000(378651727184000000)

    :param trange:18 digit CDF epoch times
    :return:a list,typically 2, of datetime strings in iso format
    """
    in_iso = []
    for t in trange:
        c = cdflib.epochs.CDFepoch.encode_tt2000(int(t)) # this number is based on an EEA, not FPI TAI time
        in_iso.append((c.replace("T"," ")[0:19]))
    return in_iso

def epoch_to_iso_obj(trange):
    """
    CDF EPOCH TO ISO:
    cdflib.epochs.CDFepoch.encode_tt2000(378651727184000000)

    :param trange:18 digit CDF epoch times
    :return:a list,typically 2, of datetime strings in iso format
    """
    in_iso = []
    for t in trange:
        c = cdflib.epochs.CDFepoch.encode_tt2000(int(t))
        d = datetime.strptime(c[0:26], "%Y-%m-%dT%H:%M:%S.%f")
        in_iso.append(d)
    return in_iso

def str_to_iso(str_range):
    iso_range = []
    for t in str_range:
        try:
            iso_range.append(datetime.strptime(t, '%Y-%m-%dT%H:%M:%S.%f'))
        except ValueError:
            try:
                iso_range.append(datetime.strptime(t[0:26], '%Y-%m-%dT%H:%M:%S.%f'))
            except ValueError:
                iso_range.append(datetime.strptime(t[0:19], '%Y-%m-%dT%H:%M:%S'))

    return iso_range    #iso_range.append(t.strftime("%Y-%m-%dT%H:%M:%S.%f"))

def cdf_epoch_tojuldays(epoch_time):
    """
    print,cdf_epoch_tojuldays(567098205397306000) = 2458108.6'
    cdflib.epochs.CDFepoch.currentJDay()
    if you give this guy a midnight value it gives you .5
    If you give this guy a noon value then it gives you .0
    So if our time is 03:00 then 12+3=15/24=.625

    Doesn't seem to be used at the moment

    :param epoch_time:
    :return:
    """

    iso_string = cdflib.epochs.CDFepoch.encode_tt2000(epoch_time)
    iso_obj = dateutil.parser.parse(iso_string)
    jDayP1 = cdflib.epochs.CDFepoch._JulianDay(iso_obj.year, iso_obj.month, iso_obj.day)
    fraction = 12 + iso_obj.hour
    jday = jDayP1 - 1 + fraction
    return jday

def cdf_epoch_tojuldays_24(epoch_time):
    """
    print,cdf_epoch_tojuldays(567098205397306000) = 2458108.6'
    cdflib.epochs.CDFepoch.currentJDay()
    if you give this guy a midnight value it gives you .5
    If you give this guy a noon value then it gives you .0
    So if our time is 03:00 then 12+3=15/24=.625

    Doesn't seem to be used at the moment

    :param epoch_time:
    :return:
    """
    if isinstance(epoch_time, str):
        Epoch_FS0 = int(epoch_time)
        iso_obj = epoch_to_iso([Epoch_FS0])
    elif isinstance(epoch_time, datetime):
        iso_obj = epoch_time
    elif isinstance(epoch_time,int):
        iso_string = cdflib.epochs.CDFepoch.encode_tt2000(epoch_time)
        iso_obj = dateutil.parser.parse(iso_string)
    elif epoch_time.dtype == np.uint64:
        iso_string = cdflib.epochs.CDFepoch.encode_tt2000(epoch_time)
        iso_obj = dateutil.parser.parse(iso_string)

    jDayP1 = cdflib.epochs.CDFepoch._JulianDay(iso_obj.year, iso_obj.month, iso_obj.day)
    fraction = 12 + iso_obj.hour
    jday = jDayP1 -1 + fraction/24
    return jday



'''
Nominally,Epoch_FS0 is one of the elements of the epoch
array extracted using Daniel's ccsds.py and as such is np.int64 '''
def epoch_to_matching(Epoch_FS0):
    """
    This produces the YYYYMMDDHHMMSSmillisec 20 char string used for match data tables'''

    :param Epoch_FS0: 18 digit epoch time
    :return: iso formatted string
    """
    if isinstance(Epoch_FS0, str):
        Epoch_FS0 = int(Epoch_FS0)
        isoTimeString = epoch_to_iso([Epoch_FS0])
        mD = dateutil.parser.parse(isoTimeString[0])
    elif isinstance(Epoch_FS0,datetime):
        mD = Epoch_FS0
    elif Epoch_FS0.dtype == np.uint64:
        isoTimeString = epoch_to_iso([Epoch_FS0])
        mD = dateutil.parser.parse(isoTimeString[0])

    matchingString = "".join(
        [
            str(mD.year),
            "{:02d}".format(mD.month),
            "{:02d}".format(mD.day),
            "{:02d}".format(mD.hour),
            "{:02d}".format(mD.minute),
            "{:02d}".format(mD.second),
        ]
    )
    return matchingString

