OTLS Control Codes!
Several changes need to be made for new systems:
1. Change the ymax, ymin, xmax, xmin, ypp, xpp, and etl in daq_control.py
2. Change the self.ymax and self.eoffset in OTLS_preview_table.py
3. The static_params.json and power_current.json are unique for each system, refill or remeasure the infromation in these two files