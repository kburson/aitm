# #287 Local evidence

Exact base `a85d088fdb0a4e36c78b848cc1c2bd1b1f2b08b2`, head `9a50c675a3d0180eb91c16bd13024a6f6e6d1f95`, tree `acd6409a2722558c82c62dfe4647c36c8439dc90`. The product and CLI profile collected the same ordered 1,216 IDs before and after. The focused native family passed 72 cases. Ruff lint and formatting passed.

Each of five matched serial pairs used private fixtures and the same instrumented test. The parent made seven direct snapshot reads per test and the candidate made four. Median measured time inside those reads was 114 ms and 60 ms, respectively. Median full focused test time was 2.73 and 2.68 seconds. This is a small local test optimization. The samples provide no estimate of end-to-end CI savings.

A disposable copy suppressed the reported settlements from the public journal view. The candidate failed at `assert settled.settlements == (change,)` as expected. This counterfactual was confined to the disposable copy.

[Paired measurement results](timing.json) · [Benchmark recipe](bench.sh) · [Measurement plugin](measure_journal.py).
