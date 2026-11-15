# #287 Consolidate duplicate settlement snapshot reads

Use one post-settlement read within the existing named test, preserving historical state readback, transaction outcomes, both side checks, and the separate replay observation. Keep all test IDs and assertions. Confirm the focused test still fails if the post-settlement view loses its recorded settlement. Compare repeated native runs against the exact frozen parent with fresh fixture locations. Measure direct read counts and time separately from total runtime. Deliver after hosted #103 and independent review of the exact tree.
