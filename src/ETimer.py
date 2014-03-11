"""
Timer and timeout functionality.

File used to get the current time to use when checking for timeouts. This has been extracted to a separate
file as a workaround for a bug or design flaw in the Python 2.7 versions of the Telit products where time.time()
takes around 100ms to complete. As a workaround time.clock() can be used to get a relative timestamp. This
seems fairly predictable on Telit. However, on the desktop this returns the CPU time which is not at all the
same. In that case ETimer.time can be overridden to use the non-broken time.time()
"""

import time

# Default to time.clock() on Telit platforms.
time = time.clock
