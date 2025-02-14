import sys
import wq_wrapper as wq
import wm_wrapper as wm
import model as m
sys.path.append(r"C:\Work\Main\Products\bin\x64")
import MShePyd as ms

# ms.wm.initialize(m.she_path, wq_coup=1)

def transfer():
  for item, set in items:
    start, end, values = wm.get_values(item, set)
    wq.set_values(item, set, values)

ok = wq.init(m.she_path)
ok &= wq.openmi_init()
items = []
n_items = wq.get_input_exchange_item_count()
for i in range(n_items):
  item_id, element_set, _, _, _, _, needed = wq.get_input_exchange_item(i)
  if needed:
    items.append([item_id, element_set])

item_list = ";".join(sublist[0] for sublist in items)
ok &= wq.openmi_prepare(item_list)
total_h = 0
for i in range(8):
  ms.wm.log(f"Time step {i + 1}")
  if(ok):
    taken, dt_step_h, sim_time = ms.wm.performTimeStep()
    total_h += dt_step_h
    ms.wm.log(f"  dt_step_h: {dt_step_h}, sim_time: {sim_time}")
    ms.wm.log(f"  total_h: {total_h}")
    wq.set_wm_coupling_time_h(total_h)
    transfer()
    ms.wm.log("  Now performing WQ time step...")
    ok, time_step_h, total_h_wq = wq.perform_time_step()
    ms.wm.log("  OK" if ok else "   FAILED")
ok &= wq.terminate(ok)
ms.wm.terminate(ok)
exit(0 if ok else 1)
