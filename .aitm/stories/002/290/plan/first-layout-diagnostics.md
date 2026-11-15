# #290 First layout diagnosis

The first local three-worker run reached 1,797 passes, eight test failures and twelve setup errors. This sample is invalid for timing comparison. The [complete traceback](first-layout.log) has SHA-256 `d11fc85b0e5edf59f37dab160393ca4c02332b1568bfcad710415fcfc89af949`. All [20 affected tests](first-layout-affected.txt) passed when rerun serially with fresh fixtures. [Focused output](first-layout-focused-serial.log)

The common failing source path was native stream discovery and revalidation on APFS. The scan snapshots the file's identity and every ancestor directory's change time. The harness put fixtures under the same directory that gains new per-PID coverage files during the run. The [controlled exact-source probe](check-path-layout.py) confirms that creating an evidence file in that ancestor changes the ancestor change time and invalidates the fixture path while leaving the fixture file identity intact. The sibling fixture path remains stable. [Probe output](path-layout-control.log)

The retry uses separate precreated fixture and evidence trees. Native probing and coverage checks remain as defined on the pinned trunk source. Timing evidence is pending the corrected matrix.
