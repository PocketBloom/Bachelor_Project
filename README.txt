
The code in this directory was created for a Bachelor Project on the topic of:
Ephemerides of Near-Earth Asteroids to Constrain the PPN parameter (beta) and 
the Solar Quadrupole Moment (J_2o): The Potential of Stellar Occultations.

In order to acheive the results of the project and to map out and estimate the 
NEAs' ephemerides, the free open-source software Tudat (and TudatPy), was used.
The code from Tudat is distributed under the BSD 3-Clause License. 
The code repository for Tudat is available here https://github.com/tudat-team 
and the examples used to start this research project are found on:
https://docs.tudat.space/en/latest/ ,  
https://docs.tudat.space/en/latest/index-examples.html#getting-started-examples ,
and https://py.api.tudat.space/en/latest/, which are distributed under the same license.


The code for this project is divided into two overaching themes:
propagation and estimation of orbits.

# -------------------------------------------------------------------
1. PROPAGATION:

In order to properly understand where the asteroids will be, and to eventually
estimate their ephemerides (so that the underlying effects that govern their motions can 
be deciferred), I first created a statistically viable model of the Solar System.

I then tested this model by propagating an asteroid and examining its behaviours.

The main code for this are found in the folder PROPAGATION:

i. PROPAGATION/TU3_linear_dw.ipynb = simple propagation case, 
testing with the Sun as a point-mass, then adding GR, J2, Yark
and examining the slope of dw

ii. PROPAGATION/TU3_orbit_precession_2.ipynb = propagation using
the entire Solar System model (so this file contains how I figured
out how to apply 20 smaller asteroids and their mass to the code).

iii. PROPAGATION/Creating_Plots.ipynb = to properly contextualise
and explain the results I made this file to showcase all three cases 
that I tested for into one file. Otherwise I couldn't compare case 1
(Sun as a point-mass) vs case 2 (GR, J2, Yark).

iv. PROPAGATION/Creating_Errors.ipynb = lastly to showcase the errors 
of the model I defined different parameters to have a slight and reasonable
offset. Thereafter I propagated the model with these offsets. The 
difference in values are the error bars.

# -----

1.2 Planet_Effects

The folder Planet_Effects contains the code I wrote when testing for
how larger bodies affected asteroid 1998 TU3 (66146).

This was important in order to gain confidence in the model.

I tested for the planets which I believed would have the largest influence 
and tried to have the planets ON (only test for asteroid TU3, that planet
and the Sun), and OFF (only test for the asteroid TU3, all other important
bodies, the Sun and NOT that specific planet). This was beneficial with
e.g. Julipter, because it caused an oscillatory effect.


# ----

1.3 Photos_Folder:

This folder contains all the photos and animations which I accumulated while
testing the model

# ----

1.4 TU3

This folder contains all of the trial runs (some okay and some quite unseccessful)
of propagating asteroid TU3. See PROPAGATION for the relatively cleaner version.

# ------------------------------------------------------------------------------------

2. ESTIMATE

It is worth mentioining that the folder Estimation contains many files
that tirelessly attempted to estimate for asteroids. It turned out to
be a bit more challenging than expected to estimate for lesser well-known
asteroids and to create a model which didn't create hUGE errors. Thus,
the folder ESTIMATE contains the final versions of many (many) attempts.

i. ESTIMATE/Improved_Initial_State_Est_MPC_EB_wMatrix.ipynb = the first
file that properly carried out an estimation of the chosen asteroids

ii. ESTIMATE/Clean_estimate-ALL_9.ipynb = where I began estimating for
all and then 4 asteroids (because all 9 gave very large errors).

iii. ESTIMATE/Clean_estimate_Occult.ipynb = the file in which I created
the first stellar occultation. I then added many more and created functions
in the same file. (PS: I did clean the file slightly, but for the long 
history of creating the stellar occults, see Estimation/Clean_estimate-Occult.ipynb)

iv. ESTIMATE/Clean_estimate_error_reduce.ipynb = added stellar occultations
and examined how the errors of the positions and velocities decreased

v. ESTIMATE/ALL_Clean_estimate-Occults.ipynb = tried estimating for all 
and adding stellar occultations for all


#--------------------------------------------------------------

Other folders:

In Table_of_Asteroids, in file Table_of_Asteroids/test_Table_code.ipynb,
I created the table in the Bachelor Thesis which displays all a,e,i,dw values
(they were all pulled from JPL Horizon and dw was calculated).

In 9_asteroids, I propagated all 9 asteroids (that were examined by Verma et al).






# -------------------------------------------------------------

NOTE: below is a message from Tudat, which was automatically printed into the GITHUB 
when installing Tudat.

The file bias.dat is a table of position and proper motion corrections
for 26 star catalogs.
The corrections are provided for both right ascension (RA) and
declination (DEC).

For each of these catalogs the file contains four columns:
- dRA, position correction in RA*cos(DEC) at epoch J2000.0 [arcsec];
- dDEC, position correction in DEC at epoch J2000.0 [arcsec];
- pmRA, proper motion correction in RA*cos(DEC) [mas/yr];
- pmDEC, proper motion correction in DEC [mas/yr].

Each row corresponds to different tiles in the sky.
The algorithm to subdivide the sky in equal area tiles is described
by Gorsky et al. 2005 (http://adsabs.harvard.edu/abs/2005ApJ...622..759G).

As a reference, for each tile the file tiles.dat gives the coordinates RA and DEC of
the tile center. The tiles correspond to those in file bias.dat, 
i.e., the rows are sorted in the same way.

To correct the astrometric asteroid observations, the following
should be subtracted from the observed RA and DEC:

( dRA + (t - 2000.0)*pmRA/1000 ) / cos(DEC)
 dDEC + (t - 2000.0)*pmDEC/1000

where t is the observation epoch (in years) and dRA, dDEC, pmRA, and
pmDEC can be obtained from bias.dat according to the star catalog
used and the tile containing the astrometric position. 

For more details see Eggl et al. (2020, Icarus).

UPDATE, March 1, 2023
The start catalog code for catalog UCAC-5 has been corrected from W to
Y in the comments and headers of the debiasing data file.  W is
currently the catalog code assigned to Gaia-DR3 and was incorrectly
assigned to UCAC-5 by the MPC at the time this debiasing scheme was
developed.
