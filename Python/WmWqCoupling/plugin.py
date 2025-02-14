import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wq_wrapper as wq
import wm_wrapper as wm
sys.path.append(r"C:\Work\Main\Products\bin\x64")
import MShePyd as ms

items = []
sim_start = None
total_h_wq = 0

def transfer():
  for item, set in items:
    start, end, values = wm.get_values(item, set)
    wq.set_values(item, set, values)

def postEnterSimulator():
  global items, sim_start
  she_path = ms.wm.getSheFilePath()
  sim_start, _ = ms.wm.simPeriod()
  ok  = wq.init(she_path)
  ok &= wq.openmi_init()
  n_items = wq.get_input_exchange_item_count()
  for i in range(n_items):
    item_id, element_set, _, _, _, _, needed = wq.get_input_exchange_item(i)
    if needed:
      items.append([item_id, element_set])
  item_list = ";".join(sublist[0] for sublist in items)
  ok &= wq.openmi_prepare(item_list)
  if not ok:
    raise Exception("Error initializing WQ")

def postTimeStep():
  global total_h_wq
  current_wm = ms.wm.currentTime()
  total_h_wm = (current_wm - sim_start).total_seconds() / 3600
  ms.wm.log(f"New WM time: {total_h_wm} h")
  #closest_checkpoint = round(total_h_wm / 12) * 12
  #if abs(total_h_wm - closest_checkpoint) < 5 / 3600: # within 5 s of checkpoint?
  if (total_h_wm - total_h_wq) >= 11.999:
    while total_h_wm > total_h_wq:
      wq.set_wm_coupling_time_h(total_h_wm)
      transfer()
      ms.wm.log(f"Running WQ from {total_h_wq} h ...")
      ok, time_step_h, total_h_wq = wq.perform_time_step()
      ms.wm.log(f"... finishing at {total_h_wq} h")
      if not ok:
        raise Exception("Error performing WQ time step")

def leaveSimulator():
  wq.terminate(True)
