# Element under Doze after a lost reply, rented Pixel 9 Pro XL (Android 17)

3 trials with 600 s of forced deep idle (d00, 120 s, is the dev trial). In each, Element was alive in the background, the held reply was dropped at the Doze entry, and Element sent the same txnId again within 0.02 s (an immediate HTTP retry of the dropped request); Synapse deduplicated it. One server copy in 3/3; the row read "Sent" 2.46 to 2.58 s after the Doze exit. Not tested: a retry scheduled later that falls inside Doze.
