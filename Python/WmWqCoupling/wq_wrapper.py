import ctypes

lib = ctypes.CDLL(r"C:\Work\Main\Products\bin\x64\MShe_wqd.dll", winmode=0)
LeID =  50 # Copy from WQ MOpenMI.f90, keep up to date!

#---------------------------------------------------
lib.MSHEWQ_INIT.argtypes = [
  ctypes.c_char_p,
  ctypes.POINTER(ctypes.c_int),
  ctypes.POINTER(ctypes.c_int),
  ctypes.c_size_t
]
lib.MSHEWQ_INIT.restype = ctypes.c_int

def init(she_path):
  path_encoded = she_path.encode()
  batch = ctypes.c_int(0)
  wmwq = ctypes.c_int(1)
  str_len = ctypes.c_size_t(len(she_path))
  res = lib.MSHEWQ_INIT(path_encoded, ctypes.byref(batch), ctypes.byref(wmwq), str_len)
  return res != 0

#---------------------------------------------------

lib.MSHEWQ_OPENMI_INIT.argtypes = []
lib.MSHEWQ_OPENMI_INIT.restype = ctypes.c_int

def openmi_init():
  return lib.MSHEWQ_OPENMI_INIT() != 0

#---------------------------------------------------

lib.MSHEWQ_GETINPUTEXCHANGEITEMCOUNT.argtypes = []
lib.MSHEWQ_GETINPUTEXCHANGEITEMCOUNT.restype = ctypes.c_int

def get_input_exchange_item_count():
  return lib.MSHEWQ_GETINPUTEXCHANGEITEMCOUNT()

#---------------------------------------------------

lib.MSHEWQ_GETINPUTEXCHANGEITEM.argtypes = [
  ctypes.POINTER(ctypes.c_int),     # (in)  item index
  ctypes.c_char_p,                  # (out) item ID
  ctypes.c_char_p,                  # (out) element set ID
  ctypes.c_char_p,                  # (out) item description
  ctypes.POINTER(ctypes.c_int),     # (out) eumType
  ctypes.POINTER(ctypes.c_int),     # (out) eumUnit
  ctypes.POINTER(ctypes.c_int),     # (out, bool) hidden?
  ctypes.POINTER(ctypes.c_int),     # (out, bool) neededForWmCoupling?
  ctypes.c_size_t,                  # string length 1
  ctypes.c_size_t,                  # string length 2
  ctypes.c_size_t                   # string length 3
]
lib.MSHEWQ_GETINPUTEXCHANGEITEM.restype = ctypes.c_int

def get_input_exchange_item(item):  
  i = ctypes.c_int(item + 1)
  buf1 = ctypes.create_string_buffer(LeID)
  buf2 = ctypes.create_string_buffer(LeID)
  buf3 = ctypes.create_string_buffer(LeID)
  l = ctypes.c_size_t(LeID)
  eum_type   = ctypes.c_int(0)
  eum_unit   = ctypes.c_int(0)
  hidden     = ctypes.c_int(0)
  needed_wm  = ctypes.c_int(0)
  lib.MSHEWQ_GETINPUTEXCHANGEITEM(
    ctypes.byref(i),
    buf1, buf2, buf3,
    ctypes.byref(eum_type), ctypes.byref(eum_unit), ctypes.byref(hidden), ctypes.byref(needed_wm),
    l, l, l
    )
  return (
    buf1.value.decode().rstrip(), buf2.value.decode().rstrip(), buf3.value.decode(),
    eum_type.value, eum_unit.value, hidden.value != 0, needed_wm.value != 0
  )

#---------------------------------------------------

lib.MSHEWQ_GETOUTPUTEXCHANGEITEMCOUNT.argtypes = []
lib.MSHEWQ_GETOUTPUTEXCHANGEITEMCOUNT.restype = ctypes.c_int

def get_output_exchange_item_count():
  return lib.MSHEWQ_GETOUTPUTEXCHANGEITEMCOUNT()

#---------------------------------------------------

lib.MSHEWQ_PREPARE.argtypes = [
  ctypes.POINTER(ctypes.c_int),
  ctypes.c_char_p,
  ctypes.c_size_t
]
lib.MSHEWQ_PREPARE.restype = ctypes.c_int

def openmi_prepare(used_quantity_ids):  
  nexquantities = ctypes.c_int(len(used_quantity_ids))
  listOfUsedquantityIDs = used_quantity_ids.encode()
  str_len = ctypes.c_size_t(len(listOfUsedquantityIDs))
  return lib.MSHEWQ_PREPARE(nexquantities, listOfUsedquantityIDs, str_len) != 0

#---------------------------------------------------

lib.MSHEWQ_SETVALUES.argtypes = [
  ctypes.c_char_p,
  ctypes.c_char_p,
  ctypes.POINTER(ctypes.c_int),
  ctypes.POINTER(ctypes.c_double),
  ctypes.c_size_t,
  ctypes.c_size_t
]
lib.MSHEWQ_SETVALUES.restype = ctypes.c_int

def set_values(quantity_ID, element_set_ID, values):
  quantityID = quantity_ID.encode()
  q_len = ctypes.c_size_t(len(quantityID))
  elementSetID = element_set_ID.encode()
  e_len = ctypes.c_size_t(len(elementSetID))
  n = ctypes.c_int(len(values))
  values_c = (ctypes.c_double * len(values))(*values)
  res = lib.MSHEWQ_SETVALUES(quantityID, elementSetID, ctypes.byref(n), values_c, q_len, e_len)
  return res != 0

#---------------------------------------------------

lib.MSHEWQ_PERFORMTIMESTEP.argtypes = [
  ctypes.POINTER(ctypes.c_double),
  ctypes.POINTER(ctypes.c_double)
]
lib.MSHEWQ_PERFORMTIMESTEP.restype = ctypes.c_int

def perform_time_step():
  dtUsedSeconds = ctypes.c_double(0.0)
  relativeSecsFromStart = ctypes.c_double(0.0)
  res = lib.MSHEWQ_PERFORMTIMESTEP(ctypes.byref(dtUsedSeconds), ctypes.byref(relativeSecsFromStart)) != 0 # r8 out, r8 out
  return res != 0, dtUsedSeconds.value / 3600.0, relativeSecsFromStart.value / 3600.0

#---------------------------------------------------

lib.MSHEWQ_SETWMCOUPLINGTIME.argtypes = [
  ctypes.POINTER(ctypes.c_double)
]
lib.MSHEWQ_SETWMCOUPLINGTIME.restype = ctypes.c_int

def set_wm_coupling_time_h(wm_time_h):
  wmTimeSec = ctypes.c_double(wm_time_h * 3600.0)
  res = lib.MSHEWQ_SETWMCOUPLINGTIME(ctypes.byref(wmTimeSec))
  return res != 0

#---------------------------------------------------

lib.MSHEWQ_TERMINATE.argtypes = [
  ctypes.POINTER(ctypes.c_int),
  ctypes.POINTER(ctypes.c_int)
]
lib.MSHEWQ_TERMINATE.restype = ctypes.c_int

def terminate(success):
  lNormalTermination = ctypes.c_int(1 if success else 0)
  lNoReturn = ctypes.c_int(0)
  res = lib.MSHEWQ_TERMINATE(ctypes.byref(lNormalTermination), ctypes.byref(lNoReturn)) # in, in
  return res != 0