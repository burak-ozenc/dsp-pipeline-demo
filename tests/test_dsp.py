# import numpy as np
# from dsp.analyze import (
#     calc_clipping_ratio,
#     safe_float
# )
# 
# def test_clipping_ratio_full_clip():
#     # all samples at max amplitude should return 1.0
#     audio = np.ones(1000)
#     assert calc_clipping_ratio(audio) == 1.0
# 
# def test_clipping_ratio_no_clip():
#     # quiet signal should have zero clipping
#     audio = np.ones(1000) * 0.5
#     assert calc_clipping_ratio(audio) == 0.0
# 
# def test_safe_float_handles_nan():
#     # your safe_float should return None for NaN
#     assert safe_float(float('nan')) is None
# 
# def test_safe_float_handles_inf():
#     assert safe_float(float('inf')) is None
# 
# def test_safe_float_normal_value():
#     assert safe_float(3.14) == 3.14