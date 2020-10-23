import os
from subprocess import check_output
from datetime import datetime
import astropy.coordinates as ac
from astropy.time import Time, TimeDelta
import astropy.units as un

from delay_models import CalcReader
from calcfile import make_calc


# Set up times, locations, and sources.

time = Time(datetime(2017, 10, 28, 15, 30, 00))

gbo_loc = ac.EarthLocation.of_site("GBT")
chime_loc = ac.EarthLocation.from_geodetic(lat=ac.Latitude('49d19m15.6s'), lon=ac.Longitude('119d37m26.4s'))

crab = ac.SkyCoord('05:34:31.9383', '22:00:52.175', unit=(un.hourangle, un.deg), frame='icrs')
ip_peg = ac.SkyCoord("23:23:08.55", "+18:24:59.3", unit=(un.hourangle, un.deg), frame='icrs')

# choose a source to use.
src = crab

t0 = time + TimeDelta(1, format='sec')
t1 = t0.copy()
t0.location = gbo_loc
t1.location = chime_loc
ltt0 = t0.light_travel_time(src, ephemeris='jpl')
ltt1 = t1.light_travel_time(src, ephemeris='jpl')

astr_delay = (ltt1 - ltt0).to_value('us')


# Make a calc file
calcname = "new.calc"
telescope_positions = [chime_loc, gbo_loc]
telescope_names = ['chime', 'gbo']
source_coords = [src]
source_names = ['src']
duration_min = 4

make_calc(telescope_positions, telescope_names, source_coords,
          source_names, time, duration_min, ofile_name=calcname)


# Run difxcalc
if os.path.exists('new.im'):
    os.remove('new.im')

result = check_output(["difxcalc", '-v', calcname])

rd = CalcReader()
rd.read_im('new.im')

difx_delay = rd.baseline_delay(1, 0, t0, 0)

# Compare to astropy
print(difx_delay, astr_delay)
